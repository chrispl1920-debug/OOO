"""Fingerprint the local install; no game files are modified or copied."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
import pefile
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from configure import ROOT, VERSION, load_manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--game-dir", type=Path, required=True)
    args = parser.parse_args()
    manifest = load_manifest()
    exe = args.game_dir / manifest["executable"]
    with exe.open("rb") as stream:
        digest = hashlib.file_digest(stream, "sha256").hexdigest()
    if digest != manifest["executable_sha256"]:
        raise ValueError("Installed executable does not match the pinned version fingerprint")
    pe = pefile.PE(str(exe), fast_load=True)
    sections = [{"name": s.Name.rstrip(b"\0").decode(), "rva": hex(s.VirtualAddress),
                 "size": s.Misc_VirtualSize} for s in pe.sections]
    pak = args.game_dir / "OutOfOre/Content/Paks/OutOfOre-WindowsNoEditor.pak"
    with pak.open("rb") as stream:
        stream.seek(-512, 2)
        footer = stream.read()
    magic = footer.rfind(struct.pack("<I", 0x5a6f12e1))
    if magic < 1:
        raise ValueError("Unrecognized archive footer")
    result = {"version_label": VERSION, "executable_sha256": digest, "size": exe.stat().st_size,
              "machine": hex(pe.FILE_HEADER.Machine), "image_base": hex(pe.OPTIONAL_HEADER.ImageBase),
              "sections": sections, "pak_size": pak.stat().st_size,
              "pak_version": struct.unpack_from("<I", footer, magic + 4)[0],
              "pak_index_encrypted": bool(footer[magic - 1])}
    destination = ROOT / "build" / VERSION / "inventory.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
