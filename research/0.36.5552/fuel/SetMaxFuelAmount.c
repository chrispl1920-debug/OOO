/* Ghidra analysis draft. Types and signatures need review. */
/* Image: OutOfOre.analysis.exe; entry: 141e32e80 */

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void SetMaxFuelAmount(longlong param_1,float param_2)

{
  if (_DAT_1447b5330 <= param_2) {
    *(float *)(param_1 + 0x2d8) = param_2;
  }
  return;
}
