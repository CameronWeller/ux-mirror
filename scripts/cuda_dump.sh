#!/usr/bin/env bash

# cuda_dump.sh -- extract SASS assembly from CUDA binary objects (.cubin, .fatbin).
# The script relies on cuobjdump (installed with the NVIDIA CUDA toolkit).
# Output files are stored in ${CUDA_SASS_OUT:-build/cuda_sass}

set -euo pipefail

CUDA_SASS_OUT="${CUDA_SASS_OUT:-build/cuda_sass}"
mkdir -p "$CUDA_SASS_OUT"

if ! command -v cuobjdump >/dev/null 2>&1; then
  echo "Error: 'cuobjdump' not available. Ensure CUDA toolkit is installed and cuobjdump is on PATH." >&2
  exit 2
fi

mapfile -t CUBINS < <(find build -type f \( -name "*.cubin" -o -name "*.fatbin" -o -name "*.so" \))

if [[ ${#CUBINS[@]} -eq 0 ]]; then
  echo "No CUDA binaries found under build/." >&2
  exit 0
fi

for BIN in "${CUBINS[@]}"; do
  BASENAME=$(basename "$BIN")
  OUTFILE="$CUDA_SASS_OUT/${BASENAME}.sass"
  echo "Dumping SASS for $BIN -> $OUTFILE"
  cuobjdump --dump-sass "$BIN" > "$OUTFILE" || {
    echo "Failed to dump SASS for $BIN" >&2
  }
done

echo "CUDA SASS dumps written to $CUDA_SASS_OUT" 