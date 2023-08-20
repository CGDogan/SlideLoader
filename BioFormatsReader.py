import ImageReader
import bfbridge
import threading
import dev_utils
import ome_types
from file_extensions import BIOFORMATS_EXTENSIONS
#from bfbridge.old_global_thread_manager import check_out_thread_local_object, save_thread_local_object, thread_to_object_dict_lock

jvm = bfbridge.BFBridgeVM()

# Try to keep BioFormats thread alive as long as possible
bfthread_holder = threading.local()

# todo deleteme 
import threading
class X:
    def __init__(self, s):
        self.x = s
    def __del__(self):
        print("dying thread " + self.x, flush=True)

l = threading.local()

class BioFormatsReader(ImageReader.ImageReader):
    @staticmethod
    def reader_name():
        return "bioformats"

    @staticmethod
    def extensions_set():
        return BIOFORMATS_EXTENSIONS

    # Pick the reader
    def __init__(self, imagepath):
        #self.__class__.l = threading.local()
        #self.__class__.l.a = X()
        global l
        if not hasattr(l, 'a'):
            l.a = X("now")
        if not hasattr(dev_utils.ll, "u"):
            dev_utils.ll.u = X("later?")

        print("__init__ called", flush=True)
        print("TrID instance:", flush=True)
        print(threading.get_native_id(), flush=True)
        # bfthread = get_thread_local_object()
        # if bfthread is None:
        #     # the following throws:
        #     bfthread = bfbridge.BFBridgeThread()
        #     save_thread_local_object(bfthread)
        #from threading import get_ident
        #import os
        #thread_id = os.getpid() #get_ident()
        # using getpid here caused having a new thread that wasn't attached
        #bfthread = check_out_thread_local_object(thread_id)
        # if bfthread is None:
        #     print("LOCK: none, now construct", flush=True)
        #     try:
        #         bfthread = bfbridge.BFBridgeThread(jvm)
        #         print("LOCK: constructed", flush=True)
        #     except Exception as f:
        #         failure = f
        #         print("LOCK: fail", flush=True)
        #         print(f)
        #     save_thread_local_object(thread_id, bfthread)
        #     print("LOCK: release")
        # else:
        #     print("LOCK: using")
        #     thread_to_object_dict_lock.acquire()
        global bfthread_holder

        if not hasattr(bfthread_holder, "bfthread"):
            bfthread_holder.bfthread = bfbridge.BFBridgeThread(jvm)

        # Conventionally internal attributes start with underscore.
        # When using them without underscore, there's the risk that
        # a property has the same name as a/the getter, which breaks
        # the abstract class. Hence all internal attributes start with underscore.
        self._bfreader = bfbridge.BFBridgeInstance(bfthread_holder.bfthread)
        if self._bfreader is None:
            raise RuntimeError("cannot make bioformats instance")
        print("__init__ called2", flush=True)
        self._image_path = imagepath
        code = self._bfreader.open(imagepath)
        if code < 0:
            raise IOError("Could not open file " + imagepath + ": " + self._bfreader.get_error_string())
        print("__init__ called3", flush=True)
        self._vendor = self._bfreader.get_format()
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

    def get_basic_metadata(self, extended):
        metadata = {}
        if not hasattr(self, "_md5"):
            self._md5 = dev_utils.file_md5(self._image_path)

        try:
            ome_xml = self._bfreader.dump_ome_xml_metadata()
        except BaseException as e:
            raise OverflowError("XML metadata too large for file considering the preallocated buffer length. " + str(e))
        print(ome_xml, flush=True)
        print("Starting metadata", flush=True)
        # TODO try except here IA
        try:
            ome_xml = ome_types.from_xml(ome_xml)
            print("continuing metadata", flush=True)

        except BaseException as e:
            raise RuntimeError("get_basic_metadata: OME-XML parsing of metadata failed, error: " + \
                str(e) + " when parsing: " + ome_xml)
        ome_xml.images[0]
        print(ome_xml.images[0], flush=True)
        # "comment" attribute of metadata
        print(str(ome_xml), flush=True)
        print("size")
        print(ome_xml.images[0].pixels.size_x, flush=True)
        print(ome_xml.images[0].pixels.size_y, flush=True)
        print(ome_xml.images[0].pixels.physical_size_x, flush=True)
        print(ome_xml.images[0].pixels.physical_size_y, flush=True)
        metadata['md5sum'] = self._md5
        metadata['width'] = str(self._dimensions[0])
        metadata['height'] = str(self._dimensions[1])
        try:
            metadata['mpp-x'] = str(ome_xml.images[0].pixels.physical_size_x)
            metadata['mpp-y'] = str(ome_xml.images[0].pixels.physical_size_y)
        except BaseException as e:
            metadata['mpp-x'] = "0"
            metadata['mpp-y'] = "0"
        metadata['vendor'] = self._vendor
        metadata['level_count'] = int(self._level_count)
        metadata['objective'] = ome_xml.instruments[0]
        
        # TODO IA: continue and complete
        # https://www.openmicroscopy.org/Schemas/Documentation/Generated/OME-2016-06/ome_xsd.html#Pixels_PhysicalSizeX
        # https://bio-formats.readthedocs.io/en/latest/metadata-summary.html objective


        

        # TODO IA: import ome-xml, dump xml, save xml IA, 
        # metadata['height']
        # metadata['width']
        # metadata['mpp-x']
        # metadata['mpp-y']
        # metadata['vendor']
        # metadata['level_count']
        # metadata['objective']
        #     or slideData.get("aperio.AppMag", -1.0))
        # metadata['comment']
        # metadata['study']
        # metadata['specimen']
        if not hasattr(self, "_metadata"):
            self._metadata = metadata
        return metadata

        