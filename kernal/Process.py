from enum import Enum

import Tool
from FileSystem import UserFile, FileOperation
from IOSystem import Device, DeviceRequest
from PageAndFrame import Page

# TODO:进程间同步如何实现？

process_queue = []


class State(Enum):
    ready = 0
    running = 1
    waiting = 2
    terminated = 3
    HangUp = 4


class DataType(Enum):
    """
    枚举类型
    """
    Default = 0
    IO = 1


class ProcessAlgorithm(Enum):
    """
    枚举类型，用于指示各种算法的标志数
    """
    PrioritySync = 0
    PriorityAsync = 1
    FCFS = 2
    RR = 3


scheduling_algorithm = ProcessAlgorithm.FCFS  # 使用的进程调度算法


class Process:

    def __init__(self,
                 process_type: DataType,
                 arrive_time,
                 last_time,
                 IO_operation_time: int = -1,
                 target_device: Device = None,
                 request_content: str = None,
                 target_file: UserFile = None,
                 file_operation: FileOperation = None,
                 priority=0,
                 page_num=3,
                 parent_process_id=-1,
                 child_process_id=-1, ):
        """
        Process的构造函数展示了进程的PCB，该构造函数用于创建进程
        :param process_type: 进程类型，私有的
        :param arrive_time: 进程开始时间，私有的
        :param last_time: 进程持续时间，私有的
        :param IO_operation_time: 仅对IO操作进程有效。IO操作需要的时间，该值必须小于occupied_time
        :param target_device: 仅对IO操作进程有效。所请求的设备
        :param request_content: 仅对IO操作进程有效。IO请求内容（数据）
        :param target_file: 仅对IO磁盘操作、文件操作进程有效。目标文件
        :param file_operation: 仅对IO磁盘操作、文件操作进程有效。文件操作
        :param priority: 进程优先级，数字越低优先级越高，0为系统级进程
        :param page_num: 进程所需的页数，私有的
        :param parent_process_id: 父进程id
        :param child_process_id: 子进程id
        """
        self.__process_type = process_type
        self.__process_id = Tool.uniqueNum()
        self.__arrive_time = arrive_time
        self.__last_time = last_time
        self.occupied_time = 0  # 已经使用的CPU时间，若该时间和last_time相等说明该进程已经执行完毕
        self.scheduled_info = []  # 一个二阶列表，每次进程被调度，就往该列表添加调度的时间
        # （一个二元组，第一个值时间戳，第二个是int，0为被调度，1为被暂停调度，2为执行完毕，3为换出swap out，4为换入swap in，5为阻塞，6为停止阻塞），以便快照计算出CPU使用率等指标
        self.state = State.ready  # 进程状态，在使用时注意先变为ready
        self.__page_num = page_num
        self.page_all_allocated = False  # 判断页是否已经分配
        # 请注意！存在进程中部分页已分配，部分未分配的情况，该情况下该字段也为False
        self.page_list = [Page(self.__process_id, self.__process_type) for _ in range(page_num)]  # 进程包含的页

        self.device_request = None  # 进程包含的IO请求
        self.device_request_is_finish = False  # 用于异步IO，指示IO请求是否完成
        self.IO_expect_return_time = -1  # 异步IO返回结果的绝对时间（一个预测值，是设备请求结束时的系统时间）

        if process_type == DataType.IO:
            # 创建IO请求。在进程创建后，将该请求放入对应设备请求队列
            self.device_request = DeviceRequest(self, IO_operation_time, target_device, request_content, target_file,
                                                file_operation)

        self.priority = priority  # 仅在优先级调度有用
        self.parent_process_id = parent_process_id
        self.child_process_id = child_process_id
        self.recover = {'system_clock': None, 'occupied_time': None, 'state': None}  # 保存现场

    # def __lt__(self, other):  # operator <，用于FCFS
    #     return self.__arrive_time < other.__arrive_time

    def __str__(self):
        string = "进程ID：{}".format(self.__process_id) + '\n' + \
                 "进程优先级：{}".format(self.priority) + '\n' + \
                 "进程起始时间：{}".format(self.__arrive_time) + '\n' + \
                 "进程持续时间：{}".format(self.__last_time) + '\n'
        return string

    def get_process_type(self):
        return self.__process_type

    def get_process_id(self):
        return self.__process_id

    def get_arrive_time(self):
        return self.__arrive_time

    def get_last_time(self):
        return self.__last_time

    def set_arrive_time(self, arrive_time):
        self.__arrive_time = arrive_time

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
        self.page_all_allocated = False
        for p in self.page_list:
            if p.mapping_frame is not None:
                p.mapping_frame.is_used = False
                p.mapping_frame.mapping_page = None
        self.page_list = None
        # IO系统为异步的，无需在进程部分对其资源进行释放
        return 1


if __name__ == "__main__":
    pass
