# The MIT License (MIT)
#
# Copyright (c) 2014-2015 WUSTL ZPLAB
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Authors: Zach Pincus

import ctypes
import numpy
import sys
import os.path
import glob
from numpy.compat import asbytes, asstr

__all__ = ['read', 'read_multipage', 'read_metadata', 'read_multipage_metadata',
    'write', 'write_multipage', 'IO_FLAGS', 'METADATA_MODELS']


def load_freeimage():
    if sys.platform == 'win32':
        loader = ctypes.windll
        functype = ctypes.WINFUNCTYPE
    else:
        loader = ctypes.cdll
        functype = ctypes.CFUNCTYPE

    freeimage = None
    errors = []
    possible_freeimage_libs = glob.glob(os.path.join(os.path.dirname(__file__), '_freeimage.*'))
    for lib in possible_freeimage_libs:
        try:
            freeimage = loader.LoadLibrary(lib)
            break
        except Exception:
            # Get exception instance in Python 2.x/3.x compatible manner
            e_type, e_value, e_tb = sys.exc_info()
            del e_tb
            errors.append((lib, e_value))

    if freeimage is None:
        if errors:
            # No freeimage library loaded, and load-errors reported for some
            # candidate libs
            err_txt = ['%s:\n%s' % (l, str(e.args[0])) for l, e in errors]
            raise RuntimeError('One or more FreeImage libraries were found, but '
                               'could not be loaded due to the following errors:\n'
                               '\n\n'.join(err_txt))
        else:
            # No errors, because no potential libraries found at all!
            raise RuntimeError('Could not find a FreeImage library in any of:\n' +
                               '\n'.join(lib_dirs))

    # FreeImage found
    @functype(None, ctypes.c_int, ctypes.c_char_p)
    def error_handler(fif, message):
        raise RuntimeError('FreeImage error: %s' % message)

    freeimage.FreeImage_SetOutputMessage(error_handler)
    return freeimage

_FI = load_freeimage()

API = {
    # All we're doing here is telling ctypes that some of the FreeImage
    # functions return pointers instead of integers. (On 64-bit systems,
    # without this information the pointers get truncated and crashes result).
    # There's no need to list functions that return ints, or the types of the
    # parameters to these or other functions -- that's fine to do implicitly.

    # Note that the ctypes immediately converts the returned void_p back to a
    # python int again! This is really not helpful, because then passing it
    # back to another library call will cause truncation-to-32-bits on 64-bit
    # systems. Thanks, ctypes! So after these calls one must immediately
    # re-wrap the int as a c_void_p if it is to be passed back into FreeImage.
    'FreeImage_AllocateT': (ctypes.c_void_p, None),
    'FreeImage_FindFirstMetadata': (ctypes.c_void_p, None),
    'FreeImage_GetBits': (ctypes.c_void_p, None),
    'FreeImage_GetPalette': (ctypes.c_void_p, None),
    'FreeImage_GetTagKey': (ctypes.c_char_p, None),
    'FreeImage_GetTagValue': (ctypes.c_void_p, None),
    'FreeImage_Load': (ctypes.c_void_p, None),
    'FreeImage_LockPage': (ctypes.c_void_p, None),
    'FreeImage_OpenMultiBitmap': (ctypes.c_void_p, None)
    }

# Albert's ctypes pattern


def register_api(lib, api):
    for f, (restype, argtypes) in api.items():
        func = getattr(lib, f)
        func.restype = restype
        func.argtypes = argtypes

register_api(_FI, API)


