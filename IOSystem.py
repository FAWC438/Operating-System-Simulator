import math
from enum import Enum

import Tool
from FileSystem import UserFile


# TODO:如何使用设备缓冲？
# TODO:如何通过IO中断来使用设备？


class FileOperation(Enum):
    Read = 0
    Write = 1
    Create = 2
    Rename = 3
    Delete = 4
    Redirect = 5


class Device:
    def __init__(self, device_name: str, transfer_rate: int, is_busy: bool, request_queue=None):
        """
        IO设备对象

        :param device_name:设备名称
        :param transfer_rate:设备传输速率
        :param is_busy:设备是否忙
        :param request_queue:请求队列
        """
        if request_queue is None:
            request_queue = []
        self.id = Tool.uniqueNum()
        self.name = device_name
        self.transfer_rate = transfer_rate
        self.is_busy = is_busy
        self.request_queue = request_queue
        self.buffer = 2 ** math.ceil(math.log10(transfer_rate))  # 设备缓冲的大小为2^(log10(设备速率))，即设备速率越大需要的缓冲越多


class DeviceRequest:
    def __init__(self, target_device: Device, request_content: str, target_file: UserFile = None,
                 file_operation: FileOperation = None):
        """
        设备请求对象

        :param target_device:所请求的设备
        :param request_content:请求内容（数据）
        :param target_file:目标文件（仅磁盘请求）
        :param file_operation:文件操作（仅磁盘请求）
        """
        self.id = Tool.uniqueNum()
        self.target_device = target_device
        self.request_content = request_content
        # 以下属性仅磁盘使用
        self.target_file = target_file
        self.file_operation = file_operation


Disk = Device('Disk', 8000000, False)
Printer = Device('Printer', 150000, False)
Mouse = Device('Mouse', 15, False)
KeyBoard = Device('KeyBoard', 10, False)
device_table = [Disk, Printer, Mouse, KeyBoard]


def IODiskScheduling(request_queue: list):
    """
    磁盘IO调度
    核心思想是把同一个文件的操作进行集中处理，省去磁盘多次寻道等冗余操作

    :param request_queue:原先的请求队列
    :return:调度后的请求队列
    """
    target_files = []
    file_request_dic = {}
    for request in request_queue:
        if request.target_file not in target_files:
            target_files.append(request.target_file)
            file_request_dic[request.target_file] = [request]
        else:
            file_request_dic[request.target_file].append(request)

    scheduled_request_queue = []
    for i in file_request_dic.values():
        scheduled_request_queue += i
    return scheduled_request_queue


def initIOSystem():
    pass
