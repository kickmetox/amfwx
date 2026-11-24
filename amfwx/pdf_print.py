"""PDF rendering and Windows GDI printing (no Qt)."""

from __future__ import annotations

import ctypes
import tempfile
from ctypes import wintypes
from pathlib import Path


class PdfPrintError(RuntimeError):
    pass


class DOCINFOW(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_int),
                ("lpszDocName", wintypes.LPCWSTR),
                ("lpszOutput", wintypes.LPCWSTR),
                ("lpszDatatype", wintypes.LPCWSTR),
                ("fwType", wintypes.DWORD)]


class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [("biSize", wintypes.DWORD), ("biWidth", wintypes.LONG),
                ("biHeight", wintypes.LONG), ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", wintypes.LONG),
                ("biYPelsPerMeter", wintypes.LONG),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD)]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER),
                ("bmiColors", wintypes.DWORD * 3)]


gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
winspool = ctypes.WinDLL("winspool.drv", use_last_error=True)
gdi32.CreateDCW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR,
                            wintypes.LPCWSTR, ctypes.c_void_p]
gdi32.CreateDCW.restype = wintypes.HDC
gdi32.DeleteDC.argtypes = [wintypes.HDC]
gdi32.StartDocW.argtypes = [wintypes.HDC, ctypes.POINTER(DOCINFOW)]
gdi32.StartDocW.restype = ctypes.c_int
gdi32.EndDoc.argtypes = [wintypes.HDC]
gdi32.StartPage.argtypes = [wintypes.HDC]
gdi32.EndPage.argtypes = [wintypes.HDC]
gdi32.GetDeviceCaps.argtypes = [wintypes.HDC, ctypes.c_int]
gdi32.GetDeviceCaps.restype = ctypes.c_int
gdi32.SetStretchBltMode.argtypes = [wintypes.HDC, ctypes.c_int]
gdi32.StretchDIBits.argtypes = [
    wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
    ctypes.c_void_p, ctypes.POINTER(BITMAPINFO), wintypes.UINT,
    wintypes.DWORD]
gdi32.StretchDIBits.restype = ctypes.c_int

HORZRES = 8
VERTRES = 10
BI_RGB = 0
DIB_RGB_COLORS = 0
SRCCOPY = 0x00CC0020
HALFTONE = 4


def render_pdf(path, dpi=150):
    try:
        import pymupdf
    except ImportError:
        try:
            import fitz as pymupdf
        except ImportError as error:
            raise PdfPrintError("pymupdf fehlt: pip install pymupdf") from error
    from PIL import Image
    document = pymupdf.open(str(path))
    pages = []
    for page in document:
        pixmap = page.get_pixmap(dpi=int(dpi), alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height),
                                pixmap.samples)
        image.thumbnail((1500, 2100))
        pages.append(image)
    document.close()
    if not pages:
        raise PdfPrintError("PDF enthält keine Seiten")
    return pages


def _dib(image):
    from PIL import ImageOps
    image = ImageOps.flip(image.convert("RGB"))
    width, height = image.size
    header = BITMAPINFOHEADER()
    header.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    header.biWidth = width
    header.biHeight = height
    header.biPlanes = 1
    header.biBitCount = 24
    header.biCompression = BI_RGB
    header.biSizeImage = width * height * 3
    info = BITMAPINFO(header)
    data = image.tobytes()
    return width, height, ctypes.create_string_buffer(data, len(data)), info



class GDIPLUSSTARTUPINPUT(ctypes.Structure):
    _fields_ = [("GdiplusVersion", ctypes.c_uint32),
                ("DebugEventCallback", ctypes.c_void_p),
                ("SuppressBackgroundThread", wintypes.BOOL),
                ("SuppressExternalCodecs", wintypes.BOOL)]




