"""Windows printer enumeration and raw spool printing."""

from __future__ import annotations

import ctypes
from ctypes import wintypes
from pathlib import Path

PRINTER_ENUM_LOCAL = 0x00000002
PRINTER_ENUM_CONNECTIONS = 0x00000004
PRINTER_ENUM_NAME = 0x00000008
PRINTER_ENUM_NETWORK = 0x00000040


class PrintError(RuntimeError):
    pass


class PRINTER_INFO_4(ctypes.Structure):
    _fields_ = [("pPrinterName", wintypes.LPWSTR),
                ("pServerName", wintypes.LPWSTR),
                ("Attributes", wintypes.DWORD)]


class DOC_INFO_1(ctypes.Structure):
    _fields_ = [("pDocName", wintypes.LPWSTR),
                ("pOutputFile", wintypes.LPWSTR),
                ("pDatatype", wintypes.LPWSTR)]


winspool = ctypes.WinDLL("winspool.drv", use_last_error=True)
winspool.EnumPrintersW.argtypes = [
    wintypes.DWORD, wintypes.LPWSTR, wintypes.DWORD, ctypes.c_void_p,
    wintypes.DWORD, ctypes.POINTER(wintypes.DWORD),
    ctypes.POINTER(wintypes.DWORD)]
winspool.EnumPrintersW.restype = wintypes.BOOL
winspool.OpenPrinterW.argtypes = [wintypes.LPWSTR,
                                  ctypes.POINTER(wintypes.HANDLE),
                                  ctypes.c_void_p]
winspool.OpenPrinterW.restype = wintypes.BOOL
winspool.ClosePrinter.argtypes = [wintypes.HANDLE]
winspool.StartDocPrinterW.argtypes = [wintypes.HANDLE, wintypes.DWORD,
                                      ctypes.POINTER(DOC_INFO_1)]
winspool.StartDocPrinterW.restype = wintypes.DWORD
winspool.EndDocPrinter.argtypes = [wintypes.HANDLE]
winspool.StartPagePrinter.argtypes = [wintypes.HANDLE]
winspool.EndPagePrinter.argtypes = [wintypes.HANDLE]
winspool.WritePrinter.argtypes = [wintypes.HANDLE, ctypes.c_void_p,
                                  wintypes.DWORD,
                                  ctypes.POINTER(wintypes.DWORD)]
winspool.WritePrinter.restype = wintypes.BOOL


class PrinterInfo:
    def __init__(self, name, server=""):
        self.name = name
        self.server = server

    def __repr__(self):
        return f"PrinterInfo({self.name!r})"


def list_printers(flags=PRINTER_ENUM_LOCAL | PRINTER_ENUM_CONNECTIONS):
    needed = wintypes.DWORD()
    returned = wintypes.DWORD()
    winspool.EnumPrintersW(flags, None, 4, None, 0,
                          ctypes.byref(needed), ctypes.byref(returned))
    if not needed.value:
        return []
    buffer = ctypes.create_string_buffer(needed.value)
    if not winspool.EnumPrintersW(flags, None, 4, buffer, needed.value,
                                  ctypes.byref(needed),
                                  ctypes.byref(returned)):
        raise PrintError(f"EnumPrinters: {ctypes.get_last_error()}")
    entries = ctypes.cast(buffer, ctypes.POINTER(PRINTER_INFO_4))
    return [PrinterInfo(entries[index].pPrinterName or "",
                        entries[index].pServerName or "")
            for index in range(returned.value)]


def print_raw(path, printer_name, job_name=None, datatype="RAW"):
    data = Path(path).read_bytes()
    handle = wintypes.HANDLE()
    if not winspool.OpenPrinterW(printer_name, ctypes.byref(handle), None):
        raise PrintError(f"OpenPrinter: {ctypes.get_last_error()}")
    try:
        document = DOC_INFO_1(job_name or Path(path).name, None, datatype)
        job = winspool.StartDocPrinterW(handle, 1, ctypes.byref(document))
        if not job:
            raise PrintError(f"StartDocPrinter: {ctypes.get_last_error()}")
        try:
            if not winspool.StartPagePrinter(handle):
                raise PrintError(f"StartPagePrinter: {ctypes.get_last_error()}")
            try:
                buffer = ctypes.create_string_buffer(data, len(data))
                written = wintypes.DWORD()
                if not winspool.WritePrinter(handle, buffer, len(data),
                                             ctypes.byref(written)):
                    raise PrintError(f"WritePrinter: {ctypes.get_last_error()}")
                if written.value != len(data):
                    raise PrintError("WritePrinter: unvollständig")
            finally:
                winspool.EndPagePrinter(handle)
        finally:
            winspool.EndDocPrinter(handle)
        return job
    finally:
        winspool.ClosePrinter(handle)


def print_file(path, printer_name, job_name=None, copies=1, duplex=False):
    path = Path(path)
    if path.suffix.lower() == ".pdf":
        from .pdf_print import print_pdf
        return print_pdf(path, printer_name, copies=copies,
                         duplex=duplex)
    return print_raw(path, printer_name, job_name)
