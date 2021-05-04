from enum import Enum

import Tool


class DataType(Enum):
    """
    枚举类型
    """
    Default = 0
    File = 1
    IO = 2


class PageAlgorithm(Enum):
    """
    枚举类型，用于指示各种算法的标志数
    """
    Default = 0
    LRU = 1
    RANG = 2
    FIFO = 3
    LFU = 4
    OPT = 5
    # TODO 添加更多算法枚举


all_page = []
allocation_algorithm = PageAlgorithm.Default  # 使用的页调度算法


class Page:

    def __init__(self, pcb_id: int, mem_type: DataType, mapping_frame=None):
        """
        Page 的构造函数展示了页结构，构造函数用于初始化页
        :param mapping_frame: 该页所对应的帧
        :param mem_type: 存储数据类型（进程pcb，文件fcb，io标识符）
        """

        self.page_id = Tool.uniqueNum()
        self.pcb_id = pcb_id
        self.mapping_frame = mapping_frame
        self.is_allocated = False
        self.mem_type = mem_type
        self.process = None  # TODO 页存储的进程pcb
        self.file = None  # TODO 页所存储的文件
        self.IO_device = None  # TODO 页所存储的io设备
        all_page.append(self)

    # def __str__(self):
    #     string = "页ID：{}".format(self.page_id) + '\n' + \
    #              "页大小：{}".format(self.size) + '\n' + \
    #              "页是否占用：{}".format(self.bitmap) + '\n' + \
    #              "页已用大小：{}".format(self.used_size) + '\n' + \
    #              "页地址：{}".format(self.page_address) + '\n' + \
    #              "存储数据类型：{}".format(self.mem_type) + '\n'
    #     return string


# TODO:页表

class Frame:
    def __init__(self, mapping_page=None):
        """
        Page 的构造函数展示了页结构，构造函数用于初始化页
        :param mapping_page: 该帧所映射到的页的id
        """
        self.frame_id = Tool.uniqueNum()
        self.mapping_page = mapping_page  # TODO 设置地址
        self.is_used = False
