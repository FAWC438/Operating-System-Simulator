from flask import Blueprint, session, request, jsonify
from kernal.IOSystem import *

io = Blueprint('io', __name__)

Disk = Device('Disk', 8000000, False)
NetworkCard = Device('NetworkCard', 300000, False)
Mouse = Device('Mouse', 15, False)
KeyBoard = Device('KeyBoard', 10, False)