def _bind_gdiplus(gdiplus):
    gdiplus.GdiplusStartup.argtypes = [ctypes.POINTER(ctypes.c_void_p),
                                       ctypes.POINTER(GDIPLUSSTARTUPINPUT),
                                       ctypes.c_void_p]
    gdiplus.GdiplusStartup.restype = ctypes.c_int
    gdiplus.GdiplusShutdown.argtypes = [ctypes.c_void_p]
    gdiplus.GdipCreateFromHDC.argtypes = [wintypes.HDC,
                                          ctypes.POINTER(ctypes.c_void_p)]
    gdiplus.GdipCreateFromHDC.restype = ctypes.c_int
    gdiplus.GdipDeleteGraphics.argtypes = [ctypes.c_void_p]
    gdiplus.GdipSetPageUnit.argtypes = [ctypes.c_void_p, ctypes.c_int]
    gdiplus.GdipSetInterpolationMode.argtypes = [ctypes.c_void_p,
                                                 ctypes.c_int]
    gdiplus.GdipLoadImageFromFile.argtypes = [wintypes.LPCWSTR,
                                              ctypes.POINTER(ctypes.c_void_p)]
    gdiplus.GdipLoadImageFromFile.restype = ctypes.c_int
    gdiplus.GdipGetImageWidth.argtypes = [ctypes.c_void_p,
                                          ctypes.POINTER(ctypes.c_uint)]
    gdiplus.GdipGetImageHeight.argtypes = [ctypes.c_void_p,
                                           ctypes.POINTER(ctypes.c_uint)]
    gdiplus.GdipDrawImageRectI.argtypes = [ctypes.c_void_p, ctypes.c_void_p,
                                           ctypes.c_int, ctypes.c_int,
                                           ctypes.c_int, ctypes.c_int]
    gdiplus.GdipDrawImageRectI.restype = ctypes.c_int
    gdiplus.GdipDisposeImage.argtypes = [ctypes.c_void_p]


def _print_images_gdiplus(images, hdc, document_name, page_width, page_height):
    gdiplus = ctypes.WinDLL("gdiplus", use_last_error=True)
    _bind_gdiplus(gdiplus)
    token = ctypes.c_void_p()
    startup = GDIPLUSSTARTUPINPUT(1, None, False, False)
    if gdiplus.GdiplusStartup(ctypes.byref(token),
                              ctypes.byref(startup), None) != 0:
        raise PdfPrintError("GdiplusStartup fehlgeschlagen")
    files = []
    try:
        for image in images:
            handle = tempfile.NamedTemporaryFile(
                suffix=".png", prefix="amfwx_gdi_", delete=False)
            handle.close()
            files.append(handle.name)
            image.save(handle.name, "PNG")
            bitmap = ctypes.c_void_p()
            if gdiplus.GdipLoadImageFromFile(handle.name,
                                             ctypes.byref(bitmap)) != 0:
                raise PdfPrintError("GdipLoadImageFromFile fehlgeschlagen")
            graphics = ctypes.c_void_p()
            try:
                if not gdi32.StartPage(hdc):
                    raise PdfPrintError(f"StartPage: {ctypes.get_last_error()}")
                try:
                    if gdiplus.GdipCreateFromHDC(hdc,
                                                  ctypes.byref(graphics)) != 0:
                        raise PdfPrintError("GdipCreateFromHDC fehlgeschlagen")
                    gdiplus.GdipSetPageUnit(graphics, 2)
                    gdiplus.GdipSetInterpolationMode(graphics, 7)
                    width = ctypes.c_uint()
                    height = ctypes.c_uint()
                    gdiplus.GdipGetImageWidth(bitmap, ctypes.byref(width))
                    gdiplus.GdipGetImageHeight(bitmap, ctypes.byref(height))
                    scale = min(page_width / max(1, width.value),
                                page_height / max(1, height.value))
                    target_w = max(1, int(width.value * scale))
                    target_h = max(1, int(height.value * scale))
                    if gdiplus.GdipDrawImageRectI(graphics, bitmap, 0, 0,
                                                  target_w, target_h) != 0:
                        raise PdfPrintError("GdipDrawImageRectI fehlgeschlagen")
                finally:
                    if graphics:
                        gdiplus.GdipDeleteGraphics(graphics)
                    gdi32.EndPage(hdc)
            finally:
                gdiplus.GdipDisposeImage(bitmap)
    finally:
        for filename in files:
            try:
                Path(filename).unlink()
            except OSError:
                pass
        gdiplus.GdiplusShutdown(token)



