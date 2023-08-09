from cffi import FFI
from pathlib import Path
import sys
import os

# API mode out-of-line
# https://cffi.readthedocs.io/en/latest/overview.html#purely-for-performance-api-level-out-of-line
# Please note: to ship with a JRE instead of a full JDK
# it might be necessary to cache the compiled output or use a
# different build mode
ffibuilder = FFI()

try:
    bfbridge_source = Path('bfbridge_basiclib.c').read_text()
    bfbridge_header = Path('bfbridge_basiclib.h').read_text()
    bfbridge_cffi_prefix = Path('bfbridge_cffi_prefix.h').read_text()
except:
    print("bfbridge_basiclib.c and/or bfbridge_basiclib.h and/or bfbridge_cffi_prefix.h could not be found")
    sys.exit(1)

header_begin = "CFFI HEADER BEGIN"
header_end = "CFFI HEADER END"

try:
    header_begin_index = bfbridge_header.index(header_begin)
    header_end_index = bfbridge_header.index(header_end)
except:
    print("bfbridge_basiclib.h CFFI markers could not be found")
    sys.exit(1)

# Fix header_begin_index: beginning from the middle of a "//"
# comment produces an invalid header.
header_begin_index = bfbridge_header.index("\n", header_begin_index)

bfbridge_header = bfbridge_header[header_begin_index:header_end_index]
bfbridge_header = bfbridge_cffi_prefix + "\n" + bfbridge_header


# https://stackoverflow.com/q/31795394
# ffibuilder.cdef, unlike set_source, does not
# call the compiler, but tries to parse it.
# Hence we can't use the standard header.

bfbridge_header = bfbridge_header.replace("BFBRIDGE_INLINE_ME_EXTRA", "").replace("BFBRIDGE_INLINE_ME", "").replace("#ifndef BFBRIDGE_KNOW_BUFFER_LEN", "").replace("#endif", "")

#print("Header: " + bfbridge_header)

ffibuilder.cdef(bfbridge_header)

# TODO DEBUG
os.environ["JAVA_HOME"] = "/Library/Java/JavaVirtualMachines/graalvm-community-openjdk-20.0.1+9.1/Contents/Home"

if "JAVA_HOME" not in os.environ:
    print("Please set JAVA_HOME to a JDK")
    sys.exit(1)

java_home = os.path.join(os.environ['JAVA_HOME'])
java_include = os.path.join(java_home, "include")
java_link = os.path.join(java_home, "lib/server")

# jni-md.h should also be included hence the platform paths, see link in https://stackoverflow.com/a/37029528
# https://github.com/openjdk/jdk/blob/6e3cc131daa9f3b883164333bdaad7aa3a6ca018/src/jdk.hotspot.agent/share/classes/sun/jvm/hotspot/utilities/PlatformInfo.java#L32
java_include = [java_include, os.path.join(java_include, "linux"), os.path.join(java_include, "darwin"), os.path.join(java_include, "win32"), os.path.join(java_include, "bsd")]

extra_link_args = []

if os.name != "nt":
    extra_link_args.append("-Wl,-rpath," + java_link) # libjvm.so
    extra_link_args.append("-Wl,-install_name,@rpath/libjvm.dylib") # libjvm.so

    # build fails without these when calling compiler manually
    # but somehow fails silently in this script.
    extra_link_args.append("-ljvm")
    extra_link_args.append("-L" + java_link)


# but compiling does call the compiler
ffibuilder.set_source("_bfbridge", bfbridge_source, extra_link_args=extra_link_args, include_dirs=java_include, libraries=[])

ffibuilder.compile(verbose=True)

from _bfbridge import ffi, lib
#import weakref
# global_weakkeydict = weakref.WeakKeyDictionary()

class BFBridgeThread:
    def __init__(self):
        self.bfbridge_library = ffi.new("bfbridge_library_t*")

        cpdir = os.environ.get("BFBRIDGE_CLASSPATH")
        if cpdir is None:
            print("Please set BFBRIDGE_CLASSPATH to a single dir containing the jar files")
            sys.exit(1)
        cpdir_arg = ffi.new("char[]", cpdir.encode())
        potential_error = lib.bfbridge_make_library(self.bfbridge_library, cpdir_arg, ffi.NULL)
        if potential_error != ffi.NULL:
            print(potential_error[0].description)
            sys.exit(1)

    # Before Python 3.4: https://stackoverflow.com/a/8025922
    # Now we can define __del__
    def __del__(self):
        print("destroying BFBridgeThread")
        lib.bfbridge_free_library(self.bfbridge_library)
        print("destroyinged BFBridgeThread")