class FI_TYPES(object):
    FIT_UNKNOWN = 0
    FIT_BITMAP = 1
    FIT_UINT16 = 2
    FIT_INT16 = 3
    FIT_UINT32 = 4
    FIT_INT32 = 5
    FIT_FLOAT = 6
    FIT_DOUBLE = 7
    FIT_COMPLEX = 8
    FIT_RGB16 = 9
    FIT_RGBA16 = 10
    FIT_RGBF = 11
    FIT_RGBAF = 12

    dtypes = {
        FIT_BITMAP: numpy.uint8,
        FIT_UINT16: numpy.uint16,
        FIT_INT16: numpy.int16,
        FIT_UINT32: numpy.uint32,
        FIT_INT32: numpy.int32,
        FIT_FLOAT: numpy.float32,
        FIT_DOUBLE: numpy.float64,
        FIT_COMPLEX: numpy.complex128,
        FIT_RGB16: numpy.uint16,
        FIT_RGBA16: numpy.uint16,
        FIT_RGBF: numpy.float32,
        FIT_RGBAF: numpy.float32
        }

    fi_types = {
        (numpy.dtype('uint8'), 1): FIT_BITMAP,
        (numpy.dtype('uint8'), 3): FIT_BITMAP,
        (numpy.dtype('uint8'), 4): FIT_BITMAP,
        (numpy.dtype('uint16'), 1): FIT_UINT16,
        (numpy.dtype('int16'), 1): FIT_INT16,
        (numpy.dtype('uint32'), 1): FIT_UINT32,
        (numpy.dtype('int32'), 1): FIT_INT32,
        (numpy.dtype('float32'), 1): FIT_FLOAT,
        (numpy.dtype('float64'), 1): FIT_DOUBLE,
        (numpy.dtype('complex128'), 1): FIT_COMPLEX,
        (numpy.dtype('uint16'), 3): FIT_RGB16,
        (numpy.dtype('uint16'), 4): FIT_RGBA16,
        (numpy.dtype('float32'), 3): FIT_RGBF,
        (numpy.dtype('float32'), 4): FIT_RGBAF
        }

    extra_dims = {
        FIT_UINT16: [],
        FIT_INT16: [],
        FIT_UINT32: [],
        FIT_INT32: [],
        FIT_FLOAT: [],
        FIT_DOUBLE: [],
        FIT_COMPLEX: [],
        FIT_RGB16: [3],
        FIT_RGBA16: [4],
        FIT_RGBF: [3],
        FIT_RGBAF: [4]
        }

    @classmethod
    def get_type_and_shape(cls, bitmap):
        w = _FI.FreeImage_GetWidth(bitmap)
        h = _FI.FreeImage_GetHeight(bitmap)
        fi_type = _FI.FreeImage_GetImageType(bitmap)
        if not fi_type:
            raise ValueError('Unknown image pixel type')
        dtype = cls.dtypes[fi_type]
        if fi_type == cls.FIT_BITMAP:
            bpp = _FI.FreeImage_GetBPP(bitmap)
            if bpp == 8:
                extra_dims = []
            elif bpp == 24:
                extra_dims = [3]
            elif bpp == 32:
                extra_dims = [4]
            else:
                raise ValueError('Cannot convert %d BPP bitmap' % bpp)
        else:
            extra_dims = cls.extra_dims[fi_type]
        return numpy.dtype(dtype), [w, h] + extra_dims


