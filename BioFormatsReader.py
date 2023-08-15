import ImageReader
import bfbridge

BioFormatsThreadGlobal = bfbridge.BFBridgeThread()

class BioFormats(ImageReader):
    def reader_name(self):
        return "bioformats"

    # Pick the reader
    def __init__(self, imagepath):
        self.reader = bfbridge.BFBridgeInstance(self.reader)
        self.level_count = self.reader.get_resolution_count()
        self.dimensions = (self.reader.get_size_x(), self.reader.get_size_y())
        self.level_dimensions = [self.dimensions]
        for l in range(1, self.level_count):
            self.reader.set_current_resolution(l)
            self.level_dimensions.append( \
                (self.reader.get_size_x(), self.reader.get_size_y()))

    @property
    def level_count(self):
        return self.level_count

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
        return self.reader.open_thumb_bytes_pil_image(0, max_size[0], max_size[1])
