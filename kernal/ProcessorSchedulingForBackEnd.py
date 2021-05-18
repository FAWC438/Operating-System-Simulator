from queue import Queue

from IOSystem import asyncIO
from Memory import allocateMemory, freeMemory
from Process import State, DataType, Process

swap_queue = []  # 进程swap空间（队列）
process_now_queue = []  # 进程执行队列
process_running = None  # 上一个周期执行的进程
process_cur = None  # 正在执行的进程
is_interrupt = True  # 嵌套中断


def swapOut(target_process: Process, system_clock: int):
    """
    进程换出
    请注意，需要在换出过程中释放内存

    :param target_process: 欲换出的目标进程
    :param system_clock: 系统时钟
    :return:
    """
    global swap_queue
    target_process.state = State.HangUp
    freeMemory(target_process.page_list)
    target_process.page_all_allocated = False
    target_process.scheduled_info.append((system_clock, 3))

    swap_queue.append(target_process)


def swapIn(target_process: Process, system_clock: int):
    """
    进程换入
    请注意，无需在换入过程中分配内存

    :param target_process:
    :param system_clock: 系统时钟
    :return:
    """
    global swap_queue
    target_process.state = State.ready
    target_process.scheduled_info.append((system_clock, 4))
    if target_process in swap_queue:
        swap_queue.remove(target_process)


def fcfsForBackEnd(process_q: list, system_clock: int):
    """
    先进先出算法
    :param process_q:进程队列
    :param system_clock:系统时钟
    :return:1：正常执行完毕，2：执行队列没有进程，3：所有调度结束
    """
    global process_now_queue, process_running, process_cur

    asyncIO()
    over_flag = True

    # 如果所有进程都终止，调度结束
    for p in process_q:
        if p.state != State.terminated:
            over_flag = False

    if over_flag:
        print('finish')  # 这里代表调度结束
        return 3

    # 当前时间可以处理的进程放入 process_now_queue
    process_now_queue = [i for i in process_q if
                         i.get_arrive_time() <= system_clock
                         and i.state != State.terminated]

    process_now_queue.sort(key=lambda x: x.get_arrive_time())  # 按到达时间进行排序

    # 找 process_cur
    # 先检查是否有 running，有则设为 process_cur
    if process_running is not None:
        process_cur = process_running

    # 没有进程 running，找第一个 ready 执行
    else:
        for p in process_now_queue:  # 找到目前能处理的第一个 ready 的进程
            if p.state == State.ready:
                process_cur = p
                process_running = True  # 有进程正在执行，不能抢占
                break

    # process_now_queue 全是 terminated？
    assert isinstance(process_cur, Process)

    # 同时只有一个running的进程
    if process_cur.state == State.running:
        process_cur.occupied_time += 1

        # 进程执行完毕
        if process_cur.occupied_time >= process_cur.get_last_time():
            # if process_cur.get_process_type() == DataType.IO and not process_cur.device_request.is_finish:
            #     # 如果进程已经执行完毕，但相应的IO请求还未结束
            #     pass

            process_cur.scheduled_info.append((system_clock, 2))
            process_cur.terminate()  # 该方法会将进程变为terminated态

    elif process_cur.state == State.ready:  # 此时可以保证没有进程 running
        if process_cur.occupied_time == 0 and process_cur.get_process_type() == DataType.IO:  # 该进程从未发生过且为 IO 类型
            process_cur.IO_expect_return_time = IO_request(process_cur, system_clock)
            # 需要向用户显示异步IO的结果会在什么时候返回
            # 注意，IO中断返回的这个时间是预计时间，由于IO调度，该数字可能会发生很大的变化

        # 分配内存
        if not process_cur.page_all_allocated:
            temp_q = process_q.copy()
            temp_q.remove(process_cur)
            allocateMemory(process_cur.page_list, temp_q)
            process_cur.page_all_allocated = True

        # 启动该进程
        process_cur.state = State.running
        process_cur.occupied_time += 1
        process_cur.scheduled_info.append((system_clock, 0))

    # 当前进程执行完毕
    if process_cur.state == State.terminated:
        process_running = None
    else:
        process_running = process_cur

    return 1
    # sleep(0.5)


