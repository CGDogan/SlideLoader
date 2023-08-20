import hashlib
import os
import json
import requests
import sys
import ImageReader

import openslide

post_url = "http://ca-back:4010/data/Slide/post"



# given a path, get metadata
# if raise_exception is false, returns an object with attribute "error"
def getMetadata(filepath, extended, raise_exception):
    print("getMetadata called", file=sys.stderr)
    # TODO consider restricting filepath
    metadata = {}
    if not os.path.isfile(filepath):
        msg = {"error": "No such file"}
        print(msg)
        return msg
    try:
        reader = ImageReader.ImageReader(filepath)
    except BaseException as e:
        if raise_exception:
            raise e
        # here, e has attribute "error"
        return str(e)
    return reader.get_basic_metadata(extended)


def postslide(img, url, token=''):
    if token != '':
        url = url + '?token='+token
    payload = json.dumps(img)
    res = requests.post(url, data=payload, headers={'content-type': 'application/json'})
    if res.status_code < 300:
        img['_status'] = 'success'
    else:
        img['_status'] = str(res.status_code)
    print('status ' + img['_status'])
    return img


# given a list of path, get metadata for each
def getMetadataList(filenames, extended, raise_exception):
    allData = []
    for filename in filenames:
        allData.append(getMetadata(filename, extended, raise_exception))
    return allData


def file_md5(fileName):
    m = hashlib.md5()
    blocksize = 2 ** 20
    with open(fileName, "rb") as f:
        while True:
            buf = f.read(blocksize)
            if not buf:
                break
            m.update(buf)
    return m.hexdigest()


def hello():
    print('hello!')
