from queue import Queue

from kernal import IOSystem, Memory
import IOSystem
from kernal.FileSystem import Folder
from FileSystem import Folder
from kernal.Memory import freeMemory, allocateMemory
from Memory import freeMemory, allocateMemory
from kernal.Process import Process, State, DataType, scheduling_algorithm, ProcessAlgorithm
from Process import Process, State, DataType, scheduling_algorithm, ProcessAlgorithm


def swapOut(target_process: Process, system_clock: int, swap_q: list):
    """
    进程换出
    请注意，需要在换出过程中释放内存

    :param swap_q: swap队列
    :param target_process: 欲换出的目标进程
    :param system_clock: 系统时钟
    :return:
    """
    target_process.state = State.HangUp
    freeMemory(target_process.page_list)
    target_process.page_all_allocated = False
    target_process.scheduled_info.append((system_clock, 3))

    swap_q.append(target_process)


def swapIn(target_process: Process, system_clock: int, swap_q: list):
    """
    进程换入
    请注意，无需在换入过程中分配内存

    :param swap_q: swap队列
    :param target_process:
    :param system_clock: 系统时钟
    :return:
    """
    target_process.state = State.ready
    target_process.scheduled_info.append((system_clock, 4))
    if target_process in swap_q:
        swap_q.remove(target_process)


def fcfsForBackEnd(process_q: list, system_clock: int, proc_running: Process, proc_cur: Process, memory: list,
                   device_table: list, root: Folder, Disk: list, file_table: list):
    """
    先进先出算法

    :param file_table: 文件表
    :param Disk: 文件系统磁盘
    :param root: 文件目录根节点
    :param device_table: 设备表
    :param memory: 物理内存
    :param proc_cur:当前进程
    :param proc_running:上一时钟周期的进程
    :param process_q:进程队列
    :param system_clock:系统时钟
    :return:返回5个参数  code=1：正常执行完毕2：执行队列没有进程3：所有调度结束;    proc_cur    proc_running    process_now_q   文件系统参数列表
    """

    IOSystem.asyncIO(device_table, root, Disk, file_table)
    over_flag = True

    # 如果所有进程都终止，调度结束
    for p in process_q:
        if p.state != State.terminated:
            over_flag = False
            break

    if over_flag:
        print('finish')  # 这里代表调度结束
        return 3, proc_cur, proc_running, None, [root, Disk, file_table]

    # 当前时间可以处理的进程放入 process_now_queue
    process_now_q = [i for i in process_q if
                     i.get_arrive_time() <= system_clock
                     and i.state != State.terminated]

    if not process_now_q:
        return 2, proc_cur, proc_running, process_now_q, [root, Disk, file_table]

    process_now_q.sort(key=lambda x: x.get_arrive_time())  # 按到达时间进行排序

    # 找 process_cur
    # 先检查是否有 running，有则设为 process_cur
    if proc_running is not None:
        proc_cur = proc_running

    # 没有进程 running，找第一个 ready 执行
    else:
        for p in process_now_q:  # 找到目前能处理的第一个 ready 的进程
            if p.state == State.ready:
                proc_cur = p
                break

    # process_now_queue 全是 terminated？
    assert isinstance(proc_cur, Process)

    # 同时只有一个running的进程
    if proc_cur.state == State.running:

        # 进程执行完毕
        if proc_cur.occupied_time >= proc_cur.get_last_time():
            # if process_cur.get_process_type() == DataType.IO and not process_cur.device_request.is_finish:
            #     # 如果进程已经执行完毕，但相应的IO请求还未结束
            #     pass

            proc_cur.scheduled_info.append((system_clock, 2))
            proc_cur.terminate()  # 该方法会将进程变为terminated态

        proc_cur.occupied_time += 1

    elif proc_cur.state == State.ready:  # 此时可以保证没有进程 running
        if proc_cur.occupied_time == 0 and proc_cur.get_process_type() == DataType.IO:  # 该进程从未发生过且为 IO 类型
            proc_cur.IO_expect_return_time = IO_request(proc_cur, system_clock)
            # 需要向用户显示异步IO的结果会在什么时候返回
            # 注意，IO中断返回的这个时间是预计时间，由于IO调度，该数字可能会发生很大的变化

        # 分配内存
        if not proc_cur.page_all_allocated:
            temp_q = process_q.copy()
            temp_q.remove(proc_cur)
            allocateMemory(proc_cur.page_list, temp_q, memory)
            proc_cur.page_all_allocated = True

        # 启动该进程
        proc_cur.state = State.running
        proc_cur.occupied_time += 1
        proc_cur.scheduled_info.append((system_clock, 0))

    # 当前进程执行完毕
    if proc_cur.state == State.terminated:
        proc_running = None
    else:
        proc_running = proc_cur

    return 1, proc_cur, proc_running, process_now_q, [root, Disk, file_table]
    # sleep(0.5)


