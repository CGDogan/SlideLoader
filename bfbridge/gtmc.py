import threading

thread_id_to_ref_count = {}
ref_count_lock = threading.Lock()

def change_ref_count(thread_id, add):
    ref_count_lock.acquire()
    new_ref_count = thread_id_to_ref_count.get(thread_id, 0) + add
    thread_id_to_ref_count[thread_id] = new_ref_count
    ref_count_lock.release()
    return new_ref_count