class IO_FLAGS(object):
    FIF_LOAD_NOPIXELS = 0x8000  # loading: load the image header only
                                # (not supported by all plugins)

    BMP_DEFAULT = 0
    BMP_SAVE_RLE = 1
    CUT_DEFAULT = 0
    DDS_DEFAULT = 0
    FAXG3_DEFAULT = 0
    GIF_DEFAULT = 0
    GIF_LOAD256 = 1  # Load the image as a 256 color image with ununsed
                     # palette entries, if it's 16 or 2 color
    GIF_PLAYBACK = 2  # 'Play' the GIF to generate each frame (as 32bpp)
                      # instead of returning raw frame data when loading
    HDR_DEFAULT = 0
    ICO_DEFAULT = 0
    ICO_MAKEALPHA = 1  # convert to 32bpp and create an alpha channel from the
                       # AND-mask when loading
    IFF_DEFAULT = 0
    JPEG_DEFAULT = 0  # loading (see JPEG_FAST);
                      # saving (see JPEG_QUALITYGOOD|JPEG_SUBSAMPLING_420)
    JPEG_FAST = 0x0001  # load the file as fast as possible,
                        # sacrificing some quality
    JPEG_ACCURATE = 0x0002  # load the file with the best quality,
                            # sacrificing some speed
    JPEG_CMYK = 0x0004  # load separated CMYK "as is"
                        # (use | to combine with other load flags)
    JPEG_EXIFROTATE = 0x0008  # load and rotate according to
                              # Exif 'Orientation' tag if available
    JPEG_QUALITYSUPERB = 0x80  # save with superb quality (100:1)
    JPEG_QUALITYGOOD = 0x0100  # save with good quality (75:1)
    JPEG_QUALITYNORMAL = 0x0200  # save with normal quality (50:1)
    JPEG_QUALITYAVERAGE = 0x0400  # save with average quality (25:1)
    JPEG_QUALITYBAD = 0x0800  # save with bad quality (10:1)
    JPEG_PROGRESSIVE = 0x2000  # save as a progressive-JPEG
                               # (use | to combine with other save flags)
    JPEG_SUBSAMPLING_411 = 0x1000  # save with high 4x1 chroma
                                   # subsampling (4:1:1)
    JPEG_SUBSAMPLING_420 = 0x4000  # save with medium 2x2 medium chroma
                                   # subsampling (4:2:0) - default value
    JPEG_SUBSAMPLING_422 = 0x8000  # save with low 2x1 chroma subsampling (4:2:2)
    JPEG_SUBSAMPLING_444 = 0x10000  # save with no chroma subsampling (4:4:4)
    JPEG_OPTIMIZE = 0x20000  # on saving, compute optimal Huffman coding tables
                             # (can reduce a few percent of file size)
    JPEG_BASELINE = 0x40000  # save basic JPEG, without metadata or any markers
    KOALA_DEFAULT = 0
    LBM_DEFAULT = 0
    MNG_DEFAULT = 0
    PCD_DEFAULT = 0
    PCD_BASE = 1  # load the bitmap sized 768 x 512
    PCD_BASEDIV4 = 2  # load the bitmap sized 384 x 256
    PCD_BASEDIV16 = 3  # load the bitmap sized 192 x 128
    PCX_DEFAULT = 0
    PFM_DEFAULT = 0
    PICT_DEFAULT = 0
    PNG_DEFAULT = 0
    PNG_IGNOREGAMMA = 1  # loading: avoid gamma correction
    PNG_Z_BEST_SPEED = 0x0001  # save using ZLib level 1 compression flag
                               # (default value is 6)
    PNG_Z_DEFAULT_COMPRESSION = 0x0006  # save using ZLib level 6 compression
                                        # flag (default recommended value)
    PNG_Z_BEST_COMPRESSION = 0x0009  # save using ZLib level 9 compression flag
                                     # (default value is 6)
    PNG_Z_NO_COMPRESSION = 0x0100  # save without ZLib compression
    PNG_INTERLACED = 0x0200  # save using Adam7 interlacing (use | to combine
                             # with other save flags)
    PNM_DEFAULT = 0
    PNM_SAVE_RAW = 0  # Writer saves in RAW format (i.e. P4, P5 or P6)
    PNM_SAVE_ASCII = 1  # Writer saves in ASCII format (i.e. P1, P2 or P3)
    PSD_DEFAULT = 0
    PSD_CMYK = 1  # reads tags for separated CMYK (default is conversion to RGB)
    PSD_LAB = 2  # reads tags for CIELab (default is conversion to RGB)
    RAS_DEFAULT = 0
    SGI_DEFAULT = 0
    TARGA_DEFAULT = 0
    TARGA_LOAD_RGB888 = 1  # Convert RGB555 and ARGB8888 -> RGB888.
    TARGA_SAVE_RLE = 2  # Save with RLE compression
    TIFF_DEFAULT = 0
    TIFF_CMYK = 0x0001  # reads/stores tags for separated CMYK
                        # (use | to combine with compression flags)
    TIFF_PACKBITS = 0x0100  # save using PACKBITS compression
    TIFF_DEFLATE = 0x0200  # save using DEFLATE (a.k.a. ZLIB) compression
    TIFF_ADOBE_DEFLATE = 0x0400  # save using ADOBE DEFLATE compression
    TIFF_NONE = 0x0800  # save without any compression
    TIFF_CCITTFAX3 = 0x1000  # save using CCITT Group 3 fax encoding
    TIFF_CCITTFAX4 = 0x2000  # save using CCITT Group 4 fax encoding
    TIFF_LZW = 0x4000  # save using LZW compression
    TIFF_JPEG = 0x8000  # save using JPEG compression
    TIFF_LOGLUV = 0x10000  # save using LogLuv compression
    WBMP_DEFAULT = 0
    XBM_DEFAULT = 0
    XPM_DEFAULT = 0