def prioritySchedulingSyncForBackEnd(process_q: list, system_clock: int, swap_q: list, proc_running: Process,
                                     proc_cur: Process, memory: list, device_table: list,
                                     root: Folder, Disk: list, file_table: list):
    """
    同步 IO优先级调度

    :param file_table: 文件表
    :param Disk: 文件系统磁盘
    :param root: 文件目录根节点
    :param device_table: 设备表
    :param swap_q: 交换队列
    :param memory: 物理内存
    :param proc_cur:当前进程
    :param proc_running:上一时钟周期的进程
    :param process_q:进程队列
    :param system_clock:系统时钟
    :return:返回5个参数  code=1：正常执行完毕2：执行队列没有进程3：所有调度结束;    proc_cur    proc_running    process_now_q   文件系统参数列表
    """

    root, Disk, file_table = IOSystem.asyncIO(device_table, root, Disk, file_table)

    # 能不能把队列处理的这段代码封装一下，应该每种调度算法都会用到
    over_flag = True  # 所有进程执行完毕退出循环

    # 开始时间小于系统时间的进程进入process_now_queue执行队列
    for p in process_q:
        if p.state != State.terminated:
            over_flag = False
            break
            # if p.state != State.running:
            #     p.state = State.ready
    if over_flag:
        print('finish')  # 这里代表调度结束
        return 3, proc_cur, proc_running, None, [root, Disk, file_table]

    # 当前时间可以处理的进程
    process_now_q = [i for i in process_q if
                     i.get_arrive_time() <= system_clock
                     and i.state != State.terminated]

    if not process_now_q:
        return 2, proc_cur, proc_running, process_now_q, [root, Disk, file_table]

    # IO 执行完毕，发出中断
    for p in process_now_q:
        # assert isinstance(p, Process)
        if p.state == State.waiting and p.device_request.is_finish:
            interruptSignal(p, system_clock)

    process_now_q.sort(key=lambda x: x.priority)

    # 优先级为 0，发出 IO 中断
    if process_now_q[0].priority == 0:
        IO_trigger(proc_cur, process_now_q[0], system_clock)

    '''
    进程swap策略（仅适用于优先级抢占调度）
    如果执行队列（process_now_queue）中的进程大于3个，则留下优先级最高的3个进程，其它进程swap out
    而执行队列中的进程不能处于挂起状态（即不能是被换出的进程，如果被换出的进程需要进入执行队列，则进行换入swap in操作）
    '''
    if len(process_now_q) > 3:
        process_to_swap = process_now_q[3:]
        process_now_q = process_now_q[:3]
        for p in process_to_swap:
            if p not in swap_q:
                swapOut(p, system_clock, swap_q)

    for p in process_now_q:
        if p.state == State.HangUp:
            swapIn(p, system_clock, swap_q)

    # TODO: 3个剩余进程都是waiting的情况
    # 同步IO。找出不是 waiting 的最高优先级进程
    for p in process_now_q:
        if p.state != State.waiting:
            proc_cur = p
            break

    assert isinstance(proc_cur, Process)

    # 同时只有一个 running 的进程
    if proc_cur.state == State.running:

        # 进程执行完毕
        if proc_cur.occupied_time >= proc_cur.get_last_time():
            # 每个IO进程的IO时间规定必须小于该进程时间，

            proc_cur.scheduled_info.append((system_clock, 2))
            proc_cur.terminate()  # 该方法会将进程变为terminated态
        proc_cur.occupied_time += 1
    elif proc_cur.state == State.ready:
        # 进程发出 IO 请求
        if proc_cur.occupied_time == 0 and proc_cur.get_process_type() == DataType.IO \
                and not proc_cur.device_request.is_finish:
            proc_cur.IO_expect_return_time = IO_request(proc_cur, system_clock)
            proc_cur.state = State.waiting
            proc_cur.scheduled_info.append((system_clock, 5))

            # 需要向用户显示异步IO的结果会在什么时候返回
            # 注意，IO中断返回的这个时间是预计时间，由于IO调度，该数字可能会发生很大的变化

        # 有进程在运行，但不是当前进程，需要发生抢占
        if proc_running is not None and proc_running != proc_cur and proc_running.state != State.HangUp \
                and proc_running.state != State.waiting:
            # 若上一个时钟周期是别的进程
            proc_running.state = State.ready
            proc_running.scheduled_info.append((system_clock, 1))

        # 分配内存
        if not proc_cur.page_all_allocated:
            temp_q = process_q.copy()
            temp_q.remove(proc_cur)
            allocateMemory(proc_cur.page_list, temp_q, memory)
            proc_cur.page_all_allocated = True

        if proc_cur.state != State.waiting:
            proc_cur.state = State.running
            proc_cur.scheduled_info.append((system_clock, 0))
            proc_cur.occupied_time += 1
    # elif proc_cur.state == State.waiting:
    #     root, Disk, file_table = IOSystem.asyncIO(device_table, root, Disk, file_table)
    #     proc_cur.occupied_time += 1

    # 当前进程执行完毕
    if proc_cur.state == State.terminated:
        proc_running = None
    else:
        proc_running = proc_cur
    return 1, proc_cur, proc_running, process_now_q, [root, Disk, file_table]
    # sleep(0.5)


