"""
目录逻辑结构：树形
目录物理结构：连续形
"""
import math

import Tool

root = None

disk = [-1 for i in range(1000)]  # 磁盘，存储文件的id

file_table = []  # 文件表，存储所有已经建立的文件


class Folder:
    def __init__(self, folder_name: str, parent_folder, child_nodes: list):
        """
        文件夹数据结构，请注意，文件夹为逻辑结构，因此不会占用物理磁盘空间

        :param folder_name:文件夹名
        :param parent_folder:父节点。所有父节点一定是文件夹，注意，根节点（根文件夹）没有父节点，该属性为None
        :param child_nodes:子节点。可能有多个，且可能是文件夹，也可能是文件
        """
        self.id = Tool.uniqueNum()
        self.folder_name = folder_name
        self.parent_node = parent_folder
        self.child_nodes = child_nodes

    def __str__(self):
        return self.folder_name


class UserFile:
    def __init__(self, file_name: str, parent_folder, data: str):
        """
        文件数据结构

        :param file_name:文件名
        :param parent_folder:父节点文件夹，每个文件该属性必须有值
        :param data:文件数据
        """
        self.id = Tool.uniqueNum()
        self.file_name = file_name
        self.parent_node = parent_folder
        self.data = data
        self.size = math.ceil(len(data) / 10)
        """
        size是文件占据的磁盘空间，为了方便前端表示，单位为10字节，一个英文字符一个字节，注意每次更改file内容时应当要更新该值
        eg1. yes 有三个字符，占三个字节，除以10向上取整，因此该文件占据的磁盘空间为1
        eg2. I am sure I am very handsome. 有29个字符（标点空格都算），因此该文件占据的磁盘空间为3
        """
        self.disk_position = -1  # 文件在磁盘中的位置

    def __str__(self):
        return self.file_name


def contiguousAllocation(file_to_allocated: UserFile):
    """
    磁盘文件连续分配

    :param file_to_allocated:需要分配磁盘空间的文件
    :return:返回文件所存储的磁盘位置（起始下标），若返回-1说明磁盘空间不足
    """
    global disk
    start_index = -1
    space_counter = 0
    for i in range(len(disk)):
        if disk[i] == -1:
            if start_index == -1:
                start_index = i
            space_counter += 1

            if space_counter >= file_to_allocated.size:
                for j in range(start_index, start_index + file_to_allocated.size):
                    disk[j] = file_to_allocated.id
                return start_index
        else:
            start_index = -1
            space_counter = 0
    return -1


def writeDiskToTXT():
    pass


def creatFile(is_folder: bool, name: str, parent_folder, child_nodes=None, data=None):
    """
    创建文件或文件夹

    :param is_folder:是否是文件夹
    :param name:文件/文件夹名称
    :param parent_folder:父文件夹对象
    :param child_nodes:文件夹内容
    :param data:文件数据
    :return:文件/文件夹对象。若同路径存在重名返回-1，磁盘分配错误返回-2
    """
    if child_nodes is None:
        child_nodes = []
    if is_folder:

        for node in parent_folder.child_nodes:
            if str(node) == name and isinstance(node, Folder):
                return -1

        new_folder = Folder(name, parent_folder, child_nodes)
        return new_folder
    else:

        for node in parent_folder.child_nodes:
            if str(node) == name and isinstance(node, UserFile):
                return -1

        new_file = UserFile(name, parent_folder, data)
        file_table.append(new_file)
        new_file.disk_position = contiguousAllocation(new_file)
        if new_file.disk_position == -1:
            print('磁盘空间分配错误')  # TODO：异常处理
            return -2
        return new_file


def clearFileInDisk(target_file: UserFile):
    """
    在物理磁盘中删除文件信息

    :param target_file:欲删除的文件
    """
    global disk
    for i in range(target_file.disk_position, target_file.disk_position + target_file.size):
        disk[i] = -1


def renameFolder():
    pass


def writeFile(file_name: str, content: str):
    """
    写文件内容（原先内容会删除）

    :param file_name:文件名
    :param content:新内容
    :return:返回1表示成功写入，返回0表示写入失败
    """
    global file_table
    for file in file_table:
        if file.file_name == file_name:
            clearFileInDisk(file)
            file.data = content
            file.size = math.ceil(len(content) / 10)
            file.disk_position = contiguousAllocation(file)
            return 1
    return 0


def readFile():
    pass


def delFile():
    pass


def redirectFile():
    pass


def initFileSystem():
    global root
    root = creatFile(True, 'root', None)
    default_folder_1 = creatFile(True, 'default_folder_1', root)
    default_folder_2 = creatFile(True, 'default_folder_2', root)
    default_folder_3 = creatFile(True, 'default_folder_3', root)
    test_file = creatFile(False, 'test', default_folder_1, data='This is a file for test')
    root.child_nodes = [default_folder_1, default_folder_2, default_folder_3]
    default_folder_1.child_nodes.append(test_file)
