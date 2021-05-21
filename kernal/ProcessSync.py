import threading
import time
import random

semaphore = threading.Semaphore(0)

def consumer():
        print("消费者等待")
        # 获取信号量
        semaphore.acquire()
        # 消费者访问共享资源
        print("消费者：消费 %s 号产品" % item)

def producer():
        global item
        time.sleep(10)
        # 设置随机数
        item = random.randint(0, 1000)
        print("生产者：生产 %s 号产品" % item)
        # 释放信号量，将内部计数器+1
        # 为零时，另一个线程正在等待其再次变大，唤醒该线程。
        semaphore.release()

if __name__ == '__main__':
        for i in range (0,5) :
                t1 = threading.Thread(target=producer)
                t2 = threading.Thread(target=consumer)
                t1.start()
                t2.start()
                t1.join()
                t2.join()
        print("done...")