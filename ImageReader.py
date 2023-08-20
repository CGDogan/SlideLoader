# Please note: if you would like to import a specific reader,
# you should "import ImageReader" first, even if you won't use it,
# to avoid a cyclic dependency error

from abc import ABCMeta, abstractmethod

# Allow near drop-in replacements for OpenSlide-Python
class ImageReader(metaclass=ABCMeta):
    # currently: "openslide", "bioformats"
    @staticmethod
    @abstractmethod
    def reader_name():
        pass
    
    @staticmethod
    @abstractmethod
    def extensions_set():
        pass
    
    # Raises exception on error
    @abstractmethod
    def __init__(self):
        pass

    @property
    @abstractmethod
    def level_count(self):
        pass

    @property
    @abstractmethod
    def dimensions(self):
        pass

    @property
    @abstractmethod
    def level_dimensions(self):
        pass
    
    @abstractmethod
    def associated_images(self):
        pass

    @abstractmethod
    def read_region(self, location, level, size):
        pass

    @abstractmethod
    def get_thumbnail(self, max_size):
        pass

    # raises exception
    @abstractmethod
    def get_basic_metadata(self, extended):
        pass

from OpenSlideReader import OpenSlideReader
from BioFormatsReader import BioFormatsReader

# Decreasing order of importance
readers = [OpenSlideReader, BioFormatsReader]

# Replaces the constructor of the abstract class
# Usage:
# image = ImageReader.construct_reader("/file/path")
# Returns a reader
# Otherwise raises an object with attribute "error"
def construct_reader(imagepath):
    import threading
    for thread in threading.enumerate(): 
        print(thread.name)

    print("these are the threads", flush=True)
    print(threading.get_native_id())
    print(threading.get_ident())
    print("my thread^", flush=True)

    relevant_readers = []
    extension = imagepath.split(".")[-1].lower()

    print("starting readers loop,", flush=True)
    for r in readers:
        print("inloop1,", flush=True)
        print(r.reader_name, flush=True)
        print("inloop12", flush=True)
        print(r.extensions_set, flush=True)
        print(r.extensions_set(), flush=True)
        print(extension, flush=True)
        if extension in r.extensions_set:
            print("inloop2,", flush=True)
            relevant_readers.append(r)
    print("ending readers loop,", flush=True)
    if len(relevant_readers) == 0:
        raise RuntimeError({"error": "File extension unsupported, no readers are compatible"})

    image_type = []
    reader = None
    errors = []
    print("starting relevant_readers loop,", flush=True)
    for r in relevant_readers:
        try:
            reader = r(imagepath)
            break
        except Exception as e:
            image_type.append(r.reader_name)
            errors.append(r.reader_name + ": " + str(e))
            continue
    if reader is None:
        raise RuntimeError({"type": image_type.join(","), "error": errors.join(", ")})
    return reader