def _print_dib(images, hdc, page_width, page_height):
    gdi32.SetStretchBltMode(hdc, HALFTONE)
    for image in images:
        width, height, buffer, info = _dib(image)
        scale = min(page_width / max(1, width), page_height / max(1, height))
        target_width = max(1, int(width * scale))
        target_height = max(1, int(height * scale))
        if not gdi32.StartPage(hdc):
            raise PdfPrintError(f"StartPage: {ctypes.get_last_error()}")
        try:
            result = gdi32.StretchDIBits(
                hdc, 0, 0, target_width, target_height, 0, 0, width, height,
                buffer, ctypes.byref(info), DIB_RGB_COLORS, SRCCOPY)
            if result == 0:
                raise PdfPrintError(f"StretchDIBits: {ctypes.get_last_error()}")
        finally:
            gdi32.EndPage(hdc)



class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmOrientation", wintypes.SHORT),
        ("dmPaperSize", wintypes.SHORT),
        ("dmPaperLength", wintypes.SHORT),
        ("dmPaperWidth", wintypes.SHORT),
        ("dmScale", wintypes.SHORT),
        ("dmCopies", wintypes.SHORT),
        ("dmDefaultSource", wintypes.SHORT),
        ("dmPrintQuality", wintypes.SHORT),
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
    ]


class PRINTER_INFO_2W(ctypes.Structure):
    _fields_ = [
        ("pServerName", wintypes.LPWSTR),
        ("pPrinterName", wintypes.LPWSTR),
        ("pShareName", wintypes.LPWSTR),
        ("pPortName", wintypes.LPWSTR),
        ("pDriverName", wintypes.LPWSTR),
        ("pComment", wintypes.LPWSTR),
        ("pLocation", wintypes.LPWSTR),
        ("pDevMode", ctypes.c_void_p),
        ("pSepFile", wintypes.LPWSTR),
        ("pPrintProcessor", wintypes.LPWSTR),
        ("pDatatype", wintypes.LPWSTR),
        ("pParameters", wintypes.LPWSTR),
        ("pSecurityDescriptor", ctypes.c_void_p),
        ("Attributes", wintypes.DWORD),
        ("Priority", wintypes.DWORD),
        ("DefaultPriority", wintypes.DWORD),
        ("StartTime", wintypes.DWORD),
        ("UntilTime", wintypes.DWORD),
        ("Status", wintypes.DWORD),
        ("cJobs", wintypes.DWORD),
        ("AveragePPM", wintypes.DWORD),
    ]


DM_COPIES = 0x0100
DM_DUPLEX = 0x1000
DM_ORIENTATION = 0x0001
DM_PAPERSIZE = 0x0002
DM_ORIENTATION_LANDSCAPE = 2
DM_PAPERS = {"letter": 1, "legal": 5, "a4": 9, "a5": 11, "a3": 8}


def _devmode(printer_name, copies=1, duplex=False, paper=None,
             landscape=False):
    if int(copies) <= 1 and not duplex and not paper and not landscape:
        return None
    winspool.OpenPrinterW.argtypes = [wintypes.LPCWSTR,
                                      ctypes.POINTER(wintypes.HANDLE),
                                      ctypes.c_void_p]
    winspool.GetPrinterW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                     ctypes.c_void_p, wintypes.DWORD,
                                     ctypes.POINTER(wintypes.DWORD)]
    winspool.ClosePrinter.argtypes = [wintypes.HANDLE]
    handle = wintypes.HANDLE()
    if not winspool.OpenPrinterW(printer_name, ctypes.byref(handle), None):
        return None
    try:
        needed = wintypes.DWORD()
        winspool.GetPrinterW(handle, 2, None, 0, ctypes.byref(needed))
        if needed.value == 0:
            return None
        info_buffer = ctypes.create_string_buffer(needed.value)
        if not winspool.GetPrinterW(handle, 2, info_buffer, needed.value,
                                    ctypes.byref(needed)):
            return None
        info = ctypes.cast(info_buffer,
                           ctypes.POINTER(PRINTER_INFO_2W)).contents
        if not info.pDevMode:
            return None
        source = ctypes.cast(info.pDevMode,
                             ctypes.POINTER(DEVMODEW)).contents
        size = int(source.dmSize) + int(source.dmDriverExtra)
        if size <= 0:
            return None
        buffer = ctypes.create_string_buffer(size)
        ctypes.memmove(buffer, info.pDevMode, size)
        devmode = ctypes.cast(buffer, ctypes.POINTER(DEVMODEW))
        fields = devmode.contents.dmFields | DM_COPIES
        devmode.contents.dmCopies = max(1, int(copies))
        paper_id = DM_PAPERS.get(str(paper or "").lower())
        if paper_id:
            devmode.contents.dmPaperSize = paper_id
            fields |= DM_PAPERSIZE
        if landscape:
            devmode.contents.dmOrientation = DM_ORIENTATION_LANDSCAPE
            fields |= DM_ORIENTATION
        if duplex:
            devmode.contents.dmDuplex = 2
            fields |= DM_DUPLEX
        devmode.contents.dmFields = fields
        return devmode
    finally:
        winspool.ClosePrinter(handle)

