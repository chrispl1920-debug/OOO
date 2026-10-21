/* Ghidra analysis draft. Types and signatures need review. */
/* Image: OutOfOre.analysis.exe; entry: 141eb3a20 */

void execSetMaxFuelAmount(undefined8 param_1,longlong param_2)

{
  undefined4 auStackX_10 [6];

  auStackX_10[0] = 0;
  FUN_142239ba0();
  if (*(longlong *)(param_2 + 0x20) == 0) {
    *(undefined8 *)(param_2 + 0x80) = *(undefined8 *)(*(longlong *)(param_2 + 0x80) + 0x20);
    func_0x000142261f30(param_2,auStackX_10);
  }
  else {
    func_0x000142261f00(param_2,*(undefined8 *)(param_2 + 0x18),auStackX_10);
  }
  *(ulonglong *)(param_2 + 0x20) =
       (ulonglong)(*(longlong *)(param_2 + 0x20) != 0) + *(longlong *)(param_2 + 0x20);
  SetMaxFuelAmount(param_1,auStackX_10[0]);
  return;
}
