"""Build the recovered module and its original assembly references (not the game)."""
import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess

from configure import ROOT, VERSION, load_manifest, make_project


def compiler_environment():
    env = os.environ.copy()
    if shutil.which("cl.exe") and shutil.which("ml64.exe"):
        return {key.upper(): value for key, value in env.items()}
    vswhere = Path(env.get("ProgramFiles(x86)", "C:/Program Files (x86)")) / "Microsoft Visual Studio/Installer/vswhere.exe"
    if not vswhere.is_file():
        raise RuntimeError("Install Visual Studio C++ tools or run in an x64 Native Tools prompt")
    installation = subprocess.check_output([
        str(vswhere), "-latest", "-products", "*", "-requires",
        "Microsoft.VisualStudio.Component.VC.Tools.x86.x64", "-property", "installationPath"
    ], text=True).strip()
    setup = Path(installation) / "VC/Auxiliary/Build/vcvars64.bat"
    if not installation or not setup.is_file():
        raise RuntimeError("No Visual Studio x64 C++ tools were found")
    command = f'call "{setup}" >nul && set'
    result = subprocess.run(command, shell=True,
                            capture_output=True, text=True, check=True)
    env = {key.upper(): value for key, value in env.items()}
    for line in result.stdout.splitlines():
        key, separator, value = line.partition("=")
        if separator and key:
            env[key.upper()] = value
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("object", nargs="?", help="objdiff may request a specific output; all four units are rebuilt")
    parser.parse_args()
    if os.name != "nt":
        raise RuntimeError("The reference objects require Windows MSVC and MASM")
    manifest = load_manifest()
    project = make_project(manifest)
    env = compiler_environment()
    compiler = shutil.which("cl.exe", path=env["PATH"])
    assembler = shutil.which("ml64.exe", path=env["PATH"])
    if not compiler or not assembler:
        raise RuntimeError("Visual Studio did not provide cl.exe and ml64.exe")
    objects = []
    for unit, entry in zip(manifest["units"], project["units"]):
        target, base = (ROOT / entry[k] for k in ("target_path", "base_path"))
        target.parent.mkdir(parents=True, exist_ok=True)
        base.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run([assembler, "/nologo", "/c", f"/Fo{target}", str(ROOT / unit["target_source"])],
                       env=env, cwd=ROOT, check=True)
        subprocess.run([compiler, "/nologo", "/c", "/O2", "/Gy", f"/Fo{base}", str(ROOT / unit["source_path"])],
                       env=env, cwd=ROOT, check=True)
        objects.append(str(base))
    test = ROOT / "build" / VERSION / "money_state_test.exe"
    test_obj = test.with_suffix(".obj")
    subprocess.run([compiler, "/nologo", "/O2", f"/Fe{test}", f"/Fo{test_obj}",
                    str(ROOT / "tests/money_state_test.cpp"), *objects], env=env, cwd=test.parent, check=True)
    subprocess.run([str(test)], check=True)
    (ROOT / "objdiff.json").write_text(json.dumps(project, indent=2) + "\n", encoding="utf-8")
    print("Recovered module built and behavioral checks passed; the game has not been rebuilt.")


if __name__ == "__main__":
    main()
