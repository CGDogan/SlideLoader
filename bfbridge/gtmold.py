# Two shortcomings:
# 1 - threading.get_ident can reuse thread ID hence we aren't sure
#  if we do have a JVM for this thread or not
# 2 - keeping JVMs in a usual dictionary prevents them from being freed automatically
#  when a thread exits

# Utility that can be used to store and reuse JVMs (or BioFormatsThread)
# for each thread in a global variable
# Usage:
# from bfbridge.global_thread_manager import check_out_thread_local_object, save_thread_local_object
# thread_id = threading.get_ident()
# bfthread = check_out_thread_local_object(thread_id)
# if bfthread is None:
#     bfthread = BFThread()
#     save_thread_local_object(thread_id, bfthread)
# <use bfthread>

# Advanced usage example with error handling:
# thread_id = threading.get_ident()
# bfthread = check_out_thread_local_object(thread_id)
# if bfthread is None:                        # When required, construct new
#     try:
#         bfthread_new = BFThread()
#     except Exception as f:
#         failure = f                         # Don't let the exception propagate until mutex is released
#         bfthread_new = None                 # Skip if cannot construct
#     save_thread_local_object(thread_id, \   # Save or don't save, but release mutex
#       bfthread_new)
#     bfthread = bfthread_new
#
# if bfthread is None:
#     <display error and raise "failure" as exception>
# <use bfthread>

import threading

# What we need is keeping thread-local variables in a way that
# new threads that might even fork from it (https://stackoverflow.com/a/60807086)
# should not have access to it.
# Additionally, we need to keep data in a thread-local variable,
# which we don't here, so the user must free them or we'll have a memory leakage.

thread_to_object_dict = {}
thread_to_object_dict_lock = threading.Lock()

# Returns the thread local object if exists, otherwise returns None.
# If exists, no further action is required.
# IMPORTANT: If it does not, a mutex is held for the caller to construct and save an object.
# Hence in this case, the caller MUST call save_thread_local_object either 1) with an object
# to save it and release the lock 2) Or, with None, to release the lock without
# saving an object.
def check_out_thread_local_object(thread_id):
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
def save_thread_local_object(thread_id, obj):
    if not thread_to_object_dict_lock.locked():
        thread_to_object_dict_lock.acquire()
    if obj is None:
        # delete if exists https://stackoverflow.com/q/15411107
        thread_to_object_dict.pop(thread_id, None)
    else:
        thread_to_object_dict[thread_id] = obj
    thread_to_object_dict_lock.release()
