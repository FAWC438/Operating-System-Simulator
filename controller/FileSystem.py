from flask import Blueprint, session, request, jsonify
from kernal.FileSystem import *

file = Blueprint('file', __name__)
state, root, disk, f_table = False, None, [], []


def getAttr():
    global root, disk, f_table
    return [root, disk, f_table]


def setAttr(fileSysAttr):
    global root, disk, f_table
    root = fileSysAttr[0]
    disk = fileSysAttr[1]
    f_table = fileSysAttr[2]


# 初始化文件系统
@file.route('/Initialize', methods=['POST'])
def init_FileSystem():
    global state, root, disk, f_table
    state, root, disk, f_table = initFileSystem()
    message = FileTree(root)
    return jsonify(message)


# 创建目录
@file.route('/createFolder', methods=['POST'])
def create_Folder():
    session['filePath'] = request.form.get('filePath')
    message = pathToObj(session['filePath'], {"operator": "createFolder"}, f_table, disk, root)

    if message == -1:
        # 目录重名
        return jsonify({'message': 'Failed!',
                        'data': 'Folder Already Exists!'})
    # 成功
    else:
        return jsonify({'message': 'Success!',
                        'data': message.__str__() + ' Created!'})


# 创建文件
@file.route('/createFile', methods=['POST'])
def create_File():
    session['filePath'] = request.form.get('filePath')
    message = pathToObj(session['filePath'], {"operator": "createFile", "content": ""}, f_table, disk, root)

    if isinstance(message, int):
        # 同目录文件重名
        if message == -1:
            return jsonify({'message': 'Failed!',
                            'data': 'File Already Exists!'})
        # 磁盘读写错误
        elif message == -2:
            return jsonify({'message': 'Failed!',
                            'data': 'Disk Allocation Fault!'})
    # 成功
    else:
        return jsonify({'message': 'Success!',
                        'data': message.__str__() + ' Created!'})


# 读文件
@file.route('/readFile', methods=['POST'])
def read_File():
    session['filePath'] = request.form.get('filePath')
    message = pathToObj(session['filePath'], {"operator": "readFile"}, f_table, disk, root)
    if isinstance(message, int):
        # 文件不存在
        if message == 0:
            return jsonify({'message': 'Failed!',
                            'data': 'File Does Not Exist!'})
        if message == -1:
            return jsonify({'message': 'Failed!',
                            'data': 'Permission Denied!'})
    # 成功,返回对象是文件内容
    else:
        print(message)
        return jsonify({'message': 'Success!',
                        'data': message})


# 写文件
@file.route('/writeFile', methods=['POST'])
def write_File():
    session['filePath'] = request.form.get('filePath')
    session['content'] = request.form.get('Content')
    message = pathToObj(session['filePath'], {"operator": "writeFile", "content": session['content']}, f_table, disk,
                        root)
    # 文件不存在
    if message == 0:
        return jsonify({'message': 'Failed!',
                        'data': 'File Does Not Exist!'})
    # 权限不足
    elif message == -1:
        return jsonify({'message': 'Failed!',
                        'data': 'Permission Denied!'})
    # 成功
    else:
        return jsonify({'message': 'Success!',
                        'data': ''})


# 删文件
@file.route('/delFile', methods=['POST'])
def del_File():
    session['filePath'] = request.form.get('filePath')
    message = pathToObj(session['filePath'], {"operator": "delFile"}, f_table, disk, root)
    # 文件不存在
    if message == 0:
        return jsonify({'message': 'Failed!',
                        'data': 'File Does Not Exist!'})
    # 成功
    else:
        return jsonify({'message': 'Success!',
                        'data': ''})


# 重命名目录
@file.route('/renameFolder', methods=['POST'])
def rename_Folder():
    session['filePath'] = request.form.get('filePath')
    session['newName'] = request.form.get('newName')
    message = pathToObj(session['filePath'], {"operator": "renameFolder", "newName": session['newName']}, f_table, disk,
                        root)
    # 文件不存在
    if message == 0:
        return jsonify({'message': 'Failed!',
                        'data': 'Folder Does Not Exist!'})
    # 命名冲突
    elif message == -1:
        return jsonify({'message': 'Failed!',
                        'data': 'Folder Already Exists!'})
    # 成功
    else:
        return jsonify({'message': 'Success!',
                        'data': ''})


# 重命名文件
@file.route('/renameFile', methods=['POST'])
def rename_File():
    session['filePath'] = request.form.get('filePath')
    session['newName'] = request.form.get('newName')
    message = pathToObj(session['filePath'], {"operator": "renameFile", "newName": session['newName']}, f_table, disk,
                        root)
    # 文件不存在
    if message == 0:
        return jsonify({'message': 'Failed!',
                        'data': 'File Does Not Exist!'})
    # 命名冲突
    elif message == -1:
        return jsonify({'message': 'Failed!',
                        'data': 'File Already Exists!'})
    # 成功
    else:
        return jsonify({'message': 'Success!',
                        'data': ''})

# 重定向文件
# @file.route('/redirectFile/', methods=['POST'])
# def redirect_File():
#     session['fileName'] = request.form.get('fileName')
#     session['folderName'] = request.form.get('folderName')
#     message = redirectFile(session['fileName'], session['folderName'])
#     if message == 0:
#         return jsonify({'message': 'Failed!',
#                         'data': 'Target Does Not Exist!'})
#     else:
#         return jsonify({'message': 'Success!',
#                         'data': ''})
