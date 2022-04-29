import csv
import subprocess
import time
from multiprocessing.pool import ThreadPool

import openslide

from dev_utils import file_md5
from dev_utils import postslide
from dev_utils import post_url

# GLOBALS (for now)
config = {'thumbnail_size': 100, 'thread_limit': 20}
manifest_path = 'manifest.csv'
apiKey = '<apiKey>'

# process expects a single image metadata as dictionary
def process(img):
    try:
        img = openslidedata(img)
        img['study'] = img.get('study', "")
        img['specimen'] = img.get('specimen', "")
        img['location'] = img['location'] or img['filename']
        img = postslide(img, post_url, apiKey)
    except BaseException as e:
        img['_status'] = e
    return img


def gen_thumbnail(filename, slide, size, imgtype="png"):
    dest = filename + "." + imgtype
    print(dest)
    slide.get_thumbnail([size, size]).save(dest, imgtype.upper())


def openslidedata(metadata):
    slide = openslide.OpenSlide(metadata['location'])
    slideData = slide.properties
    metadata['mpp-x'] = slideData.get(openslide.PROPERTY_NAME_MPP_X, None)
    metadata['mpp-x'] = slideData.get(openslide.PROPERTY_NAME_MPP_Y, None)
    metadata['mpp'] = metadata['mpp-x'] or metadata['mpp-x'] or None
    # metadata['height'] = slideData.get("openslide.level[0].height", None)
    # metadata['width'] = slideData.get("openslide.level[0].width", None)
    metadata['height'] = slideData.get(openslide.PROPERTY_NAME_BOUNDS_HEIGHT, None)
    metadata['width'] = slideData.get(openslide.PROPERTY_NAME_BOUNDS_WIDTH, None)
    metadata['vendor'] = slideData.get(openslide.PROPERTY_NAME_VENDOR, None)
    metadata['level_count'] = int(slideData.get('level_count', 1))
    metadata['objective'] = float(slideData.get("aperio.AppMag", 0.0))
    metadata['md5sum'] = file_md5(metadata['location'])
    metadata['timestamp'] = time.time()
    thumbnail_size = config.get('thumbnail_size', None)
    if thumbnail_size:
        gen_thumbnail(metadata['location'], slide, thumbnail_size)
    return metadata

# get manifest
with open(manifest_path, 'r') as f:
    reader = csv.DictReader(f)
    manifest = [row for row in reader]
    thread_limit = config.get('thread_limit', 10)
    # run process on each image
    res = ThreadPool(thread_limit).imap_unordered(process, manifest)
    print([r for r in res])
