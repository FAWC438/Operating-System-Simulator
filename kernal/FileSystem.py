"""
目录逻辑结构：树形
目录物理结构：连续形
TODO:磁盘外部碎片如何处理？
TODO:磁盘IO添加中断
"""
import math
from enum import Enum

from kernal import Tool


class FileOperation(Enum):
    Read = 0
    Write = 1
    Create = 2
    Rename = 3
    Delete = 4
    Redirect = 5


class FileAuthority(Enum):
    Default = 0
    ReadOnly = 1
    WriteOnly = 2


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
    def __init__(self, file_name: str, parent_folder, data, authority: FileAuthority = FileAuthority.Default):
        """
        文件数据结构

        :param file_name:文件名
        :param parent_folder:父节点文件夹，每个文件该属性必须有值
        :param data:文件数据
        :param authority:文件权限
        """
        self.id = Tool.uniqueNum()
        self.file_name = file_name
        self.parent_node = parent_folder
        self.data = data
        self.size = math.ceil(len(data) / 10)
        """
        size是文件占据的磁盘空间，为了方便前端表示，单位为10字节（即磁盘一个块有10字节），一个英文字符一个字节，注意每次更改file内容时应当要更新该值
        eg1. yes 有三个字符，占三个字节，除以10向上取整，因此该文件占据的磁盘空间为1
        eg2. I am sure I am very handsome. 有29个字符（标点空格都算），因此该文件占据的磁盘空间为3
        """
        self.disk_position = -1  # 文件在磁盘中的位置
        self.authority = authority

    def __str__(self):
        return self.file_name


def contiguousAllocation(file_to_allocated: UserFile):
    """
    磁盘文件连续分配

    :param file_to_allocated:需要分配磁盘空间的文件
    :return:返回文件所存储的磁盘位置（起始下标），若返回-1说明磁盘空间不足
    """
    global Disk
    start_index = -1
    space_counter = 0
    for i in range(len(Disk)):
        # 主要思想是，找到磁盘中连续且符合文件大小的几个块，且从磁盘头部遍历查找，这样有利于减少外部碎片
        if Disk[i] == -1:
            if start_index == -1:
                start_index = i
            space_counter += 1

            if space_counter >= file_to_allocated.size:
                for j in range(start_index, start_index + file_to_allocated.size):
                    Disk[j] = file_to_allocated.id
                return start_index
        else:
            start_index = -1
            space_counter = 0
    return -1


def writeDiskToTXT():
    # TODO:把结果输出到TXT？
    pass


def creatFileOrFolder(is_folder: bool, name: str, parent_folder: Folder, data, child_nodes=None):
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
        if parent_folder is not None:
            for node in parent_folder.child_nodes:
                if str(node) == name and isinstance(node, Folder):
                    return -1

        new_folder = Folder(name, parent_folder, child_nodes)
        if not name == 'root':
            parent_folder.child_nodes.append(new_folder)
        return new_folder
    else:

        for node in parent_folder.child_nodes:
            if str(node) == name and isinstance(node, UserFile):
                # 同路径重名
                return -1

        new_file = UserFile(name, parent_folder, data)
        file_table.append(new_file)
        new_file.disk_position = contiguousAllocation(new_file)
        if new_file.disk_position == -1:
            print('磁盘空间分配错误')  # TODO：异常处理
            return -2
        print("???", parent_folder)
        parent_folder.child_nodes.append(new_file)
        return new_file


def getPath(is_folder: bool, target_folder: Folder = None, target_file: UserFile = None):
    """
    利用递归获取文件/文件夹的路径

    :param is_folder:欲获取路径的对象是否是文件夹
    :param target_folder:目标文件夹
    :param target_file:目标文件
    :return:目标对象的路径
    """
    if is_folder and target_folder.folder_name == 'root':
        return '/root'

    if not is_folder:
        path_now = target_file.file_name
        parent_node = target_file.parent_node
    else:
        path_now = target_folder.folder_name
        parent_node = target_folder.parent_node

    path = getPath(True, target_folder=parent_node) + '/' + path_now
    return path


state = False

root = creatFileOrFolder(True, 'root', None, None)

DiskSize = 1000

Disk = [-1 for i in range(DiskSize)]  # 磁盘，存储文件的id

file_table = []  # 文件表，存储所有已经建立的文件

"""
路径的格式为： /root/aaa/w
以上路径表示root文件夹下的aaa文件夹的名为w的文件/文件夹
"""