class METADATA_MODELS(object):
    FIMD_COMMENTS = 0
    FIMD_EXIF_MAIN = 1
    FIMD_EXIF_EXIF = 2
    FIMD_EXIF_GPS = 3
    FIMD_EXIF_MAKERNOTE = 4
    FIMD_EXIF_INTEROP = 5
    FIMD_IPTC = 6
    FIMD_XMP = 7
    FIMD_GEOTIFF = 8
    FIMD_ANIMATION = 9


class METADATA_DATATYPE(object):
    FIDT_BYTE = 1  # 8-bit unsigned integer
    FIDT_ASCII = 2  # 8-bit bytes w/ last byte null
    FIDT_SHORT = 3  # 16-bit unsigned integer
    FIDT_LONG = 4  # 32-bit unsigned integer
    FIDT_RATIONAL = 5  # 64-bit unsigned fraction
    FIDT_SBYTE = 6  # 8-bit signed integer
    FIDT_UNDEFINED = 7  # 8-bit untyped data
    FIDT_SSHORT = 8  # 16-bit signed integer
    FIDT_SLONG = 9  # 32-bit signed integer
    FIDT_SRATIONAL = 10  # 64-bit signed fraction
    FIDT_FLOAT = 11  # 32-bit IEEE floating point
    FIDT_DOUBLE = 12  # 64-bit IEEE floating point
    FIDT_IFD = 13  # 32-bit unsigned integer (offset)
    FIDT_PALETTE = 14  # 32-bit RGBQUAD
    FIDT_LONG8 = 16  # 64-bit unsigned integer
    FIDT_SLONG8 = 17  # 64-bit signed integer
    FIDT_IFD8 = 18  # 64-bit unsigned integer (offset)

    dtypes = {
        FIDT_BYTE: numpy.uint8,
        FIDT_SHORT: numpy.uint16,
        FIDT_LONG: numpy.uint32,
        FIDT_RATIONAL: [('numerator', numpy.uint32),
                        ('denominator', numpy.uint32)],
        FIDT_SBYTE: numpy.int8,
        FIDT_UNDEFINED: numpy.uint8,
        FIDT_SSHORT: numpy.int16,
        FIDT_SLONG: numpy.int32,
        FIDT_SRATIONAL: [('numerator', numpy.int32),
                         ('denominator', numpy.int32)],
        FIDT_FLOAT: numpy.float32,
        FIDT_DOUBLE: numpy.float64,
        FIDT_IFD: numpy.uint32,
        FIDT_PALETTE: [('R', numpy.uint8), ('G', numpy.uint8),
                       ('B', numpy.uint8), ('A', numpy.uint8)],
        FIDT_LONG8: numpy.uint64,
        FIDT_SLONG8: numpy.int64,
        FIDT_IFD8: numpy.uint64
        }


