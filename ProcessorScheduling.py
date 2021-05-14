from queue import PriorityQueue

from IOSystem import asyncIO
from Memory import allocateMemory
from Process import State, DataType, Process


# TODO:明确执行队列和等待队列的表现形式
# TODO:添加swap out/in


def FCFS(process_q: PriorityQueue):
    """
    TODO：进行更新
    先进先出算法
    :param process_q:
    :return:
    """
    t = 0
    process_now = process_q.get()
    while not process_q.empty():
        if t >= process_now.get_start_time():  # 运行当前进程
            process_now.set_start_time(t)
            t += process_now.get_last_time()
            print(process_now)
            if not process_q.empty():
                process_now = process_q.get()
        else:
            t = process_now.get_start_time()


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
        over_flag = True  # 所有进程执行完毕退出循环

        # 开始时间小于系统时间的进程进入process_now_queue执行队列
        for p in process_q:
            if p.state != State.terminated:
                over_flag = False
                # if p.state != State.running:
                #     p.state = State.ready
        if over_flag:
            print('finish')
            break
        process_now_queue = [i for i in process_q if
                             i.get_start_time() <= system_clock
                             and i.state != State.terminated]
        # process_now_queue为执行队列，而process_q对process_now_queue的差集为等待队列
        for p in process_now_queue:
            if p.state != State.running:
                p.state = State.ready

        process_now_queue.sort(key=lambda x: x.priority)
        process_cur = process_now_queue[0]  # 得到优先级最高的进程（优先级数字越低表示优先级越高）
        assert isinstance(process_cur, Process)
        # 同时只有一个running的进程
        if process_cur.state == State.running:
            process_cur.occupied_time += 1
            if process_cur.occupied_time >= process_cur.get_last_time():
                # 进程执行完毕

                if process_cur.get_process_type() == DataType.IO and not process_cur.device_request.is_finish:
                    # 如果进程已经执行完毕，但相应的IO请求还未结束
                    pass  # TODO:swap or wait?

                process_cur.scheduled_info.append((system_clock, 3))
                process_cur.terminate()  # 该方法会将进程变为terminated态
        elif process_cur.state == State.ready:
            if process_cur.occupied_time == 0 and process_cur.get_process_type() == DataType.IO:
                process_cur.IO_expect_return_time = IO_interrupt(process_cur, system_clock)
                # 需要向用户显示异步IO的结果会在什么时候返回
                # 注意，IO中断返回的这个时间是预计时间，由于IO调度，该数字可能会发生很大的变化

            if process_running is not None and process_running != process_cur:
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
