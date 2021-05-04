from PageAndFrame import *

Memory = [Frame(i) for i in range(100)]  # 默认内存有100个帧


def allocateMemory(pageList: list, process_q: list):
    for p in pageList:
        page_fault_flag = True
        for f in Memory:
            if not f.is_used:
                p.mapping_frame = f
                f.mapping_page = p
                f.is_used = True
                page_fault_flag = False
                break
        if page_fault_flag:
            pass