def _process_bitmap(filename, flags, process_func):
    filename = asbytes(filename)
    ftype = _FI.FreeImage_GetFileType(filename, 0)
    if ftype == -1:
        raise ValueError('Cannot determine type of file %s' % filename)
    bitmap = _FI.FreeImage_Load(ftype, filename, flags)
    bitmap = ctypes.c_void_p(bitmap)
    if not bitmap:
        raise ValueError('Could not load file %s' % filename)
    try:
        return process_func(bitmap)
    finally:
        _FI.FreeImage_Unload(bitmap)


def read(filename, flags=0):
    """Read an image to a numpy array of shape (width, height) for
    greyscale images, or shape (width, height, nchannels) for RGB or
    RGBA images.
    The `flags` parameter should be one or more values from the IO_FLAGS
    class defined in this module, or-ed together with | as appropriate.
    (See the source-code comments for more details.)
    """
    return _process_bitmap(filename, flags, _array_from_bitmap)


def read_metadata(filename):
    """Return a dict containing all image metadata.

    Returned dict maps (metadata_model, tag_name) keys to tag values, where
    metadata_model is a string name based on the FreeImage "metadata models"
    defined in the class METADATA_MODELS.
    """
    flags = IO_FLAGS.FIF_LOAD_NOPIXELS
    return _process_bitmap(filename, flags, _read_metadata)


def _process_multipage(filename, flags, process_func):
    filename = asbytes(filename)
    ftype = _FI.FreeImage_GetFileType(filename, 0)
    if ftype == -1:
        raise ValueError('Cannot determine type of file %s' % filename)
    create_new = False
    read_only = True
    keep_cache_in_memory = True
    multibitmap = _FI.FreeImage_OpenMultiBitmap(ftype, filename, create_new,
                                                read_only, keep_cache_in_memory,
                                                flags)
    multibitmap = ctypes.c_void_p(multibitmap)
    if not multibitmap:
        raise ValueError('Could not open %s as multi-page image.' % filename)
    try:
        pages = _FI.FreeImage_GetPageCount(multibitmap)
        out = []
        for i in range(pages):
            bitmap = _FI.FreeImage_LockPage(multibitmap, i)
            bitmap = ctypes.c_void_p(bitmap)
            if not bitmap:
                raise ValueError('Could not open %s as a multi-page image.'
                                  % filename)
            try:
                out.append(process_func(bitmap))
            finally:
                _FI.FreeImage_UnlockPage(multibitmap, bitmap, False)
        return out
    finally:
        _FI.FreeImage_CloseMultiBitmap(multibitmap, 0)


def read_multipage(filename, flags=0):
    """Read a multipage image to a list of numpy arrays, where each
    array is of shape (width, height) for greyscale images, or shape
    (width, height, nchannels) for RGB or RGBA images.
    The `flags` parameter should be one or more values from the IO_FLAGS
    class defined in this module, or-ed together with | as appropriate.
    (See the source-code comments for more details.)
    """
    return _process_multipage(filename, flags, _array_from_bitmap)


def read_multipage_metadata(filename):
    """Read a multipage image to a list of metadata dicts, one dict for each
    page. The dict format is as in read_metadata().
    """
    flags = IO_FLAGS.FIF_LOAD_NOPIXELS
    return _process_multipage(filename, flags, _read_metadata)


