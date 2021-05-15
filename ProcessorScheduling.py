from queue import PriorityQueue

from IOSystem import asyncIO
from Memory import allocateMemory
from Process import State, DataType, Process


# TODO:明确执行队列和等待队列的表现形式
# TODO:添加swap out/in



def fcfs(process_q: list, system_clock: int):
    """
    TODO：进行更新
    先进先出算法
    :param process_q:进程队列
    :param system_clock:系统时钟
    :return:系统时钟（调度结束后）
    """
    process_running = None

    while system_clock < 300:
        asyncIO()
        over_flag = True

        # 如果所有进程都终止，调度结束
        for p in process_q:
            if p.state != State.terminated:
                over_flag = False

        if over_flag:
            print('finish')
            break

        # 当前时间可以处理的进程放入 process_now_queue
        process_now_queue = [i for i in process_q if
                             i.get_arrive_time() <= system_clock
                             and i.state != State.terminated]

        # 这段代码有什么用？
        for p in process_now_queue:
            if p.state != State.running: # 这里会把 waiting 改为 ready
                p.state = State.ready

        process_now_queue.sort(key=lambda x: x.get_arrive_time()) # 按到达时间进行排序
        
        # 找 process_cur
        # 先检查是否有 running，有则设为 process_cur
        if process_running:
            process_cur = process_running
        
        # 没有进程 running，找第一个 ready 执行
        else:
            for p in process_now_queue: # 找到目前能处理的第一个 ready 的进程
                if p.state == State.ready:
                    process_cur = p
                    process_running = True # 有进程正在执行，不能抢占
                    break

        # process_now_queue 全是 terminated？
        assert isinstance(process_cur, Process)

        # 同时只有一个running的进程
        if process_cur.state == State.running:
            process_cur.occupied_time += 1
            
            # 进程执行完毕
            if process_cur.occupied_time >= process_cur.get_last_time():
                if process_cur.get_process_type() == DataType.IO and not process_cur.device_request.is_finish:
                    # 如果进程已经执行完毕，但相应的IO请求还未结束
                    pass  # TODO:swap or wait?

                process_cur.scheduled_info.append((system_clock, 2))
                process_cur.terminate()  # 该方法会将进程变为terminated态

        elif process_cur.state == State.ready: # 此时可以保证没有进程 running
            if process_cur.occupied_time == 0 and process_cur.get_process_type() == DataType.IO: # 该进程从未发生过且为 IO 类型
                process_cur.IO_expect_return_time = IO_interrupt(process_cur, system_clock)
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

        # TODO:优先级最高的进程为 waiting 状态
        else:
            pass
        
        # 当前进程执行完毕
        if process_cur.state == State.terminated:
            process_running = None
        else:
            process_running = process_cur

        system_clock += 1
        # sleep(0.5)
    return system_clock

def priorityScheduling(process_q: list, system_clock: int):
    """
    优先级调度
    :param process_q:进程队列
    :param system_clock:系统时钟
    :return:系统时钟（调度结束后）
    """
    process_running = None
    """
    进程优先级队列（抢占式）
    """
    while system_clock < 300:
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
            print('finish')
            break

        # 当前时间可以处理的进程
        process_now_queue = [i for i in process_q if
                             i.get_arrive_time() <= system_clock
                             and i.state != State.terminated]

        # 这段代码有什么用？
        for p in process_now_queue:
            if p.state != State.running: # 这里会把 waiting 改为 ready
                p.state = State.ready

        process_now_queue.sort(key=lambda x: x.priority)
        # 优先级最高的进程可能是 waiting 状态
        process_cur = process_now_queue[0]  # 得到优先级最高的进程（优先级数字越低表示优先级越高）

        # TODO:如果此时队列中进程为空，应该让时钟继续走，而不是 assert
        assert isinstance(process_cur, Process)
        
        # 同时只有一个 running 的进程
        if process_cur.state == State.running:
            process_cur.occupied_time += 1
            
            # 进程执行完毕
            if process_cur.occupied_time >= process_cur.get_last_time():
                if process_cur.get_process_type() == DataType.IO and not process_cur.device_request.is_finish:
                    # 如果进程已经执行完毕，但相应的IO请求还未结束
                    pass  # TODO:swap or wait?

                process_cur.scheduled_info.append((system_clock, 2))
                process_cur.terminate()  # 该方法会将进程变为terminated态
        elif process_cur.state == State.ready:
            if process_cur.occupied_time == 0 and process_cur.get_process_type() == DataType.IO: # 该进程从未发生过且为 IO 类型
                process_cur.IO_expect_return_time = IO_interrupt(process_cur, system_clock)
                # 需要向用户显示异步IO的结果会在什么时候返回
                # 注意，IO中断返回的这个时间是预计时间，由于IO调度，该数字可能会发生很大的变化
            
            # 应该是先分配内存再发生抢占？
            # 有进程在运行，但不是当前进程，需要发生抢占
            if process_running is not None and process_running != process_cur:
                # 若上一个时钟周期是别的进程
                process_running.state = State.ready
                process_running.scheduled_info.append((system_clock, 1))

            # 分配内存
            # TODO: 如果内存不够怎么办？
            if not process_cur.page_all_allocated:
                temp_q = process_q.copy()
                temp_q.remove(process_cur)
                allocateMemory(process_cur.page_list, temp_q)
                process_cur.page_all_allocated = True
            process_cur.state = State.running
            process_cur.occupied_time += 1
            process_cur.scheduled_info.append((system_clock, 0))

        # TODO:优先级最高的进程为 waiting 状态
        else:
            pass
        
        # 当前进程执行完毕
        if process_cur.state == State.terminated:
            process_running = None
        else:
            process_running = process_cur
        system_clock += 1
        # sleep(0.5)
    return system_clock


def IO_interrupt(target_process: Process, system_clock: int):
    target_queue = target_process.device_request.target_device.request_queue
    t = 0  # IO请求队列中前面的请求需要花费的时间
    if target_queue:
        for r in target_queue:
            t += r.IO_operation_time
    target_queue.append(target_process.device_request)
    IO_expect_return_time = system_clock + t + target_process.device_request.IO_operation_time
    return IO_expect_return_time
