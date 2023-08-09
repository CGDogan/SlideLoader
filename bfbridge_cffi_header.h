// CFFI header parser doesn't support ifdef
// which means that we can #include only consciously designed headers
// but CFFI it allows us to define opaque types:
// https://cffi.readthedocs.io/en/latest/cdef.html#letting-the-c-compiler-fill-the-gaps

// #define ABC ... for integers

// Normally constant are in:
// https://docs.oracle.com/en/java/javase/20/docs/specs/jni/functions.html#constants
// but we currently use just the following:

#define JNI_ERR ...
#define JNI_EDETACHED ...
#define JNI_EVERSION ...
#define JNI_ENOMEM ...
#define JNI_EEXIST ...
#define JNI_EINVAL ...

// Our macros
// Our library won't use header only mode with CFFI as it needs to include jvm.h
// #define BFBRIDGE_INLINE_ME
// #define BFBRIDGE_INLINE_ME_EXTRA
// EDIT: It seems that CFFI doesn't support function attribute macros
// even if it's empty. Find and replace from python.
// https://github.com/cffi/cffi/issues/367

// As the docs linked above says, typedef struct { ...; } foo_t; is an alternative
// but full opaqueness is fine for us.

typedef... JavaVM;
typedef... JNIEnv;
typedef... jclass;
typedef... jmethodID;
typedef... jobject;

// Include is not supported, so append to it from Python
// #include "bfbridge_header__inner.h"
