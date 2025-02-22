from ._bfbridge import ffi, lib
from PIL import Image
import numpy as np
import os
import sys
import threading
from . import gtmc

# channels = 3 or 4 supported currently
# interleaved: Boolean
# pixel_type: Integer https://github.com/ome/bioformats/blob/9cb6cfa/components/formats-api/src/loci/formats/FormatTools.java#L98
# interleaved: Boolean
# little_endian: Boolean
def make_pil_image( \
        byte_arr, width, height, channels, interleaved, bioformats_pixel_type, little_endian):
    if bioformats_pixel_type > 8 or bioformats_pixel_type < 0:
        raise ValueError("make_pil_image: pixel_type out of range")
    # https://github.com/ome/bioformats/blob/9cb6cfaaa5361bc/components/formats-api/src/loci/formats/FormatTools.java#L98
    if bioformats_pixel_type < 2:
        bytes_per_pixel_per_channel = 1
    elif bioformats_pixel_type < 4:
        bytes_per_pixel_per_channel = 2
    elif bioformats_pixel_type < 7:
        bytes_per_pixel_per_channel = 4
    elif bioformats_pixel_type < 8:
        bytes_per_pixel_per_channel = 8
    elif bioformats_pixel_type < 9:
        # a bit type has 1 bit per byte and handle this early
        if channels != 1:
            raise ValueError("make_pil_image: bit type (8) supported only for Black&White")
        arr = np.array(byte_arr)
        arr = np.reshape(arr, (height, width))
        return Image.fromarray(arr, mode="1")

    if channels != 3 and channels != 4:
        raise ValueError("make_pil_image: only 3 or 4 channels supported currently")
    
    if len(byte_arr) != width * height * channels * bytes_per_pixel_per_channel:
        raise ValueError(
            "make_pil_image: Expected " + width + " * " + \
            height + " * " + channels + " * " + \
            bytes_per_pixel_per_channel + " got " + len(byte_arr) + " bytes"
            )

    if bioformats_pixel_type == 0:
        np_dtype = np.int8
    elif bioformats_pixel_type == 1:
        np_dtype = np.uint8
    elif bioformats_pixel_type == 2:
        np_dtype = np.int16
    elif bioformats_pixel_type == 3:
        np_dtype = np.uint16
    elif bioformats_pixel_type == 4:
        np_dtype = np.int32
    elif bioformats_pixel_type == 5:
        np_dtype = np.uint32
    elif bioformats_pixel_type == 6:
        np_dtype = np.float32
    elif bioformats_pixel_type == 7:
        np_dtype = np.float64
    
    #arr = np.array(byte_arr, dtype=np_dtype)

    dt = np.dtype(np_dtype.__name__)
    dt = dt.newbyteorder("little" if little_endian else "big")
    arr = np.frombuffer(byte_arr, dtype=dt)

    # float type
    if bioformats_pixel_type == 6 or bioformats_pixel_type == 7:
        arr_min = np.min(arr)
        arr_max = np.max(arr)
        # check if not already normalized
        if arr_min < 0 or arr_max > 1:
            arr = (arr - arr_min) / (arr_max - arr_min)
        arr_min = 0
        arr_max = 1

    # https://pillow.readthedocs.io/en/latest/handbook/concepts.html#concept-modes
    # pillow doesn't support float64, trim to float32
    if bioformats_pixel_type == 7:
        arr = np.float32(arr)
        bioformats_pixel_type = 6
        bytes_per_pixel_per_channel = 4
    
    # interleave
    if not interleaved:
        # subarrays of length (len(arr)/channels)
        arr = np.reshape(arr, (-1, len(arr) // channels))
        arr = np.transpose(arr)
        # flatten. -1 means infer
        arr = np.reshape(arr, (-1))

    # now handle types 0 to 6

    # for signed int types, make them unsigned:
    if bioformats_pixel_type < 6 and ((bioformats_pixel_type & 1) == 0):
        # 128 for int8 etc.
        offset = -np.iinfo(arr.dtype).min
        arr = arr + offset
        if bioformats_pixel_type == 0:
            arr = np.uint8(arr)
        elif bioformats_pixel_type == 2:
            arr = np.uint16(arr)
        elif bioformats_pixel_type == 4:
            arr = np.uint32(arr)
        bioformats_pixel_type += 1

    # now handle types 1, 3, 5, 6

    # PIL supports only 8 bit
    # 32 bit -> 8 bit:
    if bioformats_pixel_type == 5:
        arr = np.float64(arr) / 65536 / 256
        arr = np.rint(arr)
        arr = np.uint8(arr)
        bioformats_pixel_type = 1
        bytes_per_pixel_per_channel = 1
    # 16 bit -> 8 bit:
    if bioformats_pixel_type == 3:
        arr = np.float32(arr) / 256
        arr = np.rint(arr)
        arr = np.uint8(arr)
        bioformats_pixel_type = 1
        bytes_per_pixel_per_channel = 1
    # float -> 8 bit
    if bioformats_pixel_type == 6:
        # numpy rint rounds to nearest even integer when ends in 0.5
        arr *= 255.4999
        arr = np.rint(arr)
        arr = np.uint8(arr)
        bioformats_pixel_type = 1
        bytes_per_pixel_per_channel = 1

    arr = np.reshape(arr, (height,width,channels))
    #https://pillow.readthedocs.io/en/latest/reference/Image.html#PIL.Image.fromarray
    return Image.fromarray(arr, mode="RGB")

# Can be created only once during a Python process lifetime and once it's destroyed
# it cannot be recreated
class BFBridgeVM:
    def __init__(self):
        self.bfbridge_vm =  ffi.new("bfbridge_vm_t*")
        cpdir = os.environ.get("BFBRIDGE_CLASSPATH")
        if cpdir is None or cpdir == "":
            raise RuntimeError("Please set BFBRIDGE_CLASSPATH env var to a single dir containing the jar files")
        cpdir_arg = ffi.new("char[]", cpdir.encode())

        cachedir = os.environ.get("BFBRIDGE_CACHEDIR")
        cachedir_arg = ffi.NULL
        if cachedir is not None and cachedir != "":
            cachedir_arg = ffi.new("char[]", cachedir.encode())

        potential_error = lib.bfbridge_make_vm(self.bfbridge_vm, cpdir_arg, cachedir_arg)
        if potential_error != ffi.NULL:
            err = ffi.string(potential_error[0].description)
            lib.bfbridge_free_error(potential_error)
            print(err, flush=True)
            raise RuntimeError(err)
        self.owner_pid = os.getpid()

    def __del__(self):
        # Additionally we can check if now it's the same pid that created this object
        if hasattr(self, "bfbridge_vm"):
            lib.bfbridge_free_vm(self.bfbridge_vm)

# You can create as many copies as needed in a single thread
class BFBridgeThread:
    def __init__(self, bfbridge_vm):
        if bfbridge_vm is None:
            raise ValueError("BFBridgeInstance must be initialized with BFBridgeThread")


        self.owner_pid = os.getpid()
        if bfbridge_vm.owner_pid != self.owner_pid:
            raise RuntimeError("JVM was created in a different process")

        self.bfbridge_thread = ffi.new("bfbridge_thread_t*")
        potential_error = lib.bfbridge_make_thread(self.bfbridge_thread, bfbridge_vm.bfbridge_vm)
        if potential_error != ffi.NULL:
            err = ffi.string(potential_error[0].description)
            lib.bfbridge_free_error(potential_error)
            print(err, flush=True)
            raise RuntimeError(err)
        self.owner_thread = threading.get_native_id()
        gtmc.change_ref_count(self.owner_thread, 1)

    def __copy__(self):
        raise RuntimeError("BFBridgeThread cannot be copied")

    def __deepcopy__(self):
        raise RuntimeError("BFBridgeThread cannot be copied")

    # Before Python 3.4: https://stackoverflow.com/a/8025922
    # Now we can define __del__
    def __del__(self):
        print("destroying BFBridgeThread")
        if gtmc.change_ref_count(self.owner_thread, -1) == 0:
            lib.bfbridge_free_thread(self.bfbridge_thread)
        print("destroyinged BFBridgeThread")

# An instance can be used with only the thread object it was constructed with
class BFBridgeInstance:
    def __init__(self, bfbridge_thread):
        print("About __init__ in __init__.py", flush=True)
        if bfbridge_thread is None:
            raise ValueError("BFBridgeInstance must be initialized with BFBridgeThread")

        self.owner_thread = threading.get_native_id()
        if bfbridge_thread.owner_thread != self.owner_thread:
            raise RuntimeError("BFBridgeInstance was supplied a bfbridge_thread from a different thread")

        self.bfbridge_thread = bfbridge_thread.bfbridge_thread
        self.bfbridge_instance = ffi.new("bfbridge_instance_t*")
        self.communication_buffer = ffi.new("char[34000000]")
        self.communication_buffer_len = 34000000
        print("About to make instance in __init__.py", flush=True)
        potential_error = lib.bfbridge_make_instance(
            self.bfbridge_instance,
            self.bfbridge_thread,
            self.communication_buffer,
            self.communication_buffer_len)
        print("Made instance in __init__.py", flush=True)
        if potential_error != ffi.NULL:
            err = ffi.string(potential_error[0].description)
            lib.bfbridge_free_error(potential_error)
            print(err, flush=True)
            raise RuntimeError(err)

    def __copy__(self):
        raise RuntimeError("Copying a BFBridgeInstance might not work")

    def __deepcopy__(self):
        raise RuntimeError("Copying a BFBridgeInstance might not work")

    def __del__(self):
        print("destroying BFBridgeInstance")
        if hasattr(self, "bfbridge_instance"):
            lib.bfbridge_free_instance(self.bfbridge_instance, self.bfbridge_thread)
        print("destroyinged BFBridgeInstance")

    def __return_from_buffer(self, length, isString):
        if length < 0:
            print(self.get_error_string())
            raise ValueError(self.get_error_string())
        if isString:
            return ffi.unpack(self.communication_buffer, length).decode("utf-8")
            # or ffi.string after if we set the null byte here
        else:
            return ffi.buffer(self.communication_buffer, length)

    def __boolean(self, integer):
        if integer == 1:
            return True
        elif integer == 0:
            return False
        else:
            # Error
            print(self.get_error_string())
            return False

    # Should be called only just after the last method call returned an error code
    def get_error_string(self):
        length = lib.bf_get_error_length(self.bfbridge_instance, self.bfbridge_thread)
        return self.__return_from_buffer(length, True)
    
    def is_compatible(self, filepath):
        filepath = filepath.encode()
        file = ffi.new("char[]", filepath)
        filepathlen = len(file) - 1
        res = lib.bf_is_compatible(self.bfbridge_instance, self.bfbridge_thread, filepath, filepathlen)
        return self.__boolean(res)
    
    def open(self, filepath):
        filepath = filepath.encode()
        file = ffi.new("char[]", filepath)
        filepathlen = len(file) - 1
        res = lib.bf_open(self.bfbridge_instance, self.bfbridge_thread, filepath, filepathlen)
        print(self.get_error_string(), flush=True)
        return res
    
    def get_format(self):
        length = lib.bf_get_format(self.bfbridge_instance, self.bfbridge_thread)
        return self.__return_from_buffer(length, True)

    def close(self):
        return lib.bf_close(self.bfbridge_instance, self.bfbridge_thread)

    def get_series_count(self):
        return lib.bf_get_series_count(self.bfbridge_instance, self.bfbridge_thread)

    def set_current_series(self, ser):
        return lib.bf_set_current_series(self.bfbridge_instance, self.bfbridge_thread, ser)
    
    def get_resolution_count(self):
        return lib.bf_get_resolution_count(self.bfbridge_instance, self.bfbridge_thread)

    def set_current_resolution(self, res):
        return lib.bf_set_current_resolution(self.bfbridge_instance, self.bfbridge_thread, res)
    
    def get_size_x(self):
        return lib.bf_get_size_x(self.bfbridge_instance, self.bfbridge_thread)

    def get_size_y(self):
        return lib.bf_get_size_y(self.bfbridge_instance, self.bfbridge_thread)

    def get_size_z(self):
        return lib.bf_get_size_z(self.bfbridge_instance, self.bfbridge_thread)

    def get_size_c(self):
        return lib.bf_get_size_c(self.bfbridge_instance, self.bfbridge_thread)

    def get_size_t(self):
        return lib.bf_get_size_t(self.bfbridge_instance, self.bfbridge_thread)

    def get_effective_size_c(self):
        return lib.bf_get_effective_size_c(self.bfbridge_instance, self.bfbridge_thread)

    def get_image_count(self):
        return lib.bf_get_image_count(self.bfbridge_instance, self.bfbridge_thread)

    def get_dimension_order(self):
        length = lib.bf_get_dimension_order(self.bfbridge_instance, self.bfbridge_thread)
        return self.__return_from_buffer(length, True)

    def is_order_certain(self):
        return self.__boolean(lib.bf_is_order_certain(self.bfbridge_instance, self.bfbridge_thread))

    def get_optimal_tile_width(self):
        return lib.bf_get_optimal_tile_width(self.bfbridge_instance, self.bfbridge_thread)
    
    def get_optimal_tile_height(self):
        return lib.bf_get_optimal_tile_height(self.bfbridge_instance, self.bfbridge_thread)
    
    def get_pixel_type(self):
        return lib.bf_get_optimal_tile_height(self.bfbridge_instance, self.bfbridge_thread)
    
    def get_pixel_type(self):
        return lib.bf_get_pixel_type(self.bfbridge_instance, self.bfbridge_thread)
    
    def get_bits_per_pixel(self):
        return lib.bf_get_bits_per_pixel(self.bfbridge_instance, self.bfbridge_thread)

    def get_bytes_per_pixel(self):
        return lib.bf_get_bytes_per_pixel(self.bfbridge_instance, self.bfbridge_thread)

    def get_rgb_channel_count(self):
        return lib.bf_get_rgb_channel_count(self.bfbridge_instance, self.bfbridge_thread)

    def is_rgb(self):
        return self.__boolean(lib.bf_is_rgb(self.bfbridge_instance, self.bfbridge_thread))

    def is_interleaved(self):
        return self.__boolean(lib.bf_is_interleaved(self.bfbridge_instance, self.bfbridge_thread))
    
    def is_little_endian(self):
        return self.__boolean(lib.bf_is_little_endian(self.bfbridge_instance, self.bfbridge_thread))

    def is_indexed_color(self):
        return self.__boolean(lib.bf_is_indexed_color(self.bfbridge_instance, self.bfbridge_thread))
    
    def is_false_color(self):
        return self.__boolean(lib.bf_is_false_color(self.bfbridge_instance, self.bfbridge_thread))
    
    # TODO return a 2D array, handle sign depending on pixel type
    def get_8_bit_lookup_table(self):
        return self.__return_from_buffer(lib.bf_get_8_bit_lookup_table(self.bfbridge_instance, self.bfbridge_thread), False)
    
    # TODO return a 2D array, handle endianness, handle sign depending on pixel type
    def get_16_bit_lookup_table(self):
        return self.__return_from_buffer(lib.bf_get_8_bit_lookup_table(self.bfbridge_instance, self.bfbridge_thread), False)
    
    # plane = 0 in general
    def open_bytes(self, plane, x, y, w, h):
        return self.__return_from_buffer(lib.bf_open_bytes(self.bfbridge_instance, self.bfbridge_thread, plane, x, y, w, h), False)

    def open_bytes_pil_image(self, plane, x, y, w, h):
        byte_arr = self.open_bytes(plane, x, y, w, h)
        return make_pil_image( \
            byte_arr, w, h, self.get_rgb_channel_count(), \
            self.is_interleaved(), self.get_pixel_type(), \
            self.is_little_endian())
    
    def open_thumb_bytes(self, plane, w, h):
        return self.__return_from_buffer( \
            lib.bf_open_thumb_bytes( \
            self.bfbridge_instance, self.bfbridge_thread, plane, w, h), False)
    
    def open_thumb_bytes_pil_image(self, plane, max_w, max_h):
        print("open_thumb_bytes")
        #print(*['{:40}| {}:{}\n'.format(x.function, x.filename, x.lineno) for x in inspect.stack()])
        print("MYLIBDEBUG open_thumb_bytes_pil_image " + str(max_w) + " " + str(max_h))
        img_h = self.get_size_y()
        img_w = self.get_size_x()
        y_over_x = img_h / img_w;
        x_over_y = 1 / y_over_x;
        w = min(max_w, round(max_h * x_over_y));
        h = min(max_h, round(max_w * y_over_x));
        if h > img_h or w > img_w:
            h = img_h
            w = img_w
        byte_arr = self.open_thumb_bytes(plane, w, h)
        print("open_thumb_bytes_pil_image byte array ")
        print(byte_arr)
        print(len(byte_arr))
        print(byte_arr[0])
        print(byte_arr[1])

        # Thumbnails can't be signed int in BioFormats
        pixel_type = self.get_pixel_type()
        if pixel_type == 0 or pixel_type == 2 or pixel_type == 4:
            pixel_type += 1

        return make_pil_image( \
            byte_arr, w, h, self.get_rgb_channel_count(), \
            self.is_interleaved(), pixel_type, \
            self.is_little_endian())

    def get_mpp_x(self, no):
        return lib.bf_get_mpp_x(self.bfbridge_instance, self.bfbridge_thread, no)
    
    def get_mpp_y(self, no):
        return lib.bf_get_mpp_y(self.bfbridge_instance, self.bfbridge_thread, no)

    def get_mpp_z(self, no):
        return lib.bf_get_mpp_z(self.bfbridge_instance, self.bfbridge_thread, no)

    def dump_ome_xml_metadata(self):
        length = lib.bf_dump_ome_xml_metadata(self.bfbridge_instance, self.bfbridge_thread)
        return self.__return_from_buffer(length, True)


# TODO Deleteme these
#thre = BFBridgeThread()
#inst = BFBridgeInstance(thre)
