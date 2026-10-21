"""Generate objdiff.json from the version manifest; generated files stay untracked."""
import argparse
import json
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent
VERSION = "0.36.5552"


def relative_path(value):
    if not isinstance(value, str) or not value or "\\" in value or ":" in value:
        raise ValueError(f"Expected a repository-relative path with '/': {value!r}")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in value.split("/")):
        raise ValueError(f"Unsafe path: {value!r}")
    if not (ROOT / value).resolve().is_relative_to(ROOT):
        raise ValueError(f"Path leaves repository: {value!r}")
    return value


def load_manifest():
    manifest = json.loads((ROOT / "config" / f"{VERSION}.json").read_text(encoding="utf-8"))
    if manifest["version"] != VERSION:
        raise ValueError("Version mismatch")
    seen = set()
    for unit in manifest["units"]:
        name = relative_path(unit["name"])
        if "/" not in name or name in seen:
            raise ValueError(f"Duplicate or ungrouped unit name: {name}")
        seen.add(name)
        for key in ("source_path", "target_source"):
            if not (ROOT / relative_path(unit[key])).is_file():
                raise ValueError(f"Missing {key}: {unit[key]}")
        if unit["source_path"] != f"src/{name}.cpp":
            raise ValueError("Unit names must follow the source tree")
        for key in ("matched", "linked_from_source"):
            if type(unit.get(key)) is not bool:
                raise ValueError(f"{key} must be a boolean")
    return manifest


def make_project(manifest):
    return {
        "$schema": "https://raw.githubusercontent.com/encounter/objdiff/v3.8.3/config.schema.json",
        "custom_make": "python",
        "custom_args": ["build.py"],
        "build_target": False,
        "build_base": True,
        "units": [
            {
                "name": unit["name"],
                "target_path": f"build/{VERSION}/orig/{unit['name']}.obj",
                "base_path": f"build/{VERSION}/obj/{unit['name']}.obj",
                "metadata": {
                    "source_path": unit["source_path"],
                    "complete": unit["matched"] and unit["linked_from_source"],
                },
            } for unit in manifest["units"]
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="validate without writing output")
    args = parser.parse_args()
    project = make_project(load_manifest())
    if not args.check:
        (ROOT / "objdiff.json").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    print(f"Validated {len(project['units'])} recovered units for {VERSION}")


if __name__ == "__main__":
    main()
