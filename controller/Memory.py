from flask import Blueprint, session, request, jsonify
from kernal.Memory import *
from kernal.PageAndFrame import Frame

memory = Blueprint('memory', __name__)
MemorySize = 5
Algorithm = "LRU"
Memory = [Frame(i) for i in range(MemorySize)]  # 默认内存有100个帧


def getMemory():
    global Memory
    return Memory


def setMemory(memo: list):
    global Memory
    Memory = memo


# 获取内存基本信息
def MemoryInfo():
    global Memory, MemorySize, Algorithm
    memoList = []
    for f in Memory:
        if f.is_used:
            memoList.append({f.frame_id: 1})
        else:
            memoList.append({f.frame_id: 0})
    message = {"MemorySize": MemorySize,
               "Algorithm": Algorithm,
               "MemoryTable": memoList}
    return message


# 获取某一帧的详细信息
def MemoryDetailInfo(frameId):
    global Memory
    message = {}
    for f in Memory:
        if f.frame_id == frameId:
            if f.is_used:
                message.update({"memoryState": "True"})
            else:
                message.update({"memoryState": "False"})
            if f.mapping_page is not None:
                message.update({"frameId": f.frame_id,
                                "memoryPageId": f.mapping_page.page_id,
                                "memoryProcessId": f.mapping_page.pcb_id})
            else:
                message.update({"frameId": f.frame_id,
                                "memoryPageId": "",
                                "memoryProcessId": ""})
            return message
    return {"message": "Failed! Frame Wrong!"}


# 获取内存基本信息
@memory.route("/getMemoryInfo", methods=['POST'])
def getMemoryInfo():
    message = MemoryInfo()
    return jsonify(message)


# # 获取某一帧的详细信息
@memory.route("/getMemoryDetailInfo", methods=['POST'])
def getMemoryDetailInfo():
    session["frameId"] = Memory[int(request.form.get("frameID"))-1].frame_id
    message = MemoryDetailInfo(session["frameId"])
    return jsonify(message)
