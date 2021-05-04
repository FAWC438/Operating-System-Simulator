from Process import *

if __name__ == '__main__':
    process_queue = [Process(DataType.Default, 0, 5, 10), Process(DataType.Default, 1, 3, 8),
                     Process(DataType.Default, 3, 6, 12), Process(DataType.Default, 2, 11, 2),
                     Process(DataType.Default, 5, 2, 6)]
    system_clock = 0

    if scheduling_algorithm == ProcessAlgorithm.Priority:
        # 通过PyCharm的调试可查看输出结果
        system_clock = priorityScheduling(process_queue, system_clock)
    print('OK')
