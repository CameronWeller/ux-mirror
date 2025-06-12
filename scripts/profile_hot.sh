#!/usr/bin/env bash

# profile_hot.sh -- profile a Python program and produce perf data + optional flamegraph
# Usage: profile_hot.sh <python-script> [script args]
# Environment variables:
#   PROFILE_OUT   Directory to store profiling artefacts (default: build/profiles)
#   EVENTS        Comma-separated perf events (default: cpu-clock,context-switches)

set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <python-script> [args...]" >&2
  exit 1
fi

SCRIPT_PATH="$1"
shift

PROFILE_OUT="${PROFILE_OUT:-build/profiles}"
EVENTS="${EVENTS:-cpu-clock,context-switches}"
mkdir -p "$PROFILE_OUT"

PERF_DATA="$PROFILE_OUT/perf.data"

# Check perf availability
if ! command -v perf >/dev/null 2>&1; then
  echo "Error: 'perf' not found. Please install linux-tools or perf for your distro." >&2
  exit 2
fi

# Record perf trace
printf "Profiling %s with perf events %s...\n" "$SCRIPT_PATH" "$EVENTS"
perf record -e "$EVENTS" -F 99 -g -o "$PERF_DATA" -- python "$SCRIPT_PATH" "$@"

# Generate human-readable script output
perf script -i "$PERF_DATA" > "$PROFILE_OUT/perf.script" 2>/dev/null || true

# If FlameGraph utilities are available, create flamegraph.svg
if command -v stackcollapse-perf.pl >/dev/null 2>&1 && command -v flamegraph.pl >/dev/null 2>&1; then
  echo "Generating flamegraph.svg..."
  stackcollapse-perf.pl "$PROFILE_OUT/perf.script" | flamegraph.pl > "$PROFILE_OUT/flamegraph.svg"
fi

echo "Perf data stored in $PROFILE_OUT" 