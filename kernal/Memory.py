from PageAndFrame import *


def freeMemory(pageList: list):
    for p in pageList:
        if not p.is_allocated:
            continue
        p.mapping_frame.mapping_page = None
        p.mapping_frame.is_used = False
        p.mapping_frame = None
        p.is_allocated = False


def allocateMemory(pageList: list, process_q: list, Memory: list):
    """
    内存分配
    :param Memory: 物理内存
    :param pageList:待分配的进程的内存页列表
    :param process_q:进程队列，该队列去除了调用本方法（即申请内存分配）的那个进程
    :return:
    """
    for p in pageList:
        if p.is_allocated:
            # 即使一个进程需要内存分配，其包含的各个页中也可能存在已经分配好的页
            continue
        # 顺序在物理内存中找空的帧来映射
        for f in Memory:
            if not f.is_used:
                # 实际上每个页的重新映射也是一个缺页中断
                p.mapping_frame = f
                f.mapping_page = p
                p.is_allocated = True
                f.is_used = True
                break
        # 没有足够的帧，则发生页错误
        else:
            pageFault(p, process_q)


def pageFault(page_to_replace, process_q):
    # 以下为LRU
    process_to_replace = LRU(process_q)

    # 以下是opt
    #     process_to_replace = OPT(process_q)

    # 进行页面置换

    replace_success_flag = False
    if process_to_replace is not None:
        for page in process_to_replace.page_list:
            if page.is_allocated:
                page.mapping_frame.mapping_page = page_to_replace  # 帧映射到新页上
                page_to_replace.mapping_frame = page.mapping_frame  # 新页更新帧的映射关系
                page_to_replace.is_allocated = True
                page.mapping_frame = None  # 被置换的页面取消映射关系
                page.is_allocated = False
                process_to_replace.page_all_allocated = False
                replace_success_flag = True
                break
    if not replace_success_flag:
        print("页置换错误!!!!", end=' ')
        print(process_to_replace)


def LRU(process_q):
    latest_time = 9999999
    process_to_replace = None
    # 先找到可以被置换的，最久没有使用的进程
    for process in process_q:
        if process.scheduled_info != [] and \
                (process.scheduled_info[-1][1] == 1 or
                 process.scheduled_info[-1][1] == 3 or
                 process.scheduled_info[-1][1] == 5):
            # 只查找每个最近（列表最后一位）被暂停（元组第二位为2）的进程，因为只有这些进程被分配过内存，且没有正在运行

            # 若一个进程所有的页已经被换出，则不必再考虑该进程
            for page in process.page_list:
                if page.is_allocated:
                    break
            else:
                continue

            if latest_time > process.scheduled_info[-1][0]:
                latest_time = process.scheduled_info[-1][0]
                process_to_replace = process
    return process_to_replace


def OPT(process_q):
    max_time = 9999999
    longest_time = 0
    process_to_replace = None
    for process in process_q:
        if process.scheduled_info != [] and process.scheduled_info[-1][1] == 1:
            # 只查找每个最近（列表最后一位）被暂停（元组第二位为2）的进程，因为只有这些进程被分配过内存，且没有正在运行

            # 若一个进程所有的页已经被换出，则不必再考虑该进程
            for page in process.page_list:
                if page.is_allocated:
                    break
            else:
                continue

            # 找出该进程的当前与下一次被调用的间隔
            if longest_time < (max_time - process.scheduled_info[-1][0]):
                longest_time = max_time - process.scheduled_info[-1][0]
                process_to_replace = process
    return process_to_replace


def initMemory(MemorySize: int = 5):
    return [Frame(i) for i in range(MemorySize)]  # 默认内存有5个帧