def _wrap_bitmap_bits_in_array(bitmap, shape, dtype):
    """Return an ndarray view on the data in a FreeImage bitmap. Only
    valid for as long as the bitmap is loaded (if single page) / locked
    in memory (if multipage).
    Shape is interpreted as (width, height) or (width, height, nchannels).
    """
    pitch = _FI.FreeImage_GetPitch(bitmap)
    height = shape[1]
    byte_size = height * pitch
    itemsize = dtype.itemsize

    # We're going to use a negative pitch for the stride in the y-direction
    # because FreeImage stores images "upside down" with the first scanline
    # being the bottom of the image. So we'll create an array that just indexes
    # backwards. (This is basically what ::-1 on that axis would do anyway.)
    if len(shape) == 3:
        nchannels = shape[2]
        strides = (nchannels * itemsize, -pitch, itemsize)
    else:
        strides = (itemsize, -pitch)
    bits = _FI.FreeImage_GetBits(bitmap)
    # NB: 'offset' is provided as the start of the last scanline. This way,
    # we start at the top of the image and work our way back down using the
    # negative stride for 'pitch'
    array = numpy.ndarray(shape, dtype=dtype,
                          buffer=(ctypes.c_char * byte_size).from_address(bits),
                          strides=strides, offset=pitch*(height-1))
    return array


def _array_from_bitmap(bitmap):
    """Convert a FreeImage bitmap pointer to a numpy array.
    """
    dtype, shape = FI_TYPES.get_type_and_shape(bitmap)
    array = _wrap_bitmap_bits_in_array(bitmap, shape, dtype)
    # FreeImage uses BGR[A] pixel layout on little-endian systems. Convert to RGB[A].
    if len(shape) == 3 and _FI.FreeImage_IsLittleEndian() and dtype.type == numpy.uint8:
        b = array[:, :, 0].copy()
        array[:, :, 0] = array[:, :, 2]
        array[:, :, 2] = b

    # We need to copy because array does *not* own its memory after bitmap is freed.
    # Use order='k' to keep strides. This way the in-memory layout will be
    # the traditional scanlines-of-RGB[A]-pixels (or scanlines-of-grey-pixels)
    return array.copy(order='k')

def _read_metadata(bitmap):
    metadata = {}
    models = [(name[5:], number) for name, number in
        METADATA_MODELS.__dict__.items() if name.startswith('FIMD_')]

    tag = ctypes.c_void_p()
    for model_name, number in models:
        mdhandle = _FI.FreeImage_FindFirstMetadata(number, bitmap,
                                                   ctypes.byref(tag))
        mdhandle = ctypes.c_void_p(mdhandle)
        if mdhandle:
            more = True
            while more:
                tag_name = asstr(_FI.FreeImage_GetTagKey(tag))
                tag_type = _FI.FreeImage_GetTagType(tag)
                byte_size = _FI.FreeImage_GetTagLength(tag)
                char_ptr = ctypes.c_char * byte_size
                tag_str = char_ptr.from_address(_FI.FreeImage_GetTagValue(tag))
                if tag_type == METADATA_DATATYPE.FIDT_ASCII:
                    tag_val = asstr(tag_str.value)
                else:
                    tag_val = numpy.fromstring(tag_str,
                            dtype=METADATA_DATATYPE.dtypes[tag_type])
                    if len(tag_val) == 1:
                        tag_val = tag_val[0]
                metadata[(model_name, tag_name)] = tag_val
                more = _FI.FreeImage_FindNextMetadata(mdhandle, ctypes.byref(tag))
            _FI.FreeImage_FindCloseMetadata(mdhandle)
    return metadata


def write(array, filename, flags=0):
    """Write a (width, height) or (width, height, nchannels) array to
    a greyscale, RGB, or RGBA image, with file type deduced from the
    filename.
    The `flags` parameter should be one or more values from the IO_FLAGS
    class defined in this module, or-ed together with | as appropriate.
    (See the source-code comments for more details.)
    """
    array = numpy.asarray(array)
    filename = asbytes(filename)
    ftype = _FI.FreeImage_GetFIFFromFilename(filename)
    if ftype == -1:
        raise ValueError('Cannot determine type for %s' % filename)
    bitmap, fi_type = _array_to_bitmap(array)
    try:
        if fi_type == FI_TYPES.FIT_BITMAP:
            can_write = _FI.FreeImage_FIFSupportsExportBPP(ftype,
                                      _FI.FreeImage_GetBPP(bitmap))
        else:
            can_write = _FI.FreeImage_FIFSupportsExportType(ftype, fi_type)
        if not can_write:
            raise TypeError('Cannot save image of this format '
                            'to this file type')
        res = _FI.FreeImage_Save(ftype, bitmap, filename, flags)
        if not res:
            raise RuntimeError('Could not save image properly.')
    finally:
        _FI.FreeImage_Unload(bitmap)


