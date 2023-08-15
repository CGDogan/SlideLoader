# Utility that can be used to store and reuse JVMs (or BioFormatsThread)
# for each thread in a global variable
# Usage:
# from bfbridge.global_thread_manager import check_out_thread_local_object, save_thread_local_object
# bfthread = check_out_thread_local_object()
# if bfthread is None:
#     bfthread = BFThread()
#     save_thread_local_object(bfthread)
# <use bfthread>

# Advanced usage example with error handling:
# bfthread = check_out_thread_local_object()
# if bfthread is None:                        # When required, construct new
#     try:
#         bfthread_new = BFThread()
#     except Exception as f:
#         failure = f                         # Don't let the exception propagate until mutex is released
#         bfthread_new = None                 # Skip if cannot construct
#     save_thread_local_object(bfthread_new)  # Save or don't save, but release mutex
#     bfthread = bfthread_new
#
# if bfthread is None:
#     <display error and raise "failure" as exception>
# <use bfthread>

import threading

thread_to_object_dict = {}
thread_to_object_dict_lock = threading.Lock()

# Returns the thread local object if exists, otherwise returns None.
# If exists, no further action is required.
# IMPORTANT: If it does not, a mutex is held for the caller to construct and save an object.
# Hence in this case, the caller MUST call save_thread_local_object either 1) with an object
# to save it and release the lock 2) Or, with None, to release the lock without
# saving an object.
def check_out_thread_local_object():
    thread_id = threading.get_ident()
    thread_to_object_dict_lock.acquire()
    obj = thread_to_object_dict.get(thread_id)
    if obj is None:
        return None
    # release only if not None
    thread_to_object_dict_lock.release()
    return obj

# if obj is None: don't create, or delete dictionary entry
# Usecase 1: Delete the saved thread local object
# Usecase 2: To fulfill the requirement to finalize after
#   check_out_thread_local_object returns None 
def save_thread_local_object(obj):
    thread_id = threading.get_ident()
    if not thread_to_object_dict_lock.locked():
        thread_to_object_dict_lock.acquire()
    if obj is None:
        # delete if exists https://stackoverflow.com/q/15411107
        thread_to_object_dict.pop(thread_id, None)
    else:
        thread_to_object_dict[thread_id] = obj
    thread_to_object_dict_lock.release()