# One instance can be used with the library object it was constructed with
class BFBridgeInstance:
    def __init__(self, bfbridge_thread):
        if bfbridge_thread is None:
            raise ValueError("BFBridgeInstance must be initialized with BFBridgeThread")

        self.bfbridge_library = bfbridge_thread.bfbridge_library
        self.bfbridge_instance = ffi.new("bfbridge_instance_t*")
        self.communication_buffer = ffi.new("char[34000000]")
        self.communication_buffer_len = 34000000
        potential_error = lib.bfbridge_make_instance(
            self.bfbridge_instance,
            self.bfbridge_library,
            self.communication_buffer,
            self.communication_buffer_len)
        if potential_error != ffi.NULL:
            print(potential_error[0].description)
            sys.exit(1)

    def __del__(self):
        print("destroying BFBridgeInstance")
        lib.bfbridge_free_instance(self.bfbridge_instance, self.bfbridge_library)
        print("destroyinged BFBridgeInstance")

    def __return_from_buffer(self, length, isString):
        if length < 0:
            print(self.get_error_string())
            length = 0
        data = ffi.buffer(self.communication_buffer, length)
        if isString:
            return str(data)
        else:
            return data

    def __boolean(self, integer):
        if integer == 1:
            return True
        elif integer == 0:
            return False
        else:
            # Error
            print(self.get_error_string())
            return False

    # Should be called only after the last method call returned an error code
    def get_error_string(self):
        length = lib.bf_get_error_length(self.bfbridge_instance, self.bfbridge_library)
        return self.__return_from_buffer(length, True)
    
    def is_compatible(self, filepath):
        filepath = filepath.encode()
        file = ffi.new("char[]", filepath)
        filepathlen = len(file)
        res = lib.bf_is_compatible(self.bfbridge_instance, self.bfbridge_library, filepath, filepathlen)
        return self.__boolean(res)
    
    def open(self, filepath):
        filepath = filepath.encode()
        file = ffi.new("char[]", filepath)
        filepathlen = len(file)
        res = lib.bf_open(self.bfbridge_instance, self.bfbridge_library, filepath, filepathlen)
        return res
    
    def close(self):
        return lib.bf_close(self.bfbridge_instance, self.bfbridge_library)

    def get_series_count(self):
        return lib.bf_get_series_count(self.bfbridge_instance, self.bfbridge_library)

    def set_current_series(self):
        return lib.bf_set_current_series(self.bfbridge_instance, self.bfbridge_library)
    
    def get_resolution_count(self):
        return lib.bf_get_resolution_count(self.bfbridge_instance, self.bfbridge_library)

    def set_current_resolution(self):
        return lib.bf_set_current_resolution(self.bfbridge_instance, self.bfbridge_library)
    
    def get_size_x(self):
        return lib.bf_get_size_x(self.bfbridge_instance, self.bfbridge_library)

    def get_size_y(self):
        return lib.bf_get_size_y(self.bfbridge_instance, self.bfbridge_library)

    def get_size_z(self):
        return lib.bf_get_size_z(self.bfbridge_instance, self.bfbridge_library)

    def get_size_c(self):
        return lib.bf_get_size_c(self.bfbridge_instance, self.bfbridge_library)

    def get_size_t(self):
        return lib.bf_get_size_t(self.bfbridge_instance, self.bfbridge_library)

    def get_effective_size_c(self):
        return lib.bf_get_effective_size_c(self.bfbridge_instance, self.bfbridge_library)

    def get_dimension_order(self):
        length = lib.bf_get_dimension_order(self.bfbridge_instance, self.bfbridge_library)
        return self.__return_from_buffer(length, True)

    def is_order_certain(self):
        return self.__boolean(lib.bf_is_order_certain(self.bfbridge_instance, self.bfbridge_library))

    def get_optimal_tile_width(self):
        return lib.bf_get_optimal_tile_width(self.bfbridge_instance, self.bfbridge_library)
    
    def get_optimal_tile_height(self):
        return lib.bf_get_optimal_tile_height(self.bfbridge_instance, self.bfbridge_library)
    
    def get_pixel_type(self):
        return lib.bf_get_optimal_tile_height(self.bfbridge_instance, self.bfbridge_library)
    
    def get_pixel_type(self):
        return lib.bf_get_pixel_type(self.bfbridge_instance, self.bfbridge_library)
    
    def get_bits_per_pixel(self):
        return lib.bf_get_bits_per_pixel(self.bfbridge_instance, self.bfbridge_library)

    def get_bytes_per_pixel(self):
        return lib.bf_get_bytes_per_pixel(self.bfbridge_instance, self.bfbridge_library)

    def get_rgb_channel_count(self):
        return lib.bf_get_rgb_channel_count(self.bfbridge_instance, self.bfbridge_library)

    def is_rgb(self):
        return self.__boolean(lib.bf_is_rgb(self.bfbridge_instance, self.bfbridge_library))

    def is_interleaved(self):
        return self.__boolean(lib.bf_is_interleaved(self.bfbridge_instance, self.bfbridge_library))
    
    def is_little_endian(self):
        return self.__boolean(lib.bf_is_little_endian(self.bfbridge_instance, self.bfbridge_library))

    def is_indexed_color(self):
        return self.__boolean(lib.bf_is_indexed_color(self.bfbridge_instance, self.bfbridge_library))
    
    def is_false_color(self):
        return self.__boolean(lib.bf_is_false_color(self.bfbridge_instance, self.bfbridge_library))
    
    # TODO return a 2D array
    def get_8_bit_lookup_table(self):
        return self.__return_from_buffer(lib.bf_get_8_bit_lookup_table(self.bfbridge_instance, self.bfbridge_library), False)
    
    # TODO return a 2D array
    def get_16_bit_lookup_table(self):
        return self.__return_from_buffer(lib.bf_get_8_bit_lookup_table(self.bfbridge_instance, self.bfbridge_library), False)
    
    # plane = 0 in general
    def open_bytes(self, plane, x, y, w, h):
        return self.__return_from_buffer(lib.bf_open_bytes(self.bfbridge_instance, self.bfbridge_library, plane, x, y, w, h), False)
    
    def get_mpp_x(self):
        return lib.bf_get_mpp_x(self.bfbridge_instance, self.bfbridge_library)
    
    def get_mpp_y(self):
        return lib.bf_get_mpp_y(self.bfbridge_instance, self.bfbridge_library)

    def get_mpp_z(self):
        return lib.bf_get_mpp_z(self.bfbridge_instance, self.bfbridge_library)
#result = lib.foo(buffer_in, buffer_out, 1000)

thre = BFBridgeThread()
inst = BFBridgeInstance(thre)
