import datetime
import random


def uniqueNum():
    """
    生成唯一的随机数用于ID号
    :return:随机数
    """
    for i in range(0, 10):
        nowTime = datetime.datetime.now().strftime("%M%S")  # 生成当前时间
        randomNum = random.randint(0, 99)  # 生成的随机整数
        if randomNum < 10:
            randomNum = str(0) + str(randomNum)
        return str(nowTime) + str(randomNum)