def prioritySchedulingAsyncForBackEnd(process_q: list, system_clock: int, swap_q: list,
                                      proc_running: Process,
                                      proc_cur: Process,
                                      memory: list,
                                      device_table: list,
                                      root: Folder, Disk: list, file_table: list):
    """
    异步 IO优先级调度

    :param file_table: 文件表
    :param Disk: 文件系统磁盘
    :param root: 文件目录根节点
    :param swap_q: 交换队列
    :param device_table: 设备表
    :param memory: 物理内存
    :param proc_cur:当前进程
    :param proc_running:上一时钟周期的进程
    :param process_q:进程队列
    :param system_clock:系统时钟
    :return:返回5个参数  code=1：正常执行完毕2：执行队列没有进程3：所有调度结束;    proc_cur    proc_running    process_now_q   文件系统参数列表
    """
    root, Disk, file_table = IOSystem.asyncIO(device_table, root, Disk, file_table)

    # 能不能把队列处理的这段代码封装一下，应该每种调度算法都会用到
    over_flag = True  # 所有进程执行完毕退出循环

    # 开始时间小于系统时间的进程进入process_now_queue执行队列2
    for p in process_q:
        if p.state != State.terminated:
            over_flag = False
            break
            # if p.state != State.running:
            #     p.state = State.ready
    if over_flag:
        print('finish')  # 这里代表调度结束
        return 3, proc_cur, proc_running, None, [root, Disk, file_table]

    # 当前时间可以处理的进程
    process_now_queue = [i for i in process_q if
                         i.get_arrive_time() <= system_clock
                         and i.state != State.terminated]

    if not process_now_queue:
        return 2, proc_cur, proc_running, process_now_queue, [root, Disk, file_table]

    process_now_queue.sort(key=lambda x: x.priority)

    '''
    进程swap策略（仅适用于优先级抢占调度）
    如果执行队列（process_now_queue）中的进程大于3个，则留下优先级最高的3个进程，其它进程swap out
    而执行队列中的进程不能处于挂起状态（即不能是被换出的进程，如果被换出的进程需要进入执行队列，则进行换入swap in操作）
    '''
    if len(process_now_queue) > 3:
        process_to_swap = process_now_queue[3:]
        process_now_queue = process_now_queue[:3]
        for p in process_to_swap:
            if p not in swap_q:
                swapOut(p, system_clock, swap_q)

    for p in process_now_queue:
        if p.state == State.HangUp:
            swapIn(p, system_clock, swap_q)

    # 异步IO。得到优先级最高的进程（优先级数字越低表示优先级越高）
    proc_cur = process_now_queue[0]

    # assert isinstance(proc_cur, Process)

    # 同时只有一个 running 的进程
    if proc_cur.state == State.running:

        # 进程执行完毕
        if proc_cur.occupied_time >= proc_cur.get_last_time():
            # 每个IO进程的IO时间规定必须小于该进程时间，

            proc_cur.scheduled_info.append((system_clock, 2))
            proc_cur.terminate()  # 该方法会将进程变为terminated态

        proc_cur.occupied_time += 1
    elif proc_cur.state == State.ready:
        if proc_cur.occupied_time == 0 and proc_cur.get_process_type() == DataType.IO:  # 该进程从未发生过且为 IO 类型
            proc_cur.IO_expect_return_time = IO_request(proc_cur, system_clock)

        # 有进程在运行，但不是当前进程，需要发生抢占
        if proc_running is not None and proc_running != proc_cur and proc_running.state != State.HangUp:
            # 若上一个时钟周期是别的进程
            proc_running.state = State.ready
            proc_running.scheduled_info.append((system_clock, 1))

        # 分配内存
        if not proc_cur.page_all_allocated:
            temp_q = process_q.copy()
            temp_q.remove(proc_cur)
            allocateMemory(proc_cur.page_list, temp_q, memory)
            proc_cur.page_all_allocated = True
        proc_cur.state = State.running
        proc_cur.occupied_time += 1
        proc_cur.scheduled_info.append((system_clock, 0))

    # 当前进程执行完毕
    if proc_cur.state == State.terminated:
        proc_running = None
    else:
        proc_running = proc_cur
    return 1, proc_cur, proc_running, process_now_queue, [root, Disk, file_table]
    # sleep(0.5)


