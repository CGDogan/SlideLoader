// TODO: To be moved to decoders directory

/*
 * File:     bfbridge_basiclib.h
 * Also see: BioFormatsThread.h in github.com/camicroscope/iipImage
 */

// Optionally define: BFBRIDGE_INLINE (makes it a header-only library)
// Please note: in this case you're encouraged to call bfbridge_make_library
// and bfbridge_make_library from a single compilation unit only to save from
// final executable size, or wrap it around a non-static caller which
// you can call from multiple files
// Please note: The best way to define BFBRIDGE_INLINE is through the flag
// -DBFBRIDGE_INLINE but it also works speed-wise to #define BFBRIDGE_INLINE
// before you include it.

// Optionally define: BFBRIDGE_KNOW_BUFFER_LEN
// This will save some memory by not storing buffer length in our structs.

#ifndef BFBRIDGE_BASICLIB_H
#define BFBRIDGE_BASICLIB_H

#include <jni.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifdef BFBRIDGE_INLINE
#define BFBRIDGE_INLINE_ME_EXTRA static
#else
#define BFBRIDGE_INLINE_ME_EXTRA
#endif

// As an example, inlining solves the issue that
// passing struct ptrs requires dereference https://stackoverflow.com/a/552250
// so without inline, we would need to pass instance pointers by value
#ifdef BFBRIDGE_INLINE
#define BFBRIDGE_INLINE_ME static inline
#else
#define BFBRIDGE_INLINE_ME
#endif

// IMPORTANT: This is the documentation header file that you should read
#include "bfbridge_header_inner.h"

/*
How is the communication buffer used internally?
Some functions receive from BioFormats through the communication buffer
Some functions communicate to BioFormats (such as passing a filename) through it
Some functions don't use the buffer at all
bf_open_bytes, for example, that reads a region to bytes,
receives bytes to the communication buffer. Returns an int,
bytes to be read, which then the user of the library should read from the buffer.
 */

#ifdef BFBRIDGE_INLINE
#define BFBRIDGE_HEADER
#include "bfbridge_basiclib.c"
#undef BFBRIDGE_HEADER
#endif

#ifdef __cplusplus
} // extern "C"
#endif

#endif // BFBRIDGE_BASICLIB_H
