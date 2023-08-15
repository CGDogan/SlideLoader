import openslide
import ImageReader

class OpenSlideReader(ImageReader.ImageReader):
    def reader_name(self):
        return "openslide"

    # Pick the reader
    def __init__(imagepath):
        self.reader = openslide.OpenSlide(imagepath)
    
    @property
    def level_count(self):
        return self.reader.level_count

    @property
    def dimensions(self):
        return self.reader.dimensions

    @property
    def level_dimensions(self):
        return self.reader.level_dimensions
    
    @property
    def associated_images(self):
        return self.reader.associated_images

    def read_region(self, location, level, size):
        return self.reader.read_region(location, level, size)
    
    def get_thumbnail(self, max_size):
        return self.reader.get_thumbnail(max_size)
