from flask import Blueprint, session, request, jsonify
from controller.Memory import Memory
from controller.IOSystem import Disk, NetworkCard, Mouse, KeyBoard

from kernal.ProcessorSchedulingForBackEnd import *

process = Blueprint('process', __name__)
device_table = [Disk, NetworkCard, Mouse, KeyBoard]
process_q = []
swap_queue = []  # 进程swap空间（队列）
process_now_queue = []  # 进程执行队列
process_running = None  # 上一个周期执行的进程，无需传给前端
process_cur = None  # 正在执行的进程


@process.route("/updateSystemClock", methods=['POST'])
def update():
    global process_q, swap_queue
    msg_clock = int(request.form.get("SystemClock"))
    if msg_clock == 0:
        process_q = createQueue(msg_clock, swap_queue, process_running, process_cur, Memory, device_table)
    else:
        if not msg_clock:
            DoAlgorithm(msg_clock, process_q, swap_queue, process_running, process_cur, Memory, device_table)
    msgRunning, msgWaiting, msgUncreated, msgTerminated, msgSwapOut = getMsg(msg_clock, process_q, swap_queue)
    return jsonify({"waiting": msgWaiting,
                    "running": msgRunning,
                    "uncreated": msgUncreated,
                    "destroyed": msgTerminated,
                    "swap": msgSwapOut})


@process.route("/getProcessDetailInfo", methods=['POST'])
def getProcessDetailInfo():
    global process_q
    session["processId"] = request.form.get("processId")
    message = getProcessInfo(session["processId"], process_q)
    return jsonify(message)
