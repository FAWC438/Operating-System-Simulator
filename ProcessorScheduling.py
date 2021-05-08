from queue import PriorityQueue

from Memory import allocateMemory
from Process import State


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
        # 同时只有一个running的进程
        if process_cur.state == State.running:
            process_cur.occupied_time += 1
            if process_cur.occupied_time >= process_cur.get_last_time():
                # 进程执行完毕

                # TODO:根据DataType，若不是default类型的话，在这执行相应的File/IO操作

                process_cur.scheduled_info.append((system_clock, 3))
                process_cur.terminate()  # 该方法会将进程变为terminated态
        elif process_cur.state == State.ready:

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
