# BFBRIDGE_CLASSPATH=/Users/zerf/Downloads/Github-repos/CGDogan/decoders/jar_files python3 testmutlithread.py

from bfbridge.global_thread_manager import get_thread_local_object, save_thread_local_object

from BioFormatsReader import BioFormatsReader

import threading

def add_to_global_var():
    x = BioFormatsReader("/Users/zerf/Downloads/Github-repos/CGDogan/camic-Distro/images/posdebugfiles_3.dcm")

threads = []

# Create 10 threads
for _ in range(10):
    t = threading.Thread(target=add_to_global_var)
    threads.append(t)
    t.start()

# Wait for all threads to complete
for t in threads:
    t.join()