def prioritySchedulingSyncForBackEnd(process_q: list, system_clock: int):
    """
    同步 IO优先级调度
    :param process_q:进程队列
    :param system_clock:系统时钟
    :return:1：正常执行完毕，2：执行队列没有进程，3：所有调度结束
    """
    global swap_queue, process_now_queue, process_running, process_cur

    # 能不能把队列处理的这段代码封装一下，应该每种调度算法都会用到
    over_flag = True  # 所有进程执行完毕退出循环

    # 开始时间小于系统时间的进程进入process_now_queue执行队列2
    for p in process_q:
        if p.state != State.terminated:
            over_flag = False
            # if p.state != State.running:
            #     p.state = State.ready
    if over_flag:
        print('finish')  # 这里代表调度结束
        return 3

    # 当前时间可以处理的进程
    process_now_queue = [i for i in process_q if
                         i.get_arrive_time() <= system_clock
                         and i.state != State.terminated]

    if not process_now_queue:
        system_clock += 1
        return 2

    # IO 执行完毕，发出中断
    for p in process_now_queue:
        if p.state == State.waiting and system_clock >= p.IO_expect_return_time:
            IO_interrupt(p, system_clock)

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
            if p not in swap_queue:
                swapOut(p, system_clock)

    for p in process_now_queue:
        if p.state == State.HangUp:
            swapIn(p, system_clock)

    # 同步IO。找出不是 waiting 的最高优先级进程
    for p in process_now_queue:
        if p.state != State.waiting:
            process_cur = p
            break

    assert isinstance(process_cur, Process)

    # 同时只有一个 running 的进程
    if process_cur.state == State.running:
        process_cur.occupied_time += 1

        # 进程执行完毕
        if process_cur.occupied_time >= process_cur.get_last_time():
            # 每个IO进程的IO时间规定必须小于该进程时间，

            process_cur.scheduled_info.append((system_clock, 2))
            process_cur.terminate()  # 该方法会将进程变为terminated态
    elif process_cur.state == State.ready:
        # 进程发出 IO 请求
        if process_cur.occupied_time == 0 and process_cur.get_process_type() == DataType.IO:
            process_cur.IO_expect_return_time = IO_request(process_cur, system_clock)
            process_cur.state = State.waiting

            # 需要向用户显示异步IO的结果会在什么时候返回
            # 注意，IO中断返回的这个时间是预计时间，由于IO调度，该数字可能会发生很大的变化

        # 有进程在运行，但不是当前进程，需要发生抢占
        if process_running is not None and process_running != process_cur and process_running.state != State.HangUp:
            # 若上一个时钟周期是别的进程
            process_running.state = State.ready
            process_running.scheduled_info.append((system_clock, 1))

        # 分配内存
        if not process_cur.page_all_allocated:
            temp_q = process_q.copy()
            temp_q.remove(process_cur)
            allocateMemory(process_cur.page_list, temp_q)
            process_cur.page_all_allocated = True
        process_cur.state = State.running
        process_cur.occupied_time += 1
        process_cur.scheduled_info.append((system_clock, 0))

    # 当前进程执行完毕
    if process_cur.state == State.terminated:
        process_running = None
    else:
        process_running = process_cur
    return 1
    # sleep(0.5)


def prioritySchedulingAsyncForBackEnd(process_q: list, system_clock: int):
    """
    异步 IO优先级调度
    :param process_q:进程队列
    :param system_clock:系统时钟
    :return:1：正常执行完毕，2：执行队列没有进程，3：所有调度结束
    """
    global swap_queue, process_now_queue, process_running, process_cur
    asyncIO()

    # 能不能把队列处理的这段代码封装一下，应该每种调度算法都会用到
    over_flag = True  # 所有进程执行完毕退出循环

    # 开始时间小于系统时间的进程进入process_now_queue执行队列2
    for p in process_q:
        if p.state != State.terminated:
            over_flag = False
            # if p.state != State.running:
            #     p.state = State.ready
    if over_flag:
        print('finish')  # 这里代表调度结束
        return 3

    # 当前时间可以处理的进程
    process_now_queue = [i for i in process_q if
                         i.get_arrive_time() <= system_clock
                         and i.state != State.terminated]

    if not process_now_queue:
        system_clock += 1
        return 2

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
            if p not in swap_queue:
                swapOut(p, system_clock)

    for p in process_now_queue:
        if p.state == State.HangUp:
            swapIn(p, system_clock)

    # 异步IO。得到优先级最高的进程（优先级数字越低表示优先级越高）
    process_cur = process_now_queue[0]

    assert isinstance(process_cur, Process)

    # 同时只有一个 running 的进程
    if process_cur.state == State.running:
        process_cur.occupied_time += 1

        # 进程执行完毕
        if process_cur.occupied_time >= process_cur.get_last_time():
            # 每个IO进程的IO时间规定必须小于该进程时间，

            process_cur.scheduled_info.append((system_clock, 2))
            process_cur.terminate()  # 该方法会将进程变为terminated态
    elif process_cur.state == State.ready:
        if process_cur.occupied_time == 0 and process_cur.get_process_type() == DataType.IO:  # 该进程从未发生过且为 IO 类型
            process_cur.IO_expect_return_time = IO_request(process_cur, system_clock)
            # 需要向用户显示异步IO的结果会在什么时候返回
            # 注意，IO中断返回的这个时间是预计时间，由于IO调度，该数字可能会发生很大的变化

        # 有进程在运行，但不是当前进程，需要发生抢占
        if process_running is not None and process_running != process_cur and process_running.state != State.HangUp:
            # 若上一个时钟周期是别的进程
            process_running.state = State.ready
            process_running.scheduled_info.append((system_clock, 1))

        # 分配内存
        if not process_cur.page_all_allocated:
            temp_q = process_q.copy()
            temp_q.remove(process_cur)
            allocateMemory(process_cur.page_list, temp_q)
            process_cur.page_all_allocated = True
        process_cur.state = State.running
        process_cur.occupied_time += 1
        process_cur.scheduled_info.append((system_clock, 0))

    # 当前进程执行完毕
    if process_cur.state == State.terminated:
        process_running = None
    else:
        process_running = process_cur
    return 1
    # sleep(0.5)


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


def IO_interrupt(process: Process, system_clock: int):
    # 保存现场
    process.recover['system_clock'] = system_clock
    process.recover['occupied_time'] = process.occupied_time
    process.recover['state'] = process.state

    # 进程状态变换
    process.state = State.ready

    # 允许嵌套中断位
    # is_interrupt = False