def _print_dib(images, hdc, page_width, page_height):
    gdi32.SetStretchBltMode(hdc, HALFTONE)
    for image in images:
        width, height, buffer, info = _dib(image)
        scale = min(page_width / max(1, width), page_height / max(1, height))
        target_width = max(1, int(width * scale))
        target_height = max(1, int(height * scale))
        if not gdi32.StartPage(hdc):
            raise PdfPrintError(f"StartPage: {ctypes.get_last_error()}")
        try:
            result = gdi32.StretchDIBits(
                hdc, 0, 0, target_width, target_height, 0, 0, width, height,
                buffer, ctypes.byref(info), DIB_RGB_COLORS, SRCCOPY)
            if result == 0:
                raise PdfPrintError(f"StretchDIBits: {ctypes.get_last_error()}")
        finally:
            gdi32.EndPage(hdc)



class DEVMODEW(ctypes.Structure):
    _fields_ = [
        ("dmDeviceName", wintypes.WCHAR * 32),
        ("dmSpecVersion", wintypes.WORD),
        ("dmDriverVersion", wintypes.WORD),
        ("dmSize", wintypes.WORD),
        ("dmDriverExtra", wintypes.WORD),
        ("dmFields", wintypes.DWORD),
        ("dmOrientation", wintypes.SHORT),
        ("dmPaperSize", wintypes.SHORT),
        ("dmPaperLength", wintypes.SHORT),
        ("dmPaperWidth", wintypes.SHORT),
        ("dmScale", wintypes.SHORT),
        ("dmCopies", wintypes.SHORT),
        ("dmDefaultSource", wintypes.SHORT),
        ("dmPrintQuality", wintypes.SHORT),
        ("dmColor", wintypes.SHORT),
        ("dmDuplex", wintypes.SHORT),
    ]


DM_OUT_BUFFER = 2
DM_IN_BUFFER = 8
DM_COPIES = 0x0100
DM_DUPLEX = 0x1000
DM_ORIENTATION = 0x0001
DM_PAPERSIZE = 0x0002
DM_ORIENTATION_LANDSCAPE = 2
DM_PAPERS = {"letter": 1, "legal": 5, "a4": 9, "a5": 11, "a3": 8}


def print_images(images, printer_name, document_name="AMFWX", output_file=None,
                 copies=1, duplex=False, paper=None, landscape=False):
    devmode = _devmode(printer_name, copies, duplex, paper, landscape)
    hdc = gdi32.CreateDCW("WINSPOOL", printer_name, None,
                          ctypes.byref(devmode) if devmode else None)
    if not hdc:
        raise PdfPrintError(f"CreateDC: {ctypes.get_last_error()}")
    document = DOCINFOW(ctypes.sizeof(DOCINFOW), document_name, output_file, None, 0)
    started = False
    try:
        if gdi32.StartDocW(hdc, ctypes.byref(document)) <= 0:
            raise PdfPrintError(f"StartDoc: {ctypes.get_last_error()}")
        started = True
        page_width = gdi32.GetDeviceCaps(hdc, HORZRES)
        page_height = gdi32.GetDeviceCaps(hdc, VERTRES)
        _print_dib(images, hdc, page_width, page_height)
    finally:
        if started:
            gdi32.EndDoc(hdc)
        gdi32.DeleteDC(hdc)
    return True


def print_pdf(path, printer_name, dpi=150, copies=1, duplex=False,
              paper=None, landscape=False):
    return print_images(render_pdf(path, dpi), printer_name,
                        Path(path).name, copies=copies, duplex=duplex,
                        paper=paper, landscape=landscape)