def roundRobinForBackEnd(process_q: list, process_now_q: list, system_clock: int,
                         proc_running: Process,
                         proc_cur: Process,
                         memory: list,
                         device_table: list,
                         root: Folder, Disk: list, file_table: list, time_slice: int = 2):
    """

    :param process_now_q:
    :param process_q:
    :param system_clock:
    :param proc_running:
    :param proc_cur:
    :param memory:
    :param device_table:
    :param root:
    :param Disk:
    :param file_table:
    :param time_slice:
    :return:
    """

    root, Disk, file_table = IOSystem.asyncIO(device_table, root, Disk, file_table)

    # 如果所有进程都终止，调度结束
    over_flag = True
    # 开始时间小于系统时间的进程进入process_now_queue执行队列
    for p in process_q:
        if p.state != State.terminated:
            over_flag = False
            break
            # if p.state != State.running:
            #     p.state = State.ready
    if over_flag:
        print('finish')  # 这里代表调度结束
        return 3, proc_cur, proc_running, None, [root, Disk, file_table], time_slice

    # 将未处理过的进程加入队列
    for p in process_q:
        if p.get_arrive_time() <= system_clock and p not in process_now_q and p.state != State.terminated:
            process_now_q.append(p)

    if not process_now_q:
        return 2, proc_cur, proc_running, process_now_q, [root, Disk, file_table], time_slice

    # 找第一个需要执行的进程

    if time_slice == 0:  # 时间片轮转结束，进行调度
        process_now_q.remove(proc_cur)
        if proc_cur.occupied_time >= proc_cur.get_last_time() and proc_cur.state != State.terminated:
            # if process_cur.get_process_type() == DataType.IO and not process_cur.device_request.is_finish:
            #     # 如果进程已经执行完毕，但相应的IO请求还未结束
            #     pass

            proc_cur.scheduled_info.append((system_clock, 2))
            proc_cur.terminate()
        elif proc_running is not None:  # 上一个时间片的进程没有执行结束
            # TODO: 时间片中断

            proc_cur.state = State.ready
            proc_cur.scheduled_info.append((system_clock, 1))
            process_now_q.append(proc_cur)

            timer_trigger(proc_cur, system_clock)

    if time_slice <= 0 or proc_running is None:
        # 上一个时间片的进程执行结束了
        tmp_slice = 2
    else:
        tmp_slice = time_slice

    proc_cur = process_now_q[0]

    # # 没有进程 running，找第一个 ready 执行
    # else:
    #     # 找到目前能处理的第一个 ready 的进程
    #     for _ in range(len(process_now_q)):
    #         tmp_p = process_now_q[0]
    #         if tmp_p.state == State.ready:  # 找到
    #             proc_cur = tmp_p
    #             break
    #         process_now_q.append(tmp_p)
    if proc_cur.state == State.running:

        # 进程执行完毕
        if proc_cur.occupied_time >= proc_cur.get_last_time():
            # if process_cur.get_process_type() == DataType.IO and not process_cur.device_request.is_finish:
            #     # 如果进程已经执行完毕，但相应的IO请求还未结束
            #     pass

            proc_cur.scheduled_info.append((system_clock, 2))
            proc_cur.terminate()

        proc_cur.occupied_time += 1

    elif proc_cur.state == State.ready:  # 此时可以保证没有进程 running
        if proc_cur.occupied_time == 0 and proc_cur.get_process_type() == DataType.IO:  # 该进程从未发生过且为 IO 类型
            proc_cur.IO_expect_return_time = IO_request(proc_cur, system_clock)

        # # 有进程在运行，但不是当前进程，需要发生抢占
        # if proc_running is not None and proc_running != proc_cur:
        #     # 若上一个时钟周期是别的进程
        #     proc_running.state = State.ready
        #     proc_running.scheduled_info.append((system_clock, 1))

        # 分配内存
        if not proc_cur.page_all_allocated:
            temp_q = process_q.copy()
            temp_q.remove(proc_cur)
            allocateMemory(proc_cur.page_list, temp_q, memory)
            proc_cur.page_all_allocated = True
        proc_cur.state = State.running
        proc_cur.occupied_time += 1
        proc_cur.scheduled_info.append((system_clock, 0))

    # 当前进程执行完毕
    if proc_cur.state == State.terminated:
        proc_running = None
    else:
        proc_running = proc_cur

    tmp_slice -= 1
    return 1, proc_cur, proc_running, process_now_q, [root, Disk, file_table], tmp_slice


