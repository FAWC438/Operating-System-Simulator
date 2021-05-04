from enum import Enum
from queue import PriorityQueue
from time import sleep

import Tool
from Memory import allocateMemory
from PageAndFrame import Page

process_queue = []


class State(Enum):
    ready = 0
    running = 1
    waiting = 2
    terminated = 3
    # TODO 添加swap in/out：进程为IO调度时，执行过程中需要暂停进程执行IO


class DataType(Enum):
    """
    枚举类型
    """
    Default = 0
    File = 1
    IO = 2


class ProcessAlgorithm(Enum):
    """
    枚举类型，用于指示各种算法的标志数
    """
    Default = 0
    FCFS = 1
    Priority = 2
    RR = 3
    # TODO 添加更多算法枚举


scheduling_algorithm = ProcessAlgorithm.Priority  # 使用的进程调度算法


class Process:

    def __init__(self, process_type: DataType, start_time, last_time, priority=0,
                 page_num=3,
                 parent_process_id=-1,
                 child_process_id=-1):
        """
        Process的构造函数展示了进程的PCB，该构造函数用于创建进程
        :param process_type: 进程类型，私有的
        :param start_time: 进程开始时间，私有的
        :param last_time: 进程持续时间，私有的
        :param priority: 进程优先级，数字越低优先级越高，0为系统级进程
        :param page_num: 进程所需的页数，私有的
        :param parent_process_id: 父进程id
        :param child_process_id: 子进程id
        """
        self.__process_type = process_type
        self.__process_id = Tool.uniqueNum()
        self.__start_time = start_time
        self.__last_time = last_time
        self.occupied_time = 0  # 已经使用的CPU时间，若该时间和last_time相等说明该进程已经执行完毕
        self.scheduled_time = []  # 一个二阶列表，每次进程被调度，就往该列表添加调度的时间
        # （一个二元组，第一个值时间戳，第二个是int，0为被调度，1为被暂停调度，2为执行完毕），以便快照计算出CPU使用率等指标
        self.state = State.waiting  # 进程状态，在使用时注意先变为ready
        self.__page_num = page_num
        self.page_allocated = False  # 判断页是否已经分配
        self.page_list = [Page(self.__process_id, self.__process_type) for _ in range(page_num)]  # 进程包含的页
        self.file = None  # TODO 进程所占用的文件
        self.IO_device = None  # TODO 进程所占用的IO设备
        self.priority = priority  # 仅在优先级调度有用
        self.parent_process_id = parent_process_id
        self.child_process_id = child_process_id
        self.recover = None  # TODO 保护CPU现场，此处保存CPU状态

    def __lt__(self, other):  # operator <，用于FCFS
        return self.__start_time < other.__start_time

    def __str__(self):
        string = "进程ID：{}".format(self.__process_id) + '\n' + \
                 "进程优先级：{}".format(self.priority) + '\n' + \
                 "进程起始时间：{}".format(self.__start_time) + '\n' + \
                 "进程持续时间：{}".format(self.__last_time) + '\n' + \
                 "进程结束时间：{}".format(self.__start_time + self.__last_time) + '\n'
        return string

    def get_process_id(self):
        return self.__process_id

    def get_start_time(self):
        return self.__start_time

    def get_last_time(self):
        return self.__last_time

    def set_start_time(self, start_time):
        self.__start_time = start_time

    def terminate(self):
        """
        进程的销毁
        :return: -1为销毁异常，1为正常销毁
        """
        self.state = State.terminated
        if self.__last_time < self.occupied_time:
            print("进程占用过多资源")  # TODO 异常处理
            return -1
        elif self.__last_time > self.occupied_time:
            print("进程未执行完毕便销毁")  # TODO 异常处理
            return -1
        self.page_allocated = False
        for p in self.page_list:
            p.mapping_frame.is_used = False
            p.mapping_frame.mapping_page = None
        self.page_list = None
        self.file = None  # TODO 释放文件
        self.IO_device = None  # TODO 释放IO设备
        return 1


def block(self):
    """
    阻塞进程
    :return:
    """
    self.state = State.waiting


def turnReady(self):
    """
    将进程转为就绪态，在new、running和waiting的时候可用
    :return:
    """
    self.state = State.ready


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
    进程优先级队列
    """
    while system_clock < 300:
        over_flag = True  # 所有进程执行完毕退出循环
        for p in process_q:
            if p.state != State.terminated and p.state != State.running:
                over_flag = False
                p.state = State.waiting
        if over_flag:
            break
        process_now_queue = [i for i in process_q if
                             i.get_start_time() <= system_clock
                             and i.state != State.terminated]
        for p in process_now_queue:
            if p.state != State.running:
                p.state = State.ready
                if not p.page_allocated:
                    temp_q = process_now_queue.copy()
                    temp_q.remove(p)
                    allocateMemory(p.page_list, temp_q)
                    p.page_allocated = True
        # 开始时间小于系统时间的设为ready，否则为waiting
        # TODO:process_now_queue的进程是ready状态，需要分配内存
        process_now_queue.sort(key=lambda x: x.priorityScheduling)
        process_cur = process_now_queue[0]  # 得到优先级最高的进程（优先级数字越低表示优先级越高）
        # 同时只有一个running的进程
        if process_cur.state == State.running:
            process_cur.occupied_time += 1
            if process_cur.occupied_time >= process_cur.get_last_time():
                process_cur.scheduled_time.append((system_clock, 3))
                process_cur.terminate()
        elif process_cur.state == State.ready:
            process_cur.state = State.running
            process_cur.occupied_time += 1
            process_cur.scheduled_time.append((system_clock, 0))

            if process_running is not None:
                process_running.state = State.ready
                process_running.scheduled_time.append((system_clock, 1))

        if process_cur.state == State.terminated:
            process_running = None
        else:
            process_running = process_cur
        system_clock += 1
        sleep(0.5)
    return system_clock


if __name__ == "__main__":
    pass