def write_multipage(arrays, filename, flags=0):
    """Write a list of (width, height) or (width, height, nchannels)
    arrays to a multipage greyscale, RGB, or RGBA image, with file type
    deduced from the filename.
    The `flags` parameter should be one or more values from the IO_FLAGS
    class defined in this module, or-ed together with | as appropriate.
    (See the source-code comments for more details.)
    """
    filename = asbytes(filename)
    ftype = _FI.FreeImage_GetFIFFromFilename(filename)
    if ftype == -1:
        raise ValueError('Cannot determine type of file %s' % filename)
    create_new = True
    read_only = False
    keep_cache_in_memory = True
    multibitmap = _FI.FreeImage_OpenMultiBitmap(ftype, filename,
                                                create_new, read_only,
                                                keep_cache_in_memory, 0)
    multibitmap = ctypes.c_void_p(multibitmap)
    if not multibitmap:
        raise ValueError('Could not open %s for writing multi-page image.' %
                         filename)
    try:
        for array in arrays:
            array = numpy.asarray(array)
            bitmap, fi_type = _array_to_bitmap(array)
            _FI.FreeImage_AppendPage(multibitmap, bitmap)
    finally:
        _FI.FreeImage_CloseMultiBitmap(multibitmap, flags)

# 4-byte quads of 0,v,v,v from 0,0,0,0 to 0,255,255,255
_GREY_PALETTE = numpy.arange(0, 0x01000000, 0x00010101, dtype=numpy.uint32)


def _array_to_bitmap(array):
    """Allocate a FreeImage bitmap and copy a numpy array into it.

    """
    shape, dtype = array.shape, array.dtype
    if len(shape) == 2:
        nchannels = 1
    elif len(shape) == 3:
        nchannels = shape[2]
    else:
        raise ValueError('Only arrays with shape = (width, height) or (width, height, nchannels) are permitted')
    try:
        fi_type = FI_TYPES.fi_types[(dtype, nchannels)]
    except KeyError:
        raise ValueError('Cannot write arrays of given type and shape.')

    itemsize = dtype.itemsize
    bpp = 8 * itemsize * nchannels
    width, height = shape[:2]
    bitmap = _FI.FreeImage_AllocateT(fi_type, width, height, bpp, 0, 0, 0)
    bitmap = ctypes.c_void_p(bitmap)
    if not bitmap:
        raise RuntimeError('Could not allocate image for storage')
    try:
        wrapped_array = _wrap_bitmap_bits_in_array(bitmap, shape, array.dtype)
        if len(shape) == 3 and _FI.FreeImage_IsLittleEndian() and \
               dtype.type == numpy.uint8:
            wrapped_array[:, :, 0] = array[:, :, 2]
            wrapped_array[:, :, 1] = array[:, :, 1]
            wrapped_array[:, :, 2] = array[:, :, 0]
            if shape[2] == 4:
                wrapped_array[:, :, 3] = array[:, :, 3]
        else:
            wrapped_array[:] = array
        if len(shape) == 2 and dtype.type == numpy.uint8:
            palette = _FI.FreeImage_GetPalette(bitmap)
            palette = ctypes.c_void_p(palette)
            if not palette:
                raise RuntimeError('Could not get image palette')
            ctypes.memmove(palette, _GREY_PALETTE.ctypes.data, 1024)
        return bitmap, fi_type
    except:
        _FI.FreeImage_Unload(bitmap)
        raise