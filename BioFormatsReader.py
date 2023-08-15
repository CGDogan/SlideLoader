import ImageReader
import bfbridge
from bfbridge.global_thread_manager import check_out_thread_local_object, save_thread_local_object

# might need to be converted to a dict of threading.get_ident to BFBridgeThread
# with access trhough a mutex
##BioFormatsThreadGlobal = bfbridge.BFBridgeThread()
#print("TrID initialize:")
#print(threading.get_ident(), flush=True)

class BioFormatsReader(ImageReader.ImageReader):
    def reader_name(self):
        return "bioformats"

    # Pick the reader
    def __init__(self, imagepath):
        print("__init__ called", flush=True)
        print("TrID instance:")
        #print(threading.get_ident(), flush=True)
        bfthread = check_out_thread_local_object()
        if bfthread is None:
            try:
                bfthread = bfbridge.BFBridgeThread()
            except Exception as f:
                failure = f
            save_thread_local_object(bfthread)
        if bfthread is None:
            raise failure
        self.reader = bfbridge.BFBridgeInstance(bfthread)
        print("__init__ called2", flush=True)
        self.reader.open(imagepath)
        print("__init__ called3", flush=True)
        self.level_count_ = self.reader.get_resolution_count()
        self.dimensions = (self.reader.get_size_x(), self.reader.get_size_y())
        self.level_dimensions = [self.dimensions]
        for l in range(1, self.level_count_):
            self.reader.set_current_resolution(l)
            self.level_dimensions.append( \
                (self.reader.get_size_x(), self.reader.get_size_y()))

    @property
    def level_count(self):
        return self.level_count_

    @property
    def dimensions(self):
        return self.dimensions

    @property
    def level_dimensions(self):
        return self.level_dimensions
    
    @property
    def associated_images(self):
        return None

    def read_region(self, location, level, size):
        self.reader.set_current_resolution(level)
        return self.reader.open_bytes_pil_image(0, \
            location[0], location[1], size[0], size[1])

    def get_thumbnail(self, max_size):
        print("Starting BioFormatsReader get_thumbnail", flush=True)
        return self.reader.open_thumb_bytes_pil_image(0, max_size[0], max_size[1])
