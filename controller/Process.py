from controller.Memory import *
from controller.IOSystem import Disk, NetworkCard, Mouse, KeyBoard
from controller.FileSystem import *

from kernal.ProcessorSchedulingForBackEnd import *

process = Blueprint('process', __name__)

memo = []
fileSysAttr = []
device_table = [Disk, NetworkCard, Mouse, KeyBoard]
process_q = []
process_now_queue = []
swap_queue = []  # 进程swap空间（队列）
process_running = None  # 上一个周期执行的进程，无需传给前端
process_cur = None  # 正在执行的进程


@process.route("/updateSystemClock", methods=['POST'])
def update():
    global memo
    global fileSysAttr
    global process_q, swap_queue, process_running, process_cur, process_now_queue, device_table
    msg_clock = int(request.form.get("clock"))
    fileSysAttr = getAttr()
    if msg_clock == 0:
        memo = getMemory()
        process_q, swap_queue, process_running, process_cur, process_now_queue, memo, device_table, fileSysAttr = \
            createQueue(msg_clock, swap_queue, process_running, process_cur, process_now_queue, memo, device_table,
                        fileSysAttr)
    else:
        if not msg_clock == 0:
            process_q, swap_queue, process_running, process_cur, process_now_queue, memo, device_table, fileSysAttr = \
                DoAlgorithm(msg_clock, process_q, swap_queue, process_running, process_cur, process_now_queue, memo,
                            device_table, fileSysAttr)
    setMemory(memo)
    setAttr(fileSysAttr)
    msgRunning, msgWaiting, msgUncreated, msgTerminated, msgSwapOut = getMsg(process_q, swap_queue, process_now_queue)
    message = {"queueInfo": {"waiting": msgWaiting,
                             "running": msgRunning,
                             "uncreated": msgUncreated,
                             "destroyed": msgTerminated,
                             "swap": msgSwapOut}}
    message.update({"memoryInfo": MemoryInfo()})
    return jsonify(message)


@process.route("/getProcessDetailInfo", methods=['POST'])
def getProcessDetailInfo():
    global process_q
    session["processId"] = request.form.get("processID")
    message = getProcessInfo(session["processId"], process_q)
    return jsonify(message)
