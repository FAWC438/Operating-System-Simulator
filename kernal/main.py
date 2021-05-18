import FileSystem
from Process import *
from ProcessorScheduling import prioritySchedulingSync, prioritySchedulingAsync, fcfs, round_robin

# TODO:优化中断表现形式

if __name__ == '__main__':
    # 前端该做的
    process_queue = [Process(DataType.Default, 0, 5, priority=10), Process(DataType.Default, 1, 3, priority=8),
                     Process(DataType.Default, 3, 6, priority=12), Process(DataType.Default, 2, 11, priority=2),
                     Process(DataType.Default, 5, 2, priority=6)]
    system_clock = 0

    # 后端该做的
    FileSystem.initFileSystem()
    if scheduling_algorithm == ProcessAlgorithm.PrioritySync:
        # 通过PyCharm的调试可查看输出结果
        system_clock = prioritySchedulingSync(process_queue, system_clock)
    elif scheduling_algorithm == ProcessAlgorithm.PriorityAsync:
        system_clock = prioritySchedulingAsync(process_queue, system_clock)
    elif scheduling_algorithm == ProcessAlgorithm.FCFS:
        system_clock = fcfs(process_queue, system_clock)
    elif scheduling_algorithm == ProcessAlgorithm.RR:
        system_clock = round_robin(process_queue, system_clock)
    print('OK')
