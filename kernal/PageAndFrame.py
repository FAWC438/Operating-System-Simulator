from enum import Enum

from kernal import Tool


class DataType(Enum):
    """
    枚举类型
    """
    Default = 0
    IO = 1


class PageAlgorithm(Enum):
    """
    枚举类型，用于指示各种算法的标志数
    """
    Default = 0
    LRU = 1
    FIFO = 2
    OPT = 3


all_page = []
allocation_algorithm = PageAlgorithm.LRU  # 使用的页调度算法


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
        self.file = None                        # TODO 页所存储的文件
        self.IO_device = None                   # TODO 页所存储的io设备
        all_page.append(self)


class Frame:
    def __init__(self, mapping_page=None):
        """
        Page 的构造函数展示了页结构，构造函数用于初始化页
        :param mapping_page: 该帧所映射到的页的id
        """
        self.frame_id = Tool.uniqueNum()        # 为每一帧设置唯一id
        self.mapping_page = mapping_page        # 帧映射的页
        self.is_used = False                    # 当帧被使用则为True
