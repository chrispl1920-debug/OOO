"""Verify original reference bytes and keep subset reports out of ByteMatch history."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from configure import ROOT, VERSION, load_manifest, make_project


def code_bytes(path):
    data = path.read_bytes()
    machine, count = struct.unpack_from("<HH", data)
    optional_size = struct.unpack_from("<H", data, 16)[0]
    if machine != 0x8664 or optional_size:
        raise ValueError("Expected an x64 COFF reference object")
    result = []
    for index in range(count):
        offset = 20 + index * 40
        name = data[offset:offset + 8].rstrip(b"\0")
        size, start = struct.unpack_from("<II", data, offset + 16)
        if name.startswith(b".text") and size:
            if start + size > len(data):
                raise ValueError("Truncated COFF code section")
            result.append(data[start:start + size])
    if len(result) != 1:
        raise ValueError("Expected exactly one original code section per unit")
    return result[0]


def artifact_name(manifest):
    if manifest["bytematch_ready"] and manifest["scope"] != "whole-game":
        raise ValueError("ByteMatch publication needs a whole-game baseline; this is a subset")
    return f"{VERSION}_report" if manifest["bytematch_ready"] else f"{VERSION}_research"


def validate(report, manifest):
    project = make_project(manifest)
    expected_names = [unit["name"] for unit in project["units"]]
    if [unit["name"] for unit in report["units"]] != expected_names:
        raise ValueError("Report unit set/order differs from manifest")
    for source, expected, actual in zip(manifest["units"], project["units"], report["units"]):
        code = code_bytes(ROOT / expected["target_path"])
        if len(code) != source["size"] or hashlib.sha256(code).hexdigest() != source["code_sha256"]:
            raise ValueError(f"Original reference changed: {source['name']}")
        metadata = actual.get("metadata", {})
        if any(metadata.get(k) != v for k, v in expected["metadata"].items()):
            raise ValueError(f"Report metadata mismatch: {source['name']}")
        if int(actual["measures"]["total_code"]) != source["size"]:
            raise ValueError(f"Incorrect target code size: {source['name']}")
        if source["matched"] and actual["measures"].get("matched_functions") != 1:
            raise ValueError(f"Previously matched function regressed: {source['name']}")
    return artifact_name(manifest)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", type=Path, default=ROOT / "build" / VERSION / "report.json")
    parser.add_argument("--github-output", type=Path)
    args = parser.parse_args()
    manifest = load_manifest()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    artifact = validate(report, manifest)
    scope = {"version": VERSION, "scope": manifest["scope"], "bytematch_ready": manifest["bytematch_ready"]}
    (args.report.parent / "scope.json").write_text(json.dumps(scope, indent=2) + "\n", encoding="utf-8")
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"artifact_name={artifact}\n")
    print(f"Validated original bytes, unit metadata and report scope. Artifact: {artifact}")


if __name__ == "__main__":
    main()
