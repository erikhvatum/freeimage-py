import distutils.core
import sys

SRCS = """Source/FreeImage/BitmapAccess.cpp
Source/FreeImage/ColorLookup.cpp
Source/FreeImage/FreeImage.cpp
Source/FreeImage/FreeImageC.c
Source/FreeImage/FreeImageIO.cpp
Source/FreeImage/GetType.cpp
Source/FreeImage/MemoryIO.cpp
Source/FreeImage/PixelAccess.cpp
Source/FreeImage/MNGHelper.cpp
Source/FreeImage/Plugin.cpp
Source/FreeImage/PluginBMP.cpp
Source/FreeImage/PluginCUT.cpp
Source/FreeImage/PluginDDS.cpp
Source/FreeImage/PluginG3.cpp
Source/FreeImage/PluginGIF.cpp
Source/FreeImage/PluginHDR.cpp
Source/FreeImage/PluginICO.cpp
Source/FreeImage/PluginIFF.cpp
Source/FreeImage/PluginJNG.cpp
Source/FreeImage/PluginJPEG.cpp
Source/FreeImage/PluginKOALA.cpp
Source/FreeImage/PluginMNG.cpp
Source/FreeImage/PluginPCD.cpp
Source/FreeImage/PluginPCX.cpp
Source/FreeImage/PluginPFM.cpp
Source/FreeImage/PluginPICT.cpp
Source/FreeImage/PluginPNG.cpp
Source/FreeImage/PluginPNM.cpp
Source/FreeImage/PluginPSD.cpp
Source/FreeImage/PluginRAS.cpp
Source/FreeImage/PluginSGI.cpp
Source/FreeImage/PluginTARGA.cpp
Source/FreeImage/PluginTIFF.cpp
Source/FreeImage/PluginWBMP.cpp
Source/FreeImage/PluginXBM.cpp
Source/FreeImage/PluginXPM.cpp
Source/FreeImage/PSDParser.cpp
Source/FreeImage/TIFFLogLuv.cpp
Source/FreeImage/Conversion.cpp
Source/FreeImage/Conversion16_555.cpp
Source/FreeImage/Conversion16_565.cpp
Source/FreeImage/Conversion24.cpp
Source/FreeImage/Conversion32.cpp
Source/FreeImage/Conversion4.cpp
Source/FreeImage/Conversion8.cpp
Source/FreeImage/ConversionFloat.cpp
Source/FreeImage/ConversionRGB16.cpp
Source/FreeImage/ConversionRGBA16.cpp
Source/FreeImage/ConversionRGBAF.cpp
Source/FreeImage/ConversionRGBF.cpp
Source/FreeImage/ConversionType.cpp
Source/FreeImage/ConversionUINT16.cpp
Source/FreeImage/Halftoning.cpp
Source/FreeImage/tmoColorConvert.cpp
Source/FreeImage/tmoDrago03.cpp
Source/FreeImage/tmoFattal02.cpp
Source/FreeImage/tmoReinhard05.cpp
Source/FreeImage/ToneMapping.cpp
Source/FreeImage/LFPQuantizer.cpp
Source/FreeImage/NNQuantizer.cpp
Source/FreeImage/WuQuantizer.cpp
Source/DeprecationManager/Deprecated.cpp
Source/DeprecationManager/DeprecationMgr.cpp
Source/FreeImage/CacheFile.cpp
Source/FreeImage/MultiPage.cpp
Source/FreeImage/ZLibInterface.cpp
Source/Metadata/Exif.cpp
Source/Metadata/FIRational.cpp
Source/Metadata/FreeImageTag.cpp
Source/Metadata/IPTC.cpp
Source/Metadata/TagConversion.cpp
Source/Metadata/TagLib.cpp
Source/Metadata/XTIFF.cpp
Source/FreeImageToolkit/Background.cpp
Source/FreeImageToolkit/BSplineRotate.cpp
Source/FreeImageToolkit/Channels.cpp
Source/FreeImageToolkit/ClassicRotate.cpp
Source/FreeImageToolkit/Colors.cpp
Source/FreeImageToolkit/CopyPaste.cpp
Source/FreeImageToolkit/Display.cpp
Source/FreeImageToolkit/Flip.cpp
Source/FreeImageToolkit/JPEGTransform.cpp
Source/FreeImageToolkit/MultigridPoissonSolver.cpp
Source/FreeImageToolkit/Rescale.cpp
Source/FreeImageToolkit/Resize.cpp
Source/LibJPEG/jaricom.c
Source/LibJPEG/jcapimin.c
Source/LibJPEG/jcapistd.c
Source/LibJPEG/jcarith.c
Source/LibJPEG/jccoefct.c
Source/LibJPEG/jccolor.c
Source/LibJPEG/jcdctmgr.c
Source/LibJPEG/jchuff.c
Source/LibJPEG/jcinit.c
Source/LibJPEG/jcmainct.c
Source/LibJPEG/jcmarker.c
Source/LibJPEG/jcmaster.c
Source/LibJPEG/jcomapi.c
Source/LibJPEG/jcparam.c
Source/LibJPEG/jcprepct.c
Source/LibJPEG/jcsample.c
Source/LibJPEG/jctrans.c
Source/LibJPEG/jdapimin.c
Source/LibJPEG/jdapistd.c
Source/LibJPEG/jdarith.c
Source/LibJPEG/jdatadst.c
Source/LibJPEG/jdatasrc.c
Source/LibJPEG/jdcoefct.c
Source/LibJPEG/jdcolor.c
Source/LibJPEG/jddctmgr.c
Source/LibJPEG/jdhuff.c
Source/LibJPEG/jdinput.c
Source/LibJPEG/jdmainct.c
Source/LibJPEG/jdmarker.c
Source/LibJPEG/jdmaster.c
Source/LibJPEG/jdmerge.c
Source/LibJPEG/jdpostct.c
Source/LibJPEG/jdsample.c
Source/LibJPEG/jdtrans.c
Source/LibJPEG/jerror.c
Source/LibJPEG/jfdctflt.c
Source/LibJPEG/jfdctfst.c
Source/LibJPEG/jfdctint.c
Source/LibJPEG/jidctflt.c
Source/LibJPEG/jidctfst.c
Source/LibJPEG/jidctint.c
Source/LibJPEG/jmemmgr.c
Source/LibJPEG/jmemnobs.c
Source/LibJPEG/jquant1.c
Source/LibJPEG/jquant2.c
Source/LibJPEG/jutils.c
Source/LibJPEG/transupp.c
Source/LibPNG/png.c
Source/LibPNG/pngerror.c
Source/LibPNG/pngget.c
Source/LibPNG/pngmem.c
Source/LibPNG/pngpread.c
Source/LibPNG/pngread.c
Source/LibPNG/pngrio.c
Source/LibPNG/pngrtran.c
Source/LibPNG/pngrutil.c
Source/LibPNG/pngset.c
Source/LibPNG/pngtrans.c
Source/LibPNG/pngwio.c
Source/LibPNG/pngwrite.c
Source/LibPNG/pngwtran.c
Source/LibPNG/pngwutil.c
Source/LibTIFF4/tif_aux.c
Source/LibTIFF4/tif_close.c
Source/LibTIFF4/tif_codec.c
Source/LibTIFF4/tif_color.c
Source/LibTIFF4/tif_compress.c
Source/LibTIFF4/tif_dir.c
Source/LibTIFF4/tif_dirinfo.c
Source/LibTIFF4/tif_dirread.c
Source/LibTIFF4/tif_dirwrite.c
Source/LibTIFF4/tif_dumpmode.c
Source/LibTIFF4/tif_error.c
Source/LibTIFF4/tif_extension.c
Source/LibTIFF4/tif_fax3.c
Source/LibTIFF4/tif_fax3sm.c
Source/LibTIFF4/tif_flush.c
Source/LibTIFF4/tif_getimage.c
Source/LibTIFF4/tif_jpeg.c
Source/LibTIFF4/tif_luv.c
Source/LibTIFF4/tif_lzma.c
Source/LibTIFF4/tif_lzw.c
Source/LibTIFF4/tif_next.c
Source/LibTIFF4/tif_ojpeg.c
Source/LibTIFF4/tif_open.c
Source/LibTIFF4/tif_packbits.c
Source/LibTIFF4/tif_pixarlog.c
Source/LibTIFF4/tif_predict.c
Source/LibTIFF4/tif_print.c
Source/LibTIFF4/tif_read.c
Source/LibTIFF4/tif_strip.c
Source/LibTIFF4/tif_swab.c
Source/LibTIFF4/tif_thunder.c
Source/LibTIFF4/tif_tile.c
Source/LibTIFF4/tif_version.c
Source/LibTIFF4/tif_warning.c
Source/LibTIFF4/tif_write.c
Source/LibTIFF4/tif_zip.c
Source/ZLib/adler32.c
Source/ZLib/compress.c
Source/ZLib/crc32.c
Source/ZLib/deflate.c
Source/ZLib/gzclose.c
Source/ZLib/gzlib.c
Source/ZLib/gzread.c
Source/ZLib/gzwrite.c
Source/ZLib/infback.c
Source/ZLib/inffast.c
Source/ZLib/inflate.c
Source/ZLib/inftrees.c
Source/ZLib/trees.c
Source/ZLib/uncompr.c
Source/ZLib/zutil.c
Source/OpenEXR/Half/half.cpp""".split('\n')

INCLUDE = """Source
Source/Metadata
Source/FreeImageToolkit
Source/LibJPEG
Source/LibPNG
Source/LibTIFF4
Source/ZLib
Source/OpenEXR/Half""".split('\n')

extra_compile_args = []

if sys.platform != 'win32':
    extra_compile_args.extend(('-O3', '-march=native'))

freeimage = distutils.core.Extension('freeimage._freeimage',
    sources = ['freeimage/_freeimage.c'] + SRCS,
    extra_compile_args = extra_compile_args,
    include_dirs = INCLUDE)

distutils.core.setup(name = 'freeimage',
        version = '1.0',
        description = 'freeimage package',
        ext_modules = [freeimage],
        packages = ['freeimage'])
