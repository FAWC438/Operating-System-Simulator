from flask import Blueprint, session, request, jsonify
from kernal.IOSystem import *

io = Blueprint('io', __name__)
'''
devices: 设备列表
    Disk = Device('Disk', 8000000)
    NetworkCard = Device('NetworkCard', 300000)
    Mouse = Device('Mouse', 15)
    KeyBoard = Device('KeyBoard', 10)
'''
Disk, NetworkCard, Mouse, KeyBoard = initIO()
devices = [Disk, NetworkCard, Mouse, KeyBoard]


def getDeviceTable():
    global devices
    return devices


def setDeviceTable(device_table):
    global devices
    if not len(devices) == len(device_table):
        devices = [device_table, devices[-1]]
    else:
        devices = device_table


# 获取针对一个设备的所有请求列表
def getDeviceRequestQueue(device):
    queue = []
    for item in device.request_queue:
        queue.append({
            "sourceProcess": item.source_process.get_process_id(),
            "occupiedTime": item.occupied_time,
            "ioOperationTime": item.IO_operation_time,
            "requestContent": item.request_content,
            "isFinish": int(item.is_finish == True)
            # "targetFile": item.target_file.file_name
        })
    return queue


# 获取一个设备的基本信息
def getIODevices():
    global devices
    message = {}
    for device in devices:
        message.update({
            device.name: {
                "transferRate": str(device.transfer_rate),
                "isBusy": int(device.is_busy == True),
                "buffer": device.buffer,
                "requestQueue": getDeviceRequestQueue(device)
            }
        })
    return message


@io.route("/createDevice", methods=['POST'])
def createDevice():
    global devices
    deviceName = request.form.get("deviceName")
    transferRate = int(request.form.get("transferRate"))
    newDevice = Device(deviceName, transferRate)
    devices.append(newDevice)
    return jsonify({"message": "Success!"})