def IO_request(target_process: Process, system_clock: int):
    """
    发送IO请求

    :param target_process:发送请求的源进程
    :param system_clock:系统时钟
    :return:IO请求所预计的返回时间
    """
    target_queue = target_process.device_request.target_device.request_queue
    t = 0  # IO请求队列中前面的请求需要花费的时间
    if target_queue:
        for r in target_queue:
            t += r.IO_operation_time
    target_queue.append(target_process.device_request)
    IO_expect_return_time = system_clock + t + target_process.device_request.IO_operation_time
    return IO_expect_return_time  # TODO: 时间没法精确计算


# 中断处理程序
def mouse_interrupt():
    print('鼠标处理...')


def keyboard_interrupt():
    print('键盘处理...')


def timer_interrupt():
    print('时间片处理...')


def get_interrupt_vector(i_type: str = None):
    interrupt_vector = {'mouse': mouse_interrupt,
                        'keyboard': keyboard_interrupt,
                        'timer': timer_interrupt,
                        'page': Memory.pageFault}
    interrupt_vector[i_type]()


def timer_trigger(targetProcess: Process, system_clock: int, EI: bool = False):
    """
    时间片中断

    :param targetProcess:
    :param system_clock:
    :param EI:
    :return:
    """
    # 保存现场
    targetProcess.recover['system_clock'] = system_clock
    targetProcess.recover['occupied_time'] = targetProcess.occupied_time
    targetProcess.recover['state'] = targetProcess.state

    get_interrupt_vector('timer')


def IO_trigger(proc_cur: Process, proc_io: Process, system_clock: int, EI: bool = False):
    """
    IO中断

    :param proc_cur:
    :param proc_io:
    :param system_clock:
    :param EI:
    :return:
    """
    # 保存现场
    proc_cur.recover['system_clock'] = system_clock
    proc_cur.recover['occupied_time'] = proc_cur.occupied_time
    proc_cur.recover['state'] = proc_cur.state

    # 存放中断服务程序的首地址
    # 查中断向量表，执行中断程序
    get_interrupt_vector(proc_io.device_request.target_device.name)

    # 允许嵌套中断位
    # is_interrupt = False


