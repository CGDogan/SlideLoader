# Please note: if you would like to import a specific reader,
# you should "import ImageReader" first, even if you won't use it,
# to avoid a cyclic dependency error

from abc import ABCMeta, abstractmethod

# Allow near drop-in replacements for OpenSlide-Python
class ImageReader(metaclass=ABCMeta):
    # currently: "openslide", "bioformats"
    @abstractmethod
    def reader_name(self):
        return None
    
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

    @abstractmethod
    def get_basic_metadata(self):
        pass

from OpenSlideReader import OpenSlideReader
from BioFormatsReader import BioFormatsReader

readers = [OpenSlideReader, BioFormatsReader]

# Replaces the constructor of the abstract class
# Usage:
# from ImageReader import ImageReader
# image = ImageReader("/file/path")
# Returns a reader
# Returns None if no compatible reader was found
def ImageReader(imagepath):
    import threading
    for thread in threading.enumerate(): 
        print(thread.name)

    print("these are the threads", flush=True)
    print(threading.get_native_id())
    print(threading.get_ident())
    print("my thread^", flush=True)
    # Decreasing order of importance
    reader = None
    for r in readers:
        print("trying one", flush=True)
        try:
            print("trying one0:", flush="True")
            reader = r(imagepath)
            print("trying one1:", flush="True")
        except Exception as e:
            print("See exception:", flush="True")
            print(e, flush="True")
            continue
    print("trying one3", flush=True)
    return reader
