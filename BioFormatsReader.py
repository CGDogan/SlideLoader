import ImageReader
import bfbridge
from bfbridge.old_global_thread_manager import check_out_thread_local_object, save_thread_local_object, thread_to_object_dict_lock

jvm = bfbridge.BFBridgeVM()

class BioFormatsReader(ImageReader.ImageReader):
    def reader_name(self):
        return "bioformats"

    # Pick the reader
    def __init__(self, imagepath):
        print("__init__ called", flush=True)
        print("TrID instance:", flush=True)
        #print(threading.get_ident(), flush=True)
        # bfthread = get_thread_local_object()
        # if bfthread is None:
        #     # the following throws:
        #     bfthread = bfbridge.BFBridgeThread()
        #     save_thread_local_object(bfthread)
        from threading import get_ident
        import os
        thread_id = os.getpid() #get_ident()
        bfthread = check_out_thread_local_object(thread_id)
        if bfthread is None:
            print("LOCK: none, now construct")
            try:
                bfthread = bfbridge.BFBridgeThread(jvm)
                print("LOCK: constructed")
            except Exception as f:
                failure = f
                print("LOCK: fail")
                print(f)
            save_thread_local_object(thread_id, bfthread)
            print("LOCK: release")
        else:
            print("LOCK: using")
            thread_to_object_dict_lock.acquire()
        if bfthread is None:
            raise failure

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
