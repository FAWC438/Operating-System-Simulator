import FileSystem
from Process import *
from ProcessorScheduling import priorityScheduling

# TODO:优化中断表现形式

if __name__ == '__main__':
    FileSystem.initFileSystem()
    process_queue = [Process(DataType.Default, 0, 5, priority=10), Process(DataType.Default, 1, 3, priority=8),
                     Process(DataType.Default, 3, 6, priority=12), Process(DataType.Default, 2, 11, priority=2),
                     Process(DataType.Default, 5, 2, priority=6)]
    system_clock = 0

    if scheduling_algorithm == ProcessAlgorithm.Priority:
        # 通过PyCharm的调试可查看输出结果
        system_clock = priorityScheduling(process_queue, system_clock)
    print('OK')
