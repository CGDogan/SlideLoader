import ImageReader
import bfbridge
from bfbridge.global_thread_manager import get_thread_local_object, save_thread_local_object

class BioFormatsReader():
    def reader_name(self):
        return "bioformats"

    # Pick the reader
    def __init__(self, imagepath):
        print("__init__ called", flush=True)
        print("TrID instance:")
        #print(threading.get_ident(), flush=True)
        bfthread = get_thread_local_object()
        if bfthread is None:
            # the following throws:
            bfthread = bfbridge.BFBridgeThread()
            save_thread_local_object(bfthread)
        # Conventionally internal attributes start with underscore.
        # When using them without underscore, there's the risk that
        # a property has the same name as a/the getter, which breaks
        # the abstract class. Hence all internal attributes start with underscore.
        self._bfreader = bfbridge.BFBridgeInstance(bfthread)
        print("__init__ called2", flush=True)
        self._bfreader.open(imagepath)
        print("__init__ called3", flush=True)
        self._level_count = self._bfreader.get_resolution_count()
        self._dimensions = (self._bfreader.get_size_x(), self._bfreader.get_size_y())
        self._level_dimensions = [self._dimensions]
        for l in range(1, self._level_count):
            self._bfreader.set_current_resolution(l)
            self._level_dimensions.append( \
                (self._bfreader.get_size_x(), self._bfreader.get_size_y()))

    @property
    def level_count(self):
        return self._level_count

    @property
    def dimensions(self):
        return self._dimensions

    @property
    def level_dimensions(self):
        return self._level_dimensions
    
    @property
    def associated_images(self):
        return None

    def read_region(self, location, level, size):
        self._bfreader.set_current_resolution(level)
        return self._bfreader.open_bytes_pil_image(0, \
            location[0], location[1], size[0], size[1])

    def get_thumbnail(self, max_size):
        print("Starting BioFormatsReader get_thumbnail", flush=True)
        return self._bfreader.open_thumb_bytes_pil_image(0, max_size[0], max_size[1])

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