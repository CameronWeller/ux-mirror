#!/usr/bin/env bash

# dump_disassembly.sh -- emit readable assembly listings for supplied binaries.
# Usage: dump_disassembly.sh [binary1 binary2 ...]
# If no binaries are supplied, the script attempts to locate ELF executables (*.so,*.o,*.exe) under build/ .
# Output files are stored in ${ASM_OUT:-build/asm} with .asm extension.

set -euo pipefail

ASM_OUT="${ASM_OUT:-build/asm}"
mkdir -p "$ASM_OUT"

if ! command -v objdump >/dev/null 2>&1; then
  echo "Error: 'objdump' not found. Install binutils." >&2
  exit 2
fi

if [[ $# -eq 0 ]]; then
  mapfile -t TARGETS < <(find build -type f \( -name "*.so" -o -name "*.o" -o -name "*.exe" -o -name "*.dll" \))
else
  TARGETS=("$@")
fi

if [[ ${#TARGETS[@]} -eq 0 ]]; then
  echo "No binaries found to disassemble." >&2
  exit 0
fi

for BIN in "${TARGETS[@]}"; do
  if [[ ! -f "$BIN" ]]; then
    echo "Warning: $BIN is not a file, skipping." >&2
    continue
  fi
  BASENAME=$(basename "$BIN")
  OUTFILE="$ASM_OUT/${BASENAME}.asm"
  echo "Disassembling $BIN -> $OUTFILE"
  # --no-show-raw-insn keeps output smaller; --line-numbers attempts source mapping if symbols are present
  objdump -d --no-show-raw-insn --line-numbers "$BIN" > "$OUTFILE" || {
    echo "Failed to disassemble $BIN" >&2
  }
done

echo "Assembly dumps written to $ASM_OUT" 