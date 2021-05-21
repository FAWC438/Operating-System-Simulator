import FileSystem
from Process import *

# TODO:优化中断表现形式
from kernal import IOSystem, Memory
import IOSystem, Memory
from kernal.ProcessorSchedulingForBackEnd import prioritySchedulingSyncForBackEnd, prioritySchedulingAsyncForBackEnd, \
    fcfsForBackEnd
from ProcessorSchedulingForBackEnd import prioritySchedulingSyncForBackEnd, prioritySchedulingAsyncForBackEnd, \
    fcfsForBackEnd

if __name__ == '__main__':
    # 现在，各个模块必须进行初始化
    s, root, Disk, file_table = FileSystem.initFileSystem()
    d_table = IOSystem.initIO()
    m = Memory.initMemory()
    swap_queue = []  # 进程swap空间（队列）
    process_now_queue = []  # 进程执行队列
    process_running = None  # 上一个周期执行的进程，无需传给前端
    process_cur = None  # 正在执行的进程
    code = -1

    print('旧文件内容：' + FileSystem.readFile('test', root))
    # 前端该做的
    process_queue = [Process(DataType.Default, 0, 5, priority=10), Process(DataType.Default, 1, 3, priority=8),
                     Process(DataType.Default, 3, 6, priority=12),
                     Process(DataType.IO, 8, 8, IO_operation_time=5, priority=7, target_device=d_table[1],
                             request_content="这是个IO请求"),
                     Process(DataType.IO, 11, 3, IO_operation_time=2, priority=4, target_device=d_table[0],
                             request_content="writeFile|test|新内容!"),
                     Process(DataType.Default, 2, 11, priority=2), Process(DataType.Default, 5, 2, priority=6)]
    system_clock = 0

    while code != 3:

        # 后端该做的
        if scheduling_algorithm == ProcessAlgorithm.PrioritySync:
            # 后端需要将返回的process_cur, process_running用于下一个时钟周期，swap_q、memory和device_table由于是指针引用，因此无需返回指内部数据也会更改
            code, process_cur, process_running, process_now_queue, f_list = prioritySchedulingSyncForBackEnd(
                process_queue,
                system_clock,
                swap_q=swap_queue,
                proc_running=process_running,
                proc_cur=process_cur,
                memory=m,
                device_table=d_table,
                root=root,
                Disk=Disk,
                file_table=file_table)

            root, Disk, file_table = f_list

        elif scheduling_algorithm == ProcessAlgorithm.PriorityAsync:
            code, process_cur, process_running, process_now_queue, f_list = prioritySchedulingAsyncForBackEnd(
                process_queue,
                system_clock,
                swap_q=swap_queue,
                proc_running=process_running,
                proc_cur=process_cur,
                memory=m,
                device_table=d_table,
                root=root,
                Disk=Disk,
                file_table=file_table)

            root, Disk, file_table = f_list

        elif scheduling_algorithm == ProcessAlgorithm.FCFS:
            code, process_cur, process_running, process_now_queue, f_list = fcfsForBackEnd(process_queue, system_clock,
                                                                                           proc_running=process_running,
                                                                                           proc_cur=process_cur,
                                                                                           memory=m,
                                                                                           device_table=d_table,
                                                                                           root=root,
                                                                                           Disk=Disk,
                                                                                           file_table=file_table)
            root, Disk, file_table = f_list

        system_clock += 1

    # if scheduling_algorithm == ProcessAlgorithm.PrioritySync:
    #     # 通过PyCharm的调试可查看输出结果
    #     system_clock = prioritySchedulingSync(process_queue, system_clock, m)
    # elif scheduling_algorithm == ProcessAlgorithm.PriorityAsync:
    #     system_clock = prioritySchedulingAsync(process_queue, system_clock, m, d_table)
    # elif scheduling_algorithm == ProcessAlgorithm.FCFS:
    #     system_clock = fcfs(process_queue, system_clock, m, d_table)
    # elif scheduling_algorithm == ProcessAlgorithm.RR:
    #     system_clock = round_robin(process_queue, system_clock, m, d_table)
    print('OK')
    print('新文件内容：' + FileSystem.readFile('test', root))
