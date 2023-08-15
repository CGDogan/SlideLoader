from abc import ABC, ABCMeta, abstractmethod

# Allow near drop-in replacements for OpenSlide-Python
class ImageReader(ABC, metaclass=ABCMeta):
    # currently: "openslide", "bioformats"
    @abstractmethod
    def reader_name(self):
        return None
    
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

import OpenSlideReader
import BioFormatsReader

readers = [OpenSlideReader.OpenSlideReader, BioFormatsReader.BioFormatsReader]

# Replaces the constructor of the abstract class
# Usage:
# from ImageReader import ImageReader
# image = ImageReader("/file/path")
# Returns a reader
# Returns None if no compatible reader was found
def ImageReader(imagepath):
    # Decreasing order of importance
    reader = None
    for r in readers:
        print("trying one")
        try:
            reader = r() # imagepath
        except Exception as e:
            print(e, flush="True")
            continue
        if reader is None:
            continue
    return reader