def pathToObj(path: str, IR: dict):
    """
    通过路径找到文件/文件夹

    :param IR: 直接执行指令
    :param path:文件字符串
    :return:文件/文件夹对象。若查找错误，返回0
    """
    path = path.replace(" ", "")
    global root
    path_node_list = path.split('/')
    if path_node_list[0] == "":
        path_node_list = path_node_list[1:]
    print(path, path_node_list, IR)
    if len(path_node_list) < 1 or path_node_list[0] != 'root':
        return 0
    # 从root出发
    parent_node = root
    # 每次都会更新子节点们
    child_node_names = list(map(str, parent_node.child_nodes))
    for i in range(1, len(path_node_list)):
        print(path_node_list[i], child_node_names)
        if i == len(path_node_list) - 1:
            # 单纯的查询文件目录树
            if IR is None:
                return parent_node.child_nodes[child_node_names.index(path_node_list[i])]
            elif IR["operator"] == "createFile":
                return creatFileOrFolder(False, path_node_list[i], parent_node, data=IR['content'])
            elif IR["operator"] == "createFolder":
                return creatFileOrFolder(True, path_node_list[i], parent_node, None)
            else:
                # 不存在问题
                if not path_node_list[i] in child_node_names:
                    return 0
                target = parent_node.child_nodes[child_node_names.index(path_node_list[i])]
                # 读文件
                if IR["operator"] == "readFile":
                    # 权限不够
                    if target.authority == FileAuthority.WriteOnly:
                        return -1
                    # 读数据
                    else:
                        return target.data
                # 写文件
                elif IR["operator"] == "writeFile":
                    # 权限不够
                    if target.authority == FileAuthority.ReadOnly:
                        return -1
                    # 写数据
                    else:
                        clearFileInDisk(target)
                        target.data = IR["content"]
                        target.size = math.ceil(len(IR["content"]) / 10)
                        target.disk_position = contiguousAllocation(target)
                        return 1
                elif IR["operator"] == "delFile":
                    if isinstance(target, Folder):
                        return 0
                    else:
                        clearFileInDisk(target)
                        file_table.remove(target)
                        target.parent_node.child_nodes.remove(target)
                        return 1
                elif IR["operator"] == "renameFile":
                    if IR["newName"] in child_node_names:
                        print('新名称在同路径下冲突')
                        return -1
                    else:
                        target.file_name = IR["newName"]
                        return 1
                elif IR["operator"] == "renameFolder":
                    if IR["newName"] in child_node_names:
                        print('新名称在同路径下冲突')
                        return -1
                    else:
                        target.folder_name = IR["newName"]
                        return 1
        elif path_node_list[i] in child_node_names:
            parent_node = parent_node.child_nodes[child_node_names.index(path_node_list[i])]
            child_node_names = list(map(str, parent_node.child_nodes))
            print("!!!", parent_node)
        else:
            return 0


def clearFileInDisk(target_file: UserFile):
    """
    在物理磁盘中删除文件信息

    :param target_file:欲删除的文件
    """
    global Disk
    for i in range(target_file.disk_position, target_file.disk_position + target_file.size):
        Disk[i] = -1


def findFileById(file_id: int):
    """
    通过文件id返回文件对象
    该函数常用于磁盘索引文件，因为在本项目中磁盘仅需读取文件标识符（id）即可找到文件对象

    :param file_id:文件标识符
    :return:文件对象。若返回-1表明没有找到对应标识符的文件
    """
    global file_table

    for f in file_table:
        if f.id == file_id:
            return f
    return -1


def findObjByName(name: str, parent_node=root):
    """
    利用递归，查找除了root文件夹以外的文件系统对象

    :param name:文件/文件夹名称
    :param parent_node:该参数用于递归，对用户是透明的，就是说在调用该函数时不需填写该参数
    :return:None表示没有该对象，否则返回文件系统对象
    """

    if not parent_node.child_nodes:
        return None

    child_node_names = list(map(str, parent_node.child_nodes))
    if name in child_node_names:
        return parent_node.child_nodes[child_node_names.index(name)]
    else:
        for child_node in parent_node.child_nodes:
            if isinstance(child_node, Folder):
                result = findObjByName(name, child_node)
                if result is not None:
                    return result
        return None


def renameFolder(old_name: str, new_name: str):
    """
    重命名文件夹

    :param old_name:旧名称
    :param new_name:新名称
    :return:0表示找不到文件夹，-1表示新名字重名，1表示改名成功
    """
    folder_obj = findObjByName(old_name)
    if folder_obj is None:
        print('找不到该文件夹')  # TODO:异常处理
        return 0

    child_node_names = list(map(str, folder_obj.parent_node.child_nodes))
    if new_name in child_node_names:
        print('新名称在同路径下冲突')
        return -1
    else:
        folder_obj.folder_name = new_name
        return 1


