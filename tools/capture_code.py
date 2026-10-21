"""Read only the main module's .text from an already-running, pinned game process."""
import argparse
import ctypes as c
from ctypes import wintypes as w
import hashlib
import json
import os
from pathlib import Path
import struct
import sys
import pefile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from configure import ROOT, VERSION, load_manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    parser.add_argument("--pid", type=int, required=True)
    args = parser.parse_args()
    if os.name != "nt":
        raise RuntimeError("Code capture requires Windows")
    manifest = load_manifest()
    exe = (args.game_dir / manifest["executable"]).resolve()
    data = bytearray(exe.read_bytes())
    if hashlib.sha256(data).hexdigest() != manifest["executable_sha256"]:
        raise ValueError("Installed executable differs from the pinned version")
    pe = pefile.PE(data=bytes(data), fast_load=True)
    pe.parse_data_directories(directories=[pefile.DIRECTORY_ENTRY["IMAGE_DIRECTORY_ENTRY_BASERELOC"]])

    class Module(c.Structure):
        _fields_ = [("size", w.DWORD), ("module_id", w.DWORD), ("pid", w.DWORD),
                    ("global_count", w.DWORD), ("process_count", w.DWORD),
                    ("base", c.c_void_p), ("image_size", w.DWORD), ("handle", w.HMODULE),
                    ("name", w.WCHAR * 256), ("path", w.WCHAR * 260)]

    kernel = c.WinDLL("kernel32", use_last_error=True)
    kernel.OpenProcess.argtypes = [w.DWORD, w.BOOL, w.DWORD]
    kernel.OpenProcess.restype = w.HANDLE
    kernel.QueryFullProcessImageNameW.argtypes = [w.HANDLE, w.DWORD, w.LPWSTR, c.POINTER(w.DWORD)]
    kernel.QueryFullProcessImageNameW.restype = w.BOOL
    kernel.ReadProcessMemory.argtypes = [w.HANDLE, c.c_void_p, c.c_void_p, c.c_size_t, c.POINTER(c.c_size_t)]
    kernel.ReadProcessMemory.restype = w.BOOL
    kernel.CreateToolhelp32Snapshot.argtypes = [w.DWORD, w.DWORD]
    kernel.CreateToolhelp32Snapshot.restype = w.HANDLE
    kernel.Module32FirstW.argtypes = [w.HANDLE, c.POINTER(Module)]
    kernel.Module32FirstW.restype = w.BOOL
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.CloseHandle.restype = w.BOOL

    # PROCESS_QUERY_INFORMATION | PROCESS_VM_READ. No write, thread or injection rights.
    process = kernel.OpenProcess(0x410, False, args.pid)
    if not process:
        raise c.WinError(c.get_last_error())
    snapshot = None
    try:
        image_path = c.create_unicode_buffer(32768)
        length = w.DWORD(len(image_path))
        if not kernel.QueryFullProcessImageNameW(process, 0, image_path, c.byref(length)):
            raise c.WinError(c.get_last_error())
        if Path(image_path.value).resolve() != exe:
            raise ValueError("PID does not belong to the specified game executable")
        snapshot = kernel.CreateToolhelp32Snapshot(0x18, args.pid)
        if snapshot == c.c_void_p(-1).value:
            snapshot = None
            raise c.WinError(c.get_last_error())
        module = Module()
        module.size = c.sizeof(module)
        if not kernel.Module32FirstW(snapshot, c.byref(module)):
            raise c.WinError(c.get_last_error())
        if Path(module.path).resolve() != exe:
            raise ValueError("First module is not the expected game executable")
        section = next(s for s in pe.sections if s.Name.rstrip(b"\0") == b".text")
        buffer = c.create_string_buffer(section.SizeOfRawData)
        read = c.c_size_t()
        address = module.base + section.VirtualAddress
        if not kernel.ReadProcessMemory(process, c.c_void_p(address), buffer, len(buffer), c.byref(read)):
            raise c.WinError(c.get_last_error())
        if read.value != len(buffer):
            raise ValueError("Incomplete code-section capture")
        data[section.PointerToRawData:section.PointerToRawData + len(buffer)] = buffer.raw
        delta = module.base - pe.OPTIONAL_HEADER.ImageBase
        for block in getattr(pe, "DIRECTORY_ENTRY_BASERELOC", []):
            for relocation in block.entries:
                if relocation.type == 10 and section.VirtualAddress <= relocation.rva < section.VirtualAddress + len(buffer):
                    offset = pe.get_offset_from_rva(relocation.rva)
                    value = struct.unpack_from("<Q", data, offset)[0]
                    struct.pack_into("<Q", data, offset, (value - delta) & ((1 << 64) - 1))
        for unit in manifest["units"]:
            offset = pe.get_offset_from_rva(int(unit["rva"], 16))
            actual = hashlib.sha256(data[offset:offset + unit["size"]]).hexdigest()
            if actual != unit["code_sha256"]:
                raise ValueError(f"Loaded code differs from the recorded function: {unit['name']}")
        destination = ROOT / "build" / VERSION / "OutOfOre.analysis.exe"
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
        record = {"original_sha256": manifest["executable_sha256"],
                  "analysis_sha256": hashlib.sha256(data).hexdigest(),
                  "captured_section": ".text", "captured_bytes": len(buffer)}
        destination.with_suffix(".json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
        print(f"Captured and verified code only: {destination}")
    finally:
        if snapshot is not None:
            kernel.CloseHandle(snapshot)
        kernel.CloseHandle(process)


if __name__ == "__main__":
    main()
