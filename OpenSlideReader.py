import openslide
import ImageReader
import dev_utils
from file_extensions import OPENSLIDE_EXTENSIONS

class OpenSlideReader(ImageReader.ImageReader):
    @property
    def reader_name(self):
        return "openslide"

    @property
    def extensions_set(self):
        return OPENSLIDE_EXTENSIONS

    # Pick the reader
    def __init__(self, imagepath):
        self._image_path = imagepath
        self._reader = openslide.OpenSlide(imagepath)
    
    @property
    def level_count(self):
        return self._reader.level_count

    @property
    def dimensions(self):
        return self._reader.dimensions

    @property
    def level_dimensions(self):
        return self._reader.level_dimensions
    
    @property
    def associated_images(self):
        return self._reader.associated_images

    def read_region(self, location, level, size):
        return self._reader.read_region(location, level, size)
    
    def get_thumbnail(self, max_size):
        return self._reader.get_thumbnail(max_size)
    
    def get_basic_metadata(self, extended):
        slideData = self._reader.properties
        if extended:
            metadata = {k:v for (k,v) in slideData.items()}
        else:
            metadata = {}
            metadata['mpp-x'] = slideData.get(openslide.PROPERTY_NAME_MPP_X, None)
            metadata['mpp-y'] = slideData.get(openslide.PROPERTY_NAME_MPP_Y, None)
            metadata['height'] = slideData.get(openslide.PROPERTY_NAME_BOUNDS_HEIGHT, None) \
                or slideData.get("openslide.level[0].height", None)
            metadata['width'] = slideData.get(openslide.PROPERTY_NAME_BOUNDS_WIDTH, None) \
                or slideData.get( "openslide.level[0].width", None)
            metadata['vendor'] = slideData.get(openslide.PROPERTY_NAME_VENDOR, None)
            metadata['level_count'] = int(self._reader.level_count)
            metadata['objective'] = float(slideData.get(openslide.PROPERTY_NAME_OBJECTIVE_POWER, 0) \
                or slideData.get("aperio.AppMag", -1.0))
            metadata['comment'] = slideData.get(openslide.PROPERTY_NAME_COMMENT, None)
            metadata['study'] = ""
            metadata['specimen'] = ""
        if not hasattr(self, "_md5"):
            self._md5 = dev_utils.file_md5(self._image_path)
        metadata['md5sum'] = self._md5
        return metadata