def renameFile(old_name: str, new_name: str):
    """
    重命名文件

    :param old_name:旧名称
    :param new_name:新名称
    :return:0表示找不到文件，-1表示新名字重名，1表示改名成功
    """
    file_obj = findObjByName(old_name)
    if file_obj is None:
        print('找不到该文件')  # TODO:异常处理
        return 0

    child_node_names = list(map(str, file_obj.parent_node.child_nodes))
    if new_name in child_node_names:
        print('新名称在同路径下冲突')
        return -1
    else:
        file_obj.file_name = new_name
        return 1


def writeFile(file_name: str, content: str):
    """
    写文件内容（原先内容会删除）

    :param file_name:文件名
    :param content:新内容
    :return:返回1表示成功写入，返回0表示写入失败，返回-1表示文件没有写权限
    """
    target_file = findObjByName(file_name)

    if target_file is None or isinstance(target_file, Folder):
        print('文件不存在')  # TODO:异常处理
        return 0

    assert isinstance(target_file, UserFile)
    if target_file.authority == FileAuthority.ReadOnly:
        print('文件权限不足')  # TODO:异常处理
        return -1
    else:

        clearFileInDisk(target_file)
        target_file.data = content
        target_file.size = math.ceil(len(content) / 10)
        target_file.disk_position = contiguousAllocation(target_file)
        return 1


def readFile(file_name: str):
    """
    读取文件

    :param file_name:文件名称
    :return:返回文件数据字符串，若返回0表明文件不存在，返回-1表明文件权限不足
    """
    target_file = findObjByName(file_name)
    if target_file is None or isinstance(target_file, Folder):
        print('文件不存在')  # TODO:异常处理
        return 0

    assert isinstance(target_file, UserFile)
    if target_file.authority == FileAuthority.WriteOnly:
        print('文件权限不足')  # TODO:异常处理
        return -1
    else:
        return target_file.data


def delFile(file_name: str):
    """
    彻底删除文件，包括磁盘和文件表的记录

    :param file_name:文件名
    :return:返回0表示无法找到对应文件，返回1表明删除成功
    """
    target_file = findObjByName(file_name)
    if target_file is None or isinstance(target_file, Folder):
        print('文件不存在')  # TODO:异常处理
        return 0

    assert isinstance(target_file, UserFile)
    clearFileInDisk(target_file)
    file_table.remove(target_file)
    target_file.parent_node.child_nodes.remove(target_file)

    return 1


def redirectFile(file_name: str, target_folder_name: str):
    """
    在不删除文件的情况下重定向文件路径，可以和其他操作组合实现复制和剪切等操作

    :param file_name:欲重定向的文件名称
    :param target_folder_name:欲重定向的目标文件夹
    :return:返回0表示无法找到对应文件，返回1表明重定向成功
    """
    target_file = findObjByName(file_name)
    if target_file is None or isinstance(target_file, Folder):
        print('文件不存在')  # TODO:异常处理
        return 0
    target_folder = findObjByName(target_folder_name)
    if target_folder is None or isinstance(target_folder, UserFile):
        print('文件夹不存在')  # TODO:异常处理
        return 0

    assert isinstance(target_file, UserFile)
    assert isinstance(target_folder, Folder)
    target_file.parent_node.child_nodes.remove(target_file)
    target_file.parent_node = target_folder
    target_folder.child_nodes.append(target_file)
    return 1


def initFileSystem():
    """
    文件系统初始化

    :return:
    """
    global state, root
    if not state:
        state = True
        default_folder_1 = creatFileOrFolder(True, 'default_folder_1', root, None)
        default_folder_2 = creatFileOrFolder(True, 'default_folder_2', root, None)
        default_folder_3 = creatFileOrFolder(True, 'default_folder_3', root, None)
        test_file = creatFileOrFolder(False, 'test', default_folder_1, data='This is a file for test')
        root.child_nodes = [default_folder_1, default_folder_2, default_folder_3]


def FileTree(parent_node):
    # 是目录
    if isinstance(parent_node, Folder):
        data = []
        child_nodes = list(parent_node.child_nodes)
        for child in child_nodes:
            data.append(FileTree(child))
        return {parent_node.__str__(): data}
    elif isinstance(parent_node, UserFile):
        return {parent_node.__str__(): 0}


if __name__ == '__main__':
    initFileSystem()
    print(FileTree(root))
