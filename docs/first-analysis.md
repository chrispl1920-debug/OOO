# First analysis: 0.36.5552

The starting GitHub `main` contained only `.gitattributes`. There was no source tree,
configure script, build system, objdiff configuration, workflow, or functional-C list.

The installed game contains a PE32+ x64 shipping executable and a cooked Unreal
archive. The debug manifest mentions `OutOfOre-Win64-Shipping.pdb`, but the file is
absent. No original `.obj`, `.lib`, `.uproject`, or C++ sources were found.

## Pinned input

- Executable: `OutOfOre/Binaries/Win64/OutOfOre-Win64-Shipping.exe`
- Size: 103,463,216 bytes
- SHA-256: `7fe80b871f0f4c2572ea82bd1aca01a8fcd5ce404d4d3bae0c291cdb3a198a76`
- Steam app/build: `2009350` / `25808949`
- Engine string: `++UE4+Release-4.27-CL-18319896`
- Preferred image base: `0x140000000`
- Linker header: 14.29. This does not establish the original compiler version or flags.
- `.pdata` has 312,504 runtime function records; these include engine/library code
  and function fragments, and are not a count of unique game functions.
- Cooked archive: 14,213,298,292 bytes, pak format 11; its footer marks the index encrypted.

The disk `.text` did not decode as ordinary native instructions at registered
function pointers. Reading the already-running game's `.text` produced valid code.
Only that code section was overlaid on a local copy of the original PE. Static
read-only data comes from the disk file, not the live game state. No installed file
or process memory was modified. Ghidra used `x86:LE:64:default:windows`.

## Recovered functions

Native registration name/code pairs identify the `exec` wrappers. Direct calls from
those wrappers identify the small methods below. RVAs are relative to the pinned
image base; the original C++ class names and parameter signedness remain unproven.

| Name | Native wrapper RVA | Implementation RVA | Bytes | Observed store |
| --- | --- | --- | --- | --- |
| SetRewardMoney | `0x1ecc5e0` | `0x1e33490` | 4 | 32 bits at object + `0x48` |
| SetPersonalMoney | `0x1ec4f20` | `0x1e33030` | 7 | 32 bits at object + `0x7ac` |
| SetSuperGameMoney | `0x1ea0e40` | `0x1e33610` | 8 | 64 bits at object + `0x2b8` |
| SetSuperCompanyMoney | `0x1ea0db0` | `0x1df6df0` | 8 | 64 bits at object + `0x2b0` |

Each reference assembly file transcribes the observed original instructions, with
assigned readable names. It is independent of the current C++ implementation.
The manifest records a hash of each captured native instruction span. CI checks
the assembled reference section against that hash before accepting the report.
These four leaf functions have no external references or relocations to reconstruct.
The target COFF objects are reconstruction references, not original compiler outputs.

The standalone C++ functions reproduced all **27 instruction bytes**, and objdiff
reported four matched functions. Twenty behavior cases check signed boundary values
and verify that every adjacent byte is preserved. Byte matching does not establish
original class declarations, full gameplay behavior, or whole-game linkage.

## Fuel draft

`execSetMaxFuelAmount` at RVA `0x1eb3a20` calls `SetMaxFuelAmount` at `0x1e32e80`.
The method compares its float argument against the read-only constant at RVA
`0x47b5330` (`00 00 80 3f`, float `1.0`) and stores the value at object + `0x2d8`
when it is at least 1.0. It returns without storing for lower values or an unordered
comparison. The checked-in Ghidra draft intentionally retains the unresolved global
name, so the inference is separate from the exported evidence.

The wrapper draft lacks complete Unreal types/prototypes. It is not buildable source
and is excluded from progress. Its parameter unpacking and engine calls still need
review. Compiling the fuel method will also require restoring its constant relocation.

## Remaining work

1. Recover the surrounding game class identities and layouts from Unreal metadata.
2. Reconstruct and test the fuel method, then tackle its caller/component behavior.
3. Recover additional native methods and separate game, plugin, engine, and library code.
4. Establish a whole-game target/object baseline with restored symbols and relocations;
   linked executable slices cannot generally be treated as original relocatable objects.
5. Recover the original build/compiler/link configuration and eventually relink from source.
6. Enable ByteMatch history only when the report includes the agreed whole-game baseline.

The cooked archive's encrypted index was detected but its assets and Blueprints have
not been extracted. No decryption key is included. Binary copies, Ghidra projects,
compiled objects, reports, and temporary analysis remain outside Git.