def interruptSignal(process: Process, system_clock: int, is_interrupt: bool = False):
    """
    IO中断

    :param process:引起中断的进程
    :param system_clock:系统时钟
    :param is_interrupt: 嵌套中断位
    :return:
    """
    # 保存现场
    process.recover['system_clock'] = system_clock
    process.recover['occupied_time'] = process.occupied_time
    process.recover['state'] = process.state

    # 进程状态变换
    process.state = State.ready
    process.scheduled_info.append((system_clock, 6))

    # 允许嵌套中断位
    # is_interrupt = False


def getMsg(process_q, swap_queue, proc_now):
    msgRunning = []
    msgWaiting = []
    msgUncreated = []
    msgTerminated = []
    msgSwapOut = []
    for proc in process_q:
        if proc.state == State.running:
            msgRunning.append(proc.get_process_id())
        elif proc.state == State.waiting:
            msgWaiting.append(proc.get_process_id())
        elif proc.state == State.terminated:
            msgTerminated.append(proc.get_process_id())
        elif not (proc in proc_now):
            msgUncreated.append(proc.get_process_id())
    for proc in swap_queue:
        msgSwapOut.append(proc.get_process_id())

    return msgRunning, msgWaiting, msgUncreated, msgTerminated, msgSwapOut


def createQueue(clock: int, swap_queue, proc_running, proc_cur, proc_now, memory, device_table, fileAttr):
    process_q = [Process(DataType.Default, 0, 5, priority=10), Process(DataType.Default, 1, 3, priority=8),
                 Process(DataType.Default, 3, 6, priority=12), Process(DataType.Default, 2, 11, priority=2),
                 Process(DataType.Default, 5, 2, priority=6)]
    process_q, swap_queue, proc_running, proc_cur, proc_now, memory, device_table, fileAttr = \
        DoAlgorithm(clock, process_q, swap_queue, proc_running, proc_cur, proc_now, memory, device_table, fileAttr)
    return process_q, swap_queue, proc_running, proc_cur, proc_now, memory, device_table, fileAttr


def DoAlgorithm(clock: int, process_q, swap_queue, proc_running, proc_cur, proc_now, memory, device_table, fileAttr):
    if scheduling_algorithm == ProcessAlgorithm.Priority:
        # 通过PyCharm的调试可查看输出结果
        # system_clock = prioritySchedulingSync(process_queue, system_clock)
        state, proc_cur, proc_running, proc_now, fileAttr = prioritySchedulingAsyncForBackEnd(process_q,
                                                                                              clock,
                                                                                              swap_queue,
                                                                                              proc_running,
                                                                                              proc_cur,
                                                                                              memory,
                                                                                              device_table,
                                                                                              fileAttr[0],
                                                                                              fileAttr[1],
                                                                                              fileAttr[2])
    return process_q, swap_queue, proc_running, proc_cur, proc_now, memory, device_table, fileAttr
    # system_clock = fcfs(process_queue, system_clock)
    # system_clock = round_robin(process_queue, system_clock)


def getProcessInfo(processId: str, process_q):
    message = {}
    for proc in process_q:
        if processId == proc.get_process_id():
            page_list = []
            if proc.page_list is not None:
                for p in proc.page_list:
                    page_list.append(p.page_id)
            message.update({"processId": processId,
                            "processType": str(proc.get_process_type()),
                            "processArriveTime": proc.get_arrive_time(),
                            "processDuration": proc.get_last_time(),
                            "processState": str(proc.state),
                            "processPriority": proc.priority,
                            "processSchedule": proc.scheduled_info,
                            "processPageNumber": proc.get_page_num(),
                            "processPagesId": page_list,
                            "deviceRequest": proc.device_request,
                            "deviceRequestBit": proc.device_request_is_finish,
                            "processScene": proc.recover})
            return message
    message.update({"message": "Failed! Process Not Exists!"})
    return message
