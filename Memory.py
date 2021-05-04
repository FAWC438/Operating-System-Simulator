from PageAndFrame import *

Memory = [Frame(i) for i in range(100)]  # 默认内存有100个帧


def allocateMemory(pageList: list, process_q: list):
    """
    内存分配
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
                p.mapping_frame = f
                f.mapping_page = p
                p.is_allocated = True
                f.is_used = True
                break
        # 没有足够的帧，则发生页错误
        else:
            # 以下为LRU
            latest_time = 9999999
            process_to_replace = None
            # 先找到可以被置换的，最久没有使用的进程
            for process in process_q:
                if process.scheduled_info != [] and process.scheduled_info[-1][1] == 2:
                    # 只查找每个最近（列表最后一位）被暂停（元组第二位为2）的进程，因为只有这些进程被分配过内存，且没有正在运行

                    # 若一个进程所有的页已经被换出，则不必再考虑该进程
                    for page in process_to_replace.page_list:
                        if page.is_allocated:
                            break
                    else:
                        continue

                    if latest_time > process.scheduled_info[-1][0]:
                        latest_time = process.scheduled_info[-1][0]
                        process_to_replace = process
            # 进行页面置换
            replace_success_flag = False
            if process_to_replace is not None:
                for page in process_to_replace.page_list:
                    if page.is_allocated:
                        page.mapping_frame.mapping_page = p  # 帧映射到新页上
                        p.mapping_frame = page.mapping_frame  # 新页更新帧的映射关系
                        p.is_allocated = True
                        page.mapping_frame = None  # 被置换的页面取消映射关系
                        page.is_allocated = False
                        process_to_replace.page_all_allocated = False
                        replace_success_flag = True
            if not replace_success_flag:
                print("页置换错误!!!!")
