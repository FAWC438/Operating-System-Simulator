from controller.Memory import *
from controller.IOSystem import *
from controller.FileSystem import *

from kernal.ProcessorSchedulingForBackEnd import *

process = Blueprint('process', __name__)

memo = []                   # 内存
fileSysAttr = []            # 文件参数
device_table = []           # 设备表
stat = 0                    # 系统执行进程的情况
process_q = []              # 所有进程队列
process_now_queue = []      # 当前执行/待执行队列
swap_queue = []             # 进程swap空间（队列）
process_running = None      # 上一个周期执行的进程，无需传给前端
process_cur = None          # 正在执行的进程
time_slice = 2              # 时间片


# 每个时钟周期都会更新一下系统当前状态
@process.route("/updateSystemClock", methods=['POST'])
def update():
    global memo
    global fileSysAttr
    global stat, process_q, swap_queue, process_running, process_cur, process_now_queue, device_table, time_slice
    initInter()
    msg_clock = int(request.form.get("clock"))
    memo = getMemory()
    fileSysAttr = getAttr()
    device_table = getDeviceTable()
    stat, process_q, swap_queue, process_running, process_cur, process_now_queue, memo, device_table, \
    fileSysAttr, time_slice, inter = \
        DoAlgorithm(msg_clock, stat, process_q, swap_queue, process_running, process_cur, process_now_queue,
                    memo, device_table, fileSysAttr, time_slice)
    setMemory(memo)
    setAttr(fileSysAttr)
    setDeviceTable(device_table)
    msgRunning, msgWaiting, msgUncreated, msgTerminated, msgSwapOut = getMsg(process_q, swap_queue, process_now_queue)
    message = {"queueInfo": {"waiting": msgWaiting,
                             "running": msgRunning,
                             "uncreated": msgUncreated,
                             "destroyed": msgTerminated,
                             "swap": msgSwapOut}}
    message.update({"memoryInfo": MemoryInfo()})
    message.update({"deviceInfo": getIODevices()})
    message.update({"code": stat})
    # IO进程在抢占设备时会发出IO中断
    if process_cur is not None and process_cur.get_process_type() == DataType.IO and process_cur.state == State.running:
        inter[0] = 1
    message.update({"interrupt": inter})
    return jsonify(message)


# 获取某一进程详细信息
@process.route("/getProcessDetailInfo", methods=['POST'])
def getProcessDetailInfo():
    global process_q
    session["processId"] = request.form.get("processID")
    message = getProcessInfo(session["processId"], process_q)
    return jsonify(message)


# 创建进程
@process.route("/createProcess", methods=['POST'])
def createProcess():
    global process_q, device_table
    device_table = getDeviceTable()
    dataType = int(request.form.get("processType"))
    if dataType == 0:
        dataType = DataType.Default
    else:
        dataType = DataType.IO
    startTime = int(request.form.get("startTime"))
    lastTime = int(request.form.get("lastTime"))
    priority = int(request.form.get("processPriority"))
    occupy = int(request.form.get("processOccupiedPage"))
    if dataType == DataType.IO:
        ioDuration = int(request.form.get("ioDuration"))
        targetDevice = int(request.form.get("targetDevice"))
        ioRequest = request.form.get("ioRequest")
        process_q.append(Process(dataType, startTime, lastTime, IO_operation_time=ioDuration, priority=priority,
                                 target_device=device_table[targetDevice], page_num=occupy, request_content=ioRequest))
    else:
        process_q.append(Process(dataType, startTime, lastTime, priority=priority, page_num=occupy))
    return jsonify({"message": "Success!"})
