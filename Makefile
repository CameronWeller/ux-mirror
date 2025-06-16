# Hot-path optimisation, JIT/GPU ISA review, and compiler-regression guard helpers

.PHONY: build profile-hot asm-dump cuda-dump

# Compile or otherwise prepare binaries into ./build (override as needed)
build:
	@echo "[make] No default build step defined. Add your build commands here if required."

# Usage: make profile-hot SCRIPT=path/to/entrypoint.py [ARGS="--flags"]
profile-hot:
	@echo "[make] Running hot-path profiler via scripts/profile_hot.sh"
	bash scripts/profile_hot.sh $(SCRIPT) $(ARGS)

# Dump disassembly for binaries in ./build or supplied via FILES="bin1 bin2"
asm-dump:
	@echo "[make] Dumping disassembly via scripts/dump_disassembly.sh"
	bash scripts/dump_disassembly.sh $(FILES)

# Dump CUDA SASS/PTX for GPU binaries
cuda-dump:
	@echo "[make] Dumping CUDA SASS via scripts/cuda_dump.sh"
	bash scripts/cuda_dump.sh 