import ImageReader
import bfbridge
from bfbridge.global_thread_manager import get_thread_local_object, save_thread_local_object

from BioFormatsReader import BioFormatsReader

# Modified from https://stackoverflow.com/a/60807086
# CC BY-SA 4.0. By FGreg on StackOverflow

import concurrent.futures
import multiprocessing
import threading

thread_data = threading.local()


def work():
    x = BioFormatsReader("/Users/zerf/Downloads/Github-repos/CGDogan/camic-Distro/images/posdebugfiles_3.dcm")
    print(x.level_count)

    print("[{}] [{}] {}".format(
        multiprocessing.current_process().name,
        threading.current_thread().getName(),
        getattr(thread_data, 'my_data', None)
    ), flush=True)


def main():
    thread_data.my_data = 'Data from {}'.format(multiprocessing.current_process().name)

    work()

    with concurrent.futures.ProcessPoolExecutor() as executor:
        futures = []
        for i in range(8):
            futures.append(executor.submit(work))
        for _ in concurrent.futures.as_completed(futures):
            print("[{}] [{}] Work done.".format(
                multiprocessing.current_process().name,
                threading.current_thread().getName()
            ), flush=True)


if __name__ == "__main__":
    main()