// Export selected functions as analysis drafts; these are not buildable source.
// @category OOO
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.DecompInterface;
import ghidra.app.decompiler.DecompileResults;
import ghidra.program.model.address.Address;
import ghidra.program.model.address.AddressSet;
import ghidra.program.model.listing.Function;
import ghidra.program.model.listing.Instruction;
import ghidra.program.model.symbol.SourceType;
import java.io.*;
import java.nio.charset.StandardCharsets;

public class ExportSelected extends GhidraScript {
    public void run() throws Exception {
        String[] args = getScriptArgs();
        if (args.length < 2) throw new IllegalArgumentException("output-dir name:rva:size [...]");
        File dir = new File(args[0]);
        if (!dir.isDirectory() && !dir.mkdirs()) throw new IOException("Cannot create " + dir);
        DecompInterface decompiler = new DecompInterface();
        if (!decompiler.openProgram(currentProgram)) throw new IOException("Cannot open program");
        try {
            for (int i = 1; i < args.length; ++i) {
                String[] parts = args[i].split(":", 3);
                if (parts.length != 3 || !parts[0].matches("[A-Za-z_][A-Za-z0-9_]*"))
                    throw new IllegalArgumentException("Invalid selection: " + args[i]);
                Address entry = currentProgram.getImageBase().add(Long.decode(parts[1]));
                int size = Integer.decode(parts[2]);
                if (size < 1 || size > 1048576) throw new IllegalArgumentException("Invalid function size");
                Address end = entry.add(size - 1);
                Address cursor = entry;
                while (cursor.compareTo(end) <= 0) {
                    if (getInstructionAt(cursor) == null) disassemble(cursor);
                    Instruction ins = getInstructionAt(cursor);
                    if (ins == null || ins.getMaxAddress().compareTo(end) > 0)
                        throw new IOException("Cannot decode bounded function at " + cursor);
                    cursor = ins.getMaxAddress().add(1);
                }
                Function fn = getFunctionAt(entry);
                if (fn == null) fn = createFunction(entry, parts[0]);
                if (fn == null) throw new IOException("Cannot define function at " + entry);
                fn.setBody(new AddressSet(entry, end));
                fn.setName(parts[0], SourceType.USER_DEFINED);
                DecompileResults result = decompiler.decompileFunction(fn, 60, monitor);
                if (!result.decompileCompleted()) throw new IOException(result.getErrorMessage());
                try (PrintWriter out = new PrintWriter(new File(dir, parts[0]+".c"), StandardCharsets.UTF_8)) {
                    out.println("/* Ghidra analysis draft. Types and signatures need review. */");
                    out.println("/* Image: " + currentProgram.getName() + "; entry: " + entry + " */");
                    out.println(result.getDecompiledFunction().getC());
                }
                try (PrintWriter out = new PrintWriter(new File(dir, parts[0]+".asm"), StandardCharsets.UTF_8)) {
                    var instructions = currentProgram.getListing().getInstructions(new AddressSet(entry, end), true);
                    while (instructions.hasNext()) {
                        Instruction ins = instructions.next();
                        out.println(ins.getAddress() + "  " + ins.toString());
                    }
                }
                println("Exported " + fn.getName() + " at " + entry);
            }
        } finally { decompiler.dispose(); }
    }
}
