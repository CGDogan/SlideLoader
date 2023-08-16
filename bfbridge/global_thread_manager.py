# Utility that can be used to store and reuse JVMs (or BioFormatsThread)
# for each thread in a global variable.
# Handles the case that fork() copies the address space; we shouldn't be
# tricked into thinking that we already have a JVM.

import threading

# What we need is keeping thread-local objects in a way that
# new threads that fork from it (https://stackoverflow.com/a/60807086)
# should not have access to it.
# For this, check the correct thread ID on every access.
# An alternative considered is using a custom class and implementing __copy__, __deepcopy__
# (https://stackoverflow.com/q/1500718) as delete, but I'm not sure if these are called
# when copying to a new thread.

# Using threading.local is beneficial as its contents are freed, including
# calling the JVM destructor automatically when the thread exits
# ----
# our thread_local_object attributes: .o for object and .id for thread id
# "->" represents "implies"
# State invariant: Either
# 1) .id defined and correct -> .o defined and correct
# meaning: ready for retrieval
# 2) .id defined but not correct -> .o defined but not correct
# 3) .id not defined -> .o not defined or is incorrect
# these last two cases mean that new object construction is needed
thread_local_object = threading.local()

# Returns the thread local object if exists, otherwise returns None.
def get_thread_local_object():
    if not hasattr(thread_local_object, "id") or \
        thread_local_object.id != threading.get_ident():
        # initialization needed
        return None
    else:
        return thread_local_object.o


# if obj is None: delete dictionary entry or don't create
def save_thread_local_object(obj):
    if obj is None:
        if hasattr(thread_local_object, "id"):
            del thread_local_object.id
    else:
        thread_local_object.id = threading.get_ident()
        thread_local_object.o = obj
