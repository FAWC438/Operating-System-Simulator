from flask import Blueprint, session, request, jsonify
from kernal.Memory import *

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


def MemoryDetailInfo(frameId):
    global Memory
    message = {}
    for f in Memory:
        if f.frame_id == frameId:
            if f.is_used:
                message.update({"isUsed": "True"})
            else:
                message.update({"isUsed": "False"})
            message.update({"pageId": f.mapping_page.page_id,
                            "pcbId": f.mapping_page.pcb_id})
            return message
    return {"message": "Failed! Frame Wrong!"}


@memory.route("/getMemoryInfo", methods=['POST'])
def getMemoryInfo():
    message = MemoryInfo()
    return jsonify(message)


@memory.route("/getMemoryDetailInfo", methods=['POST'])
def getMemoryDetailInfo():
    session["frameId"] = request.form.get("frameId")
    message = MemoryDetailInfo(session["frameId"])
    return jsonify(message)
