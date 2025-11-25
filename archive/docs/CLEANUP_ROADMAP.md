# Code Cleanup Roadmap for UX-MIRROR

## Current Cleanup Status

### ✅ Already Cleaned
- Multi-agent infrastructure removed (completed)
- Agent files deleted and references updated
- Architecture consolidated to unified system

### 🔍 Identified for Cleanup

## Phase 1: Remove Legacy/Deprecated Code

### 1. Legacy Directory
**Location:** `legacy/`
**Status:** Contains old agent implementations
**Action:** 
- [ ] Review if any code is still needed
- [ ] Archive or remove if completely obsolete
- [ ] Files:
  - `legacy/agents/orchestrator.py`
  - `legacy/agents/simple_orchestrator.py`
  - `legacy/agents/autonomous_implementation.py`
  - `legacy/start_core_system.py`

### 2. Empty/Unused Directories
**Status:** Check for empty directories
**Action:**
- [ ] `agents/` - Should be empty after agent removal
- [ ] `game-target/` - Check if used
- [ ] `test_game/` - Check if used
- [ ] `love2d_source/` - Check if used
- [ ] `pixel_game_engine/` - Check if used
- [ ] `raylib_source/` - Check if used

### 3. Example/Demo Files
**Status:** May be useful for reference but clutter root
**Action:**
- [ ] `prototype_poc.py` - Move to `examples/` or remove
- [ ] `api_call_example.py` - Move to `examples/` or remove
- [ ] `comprehensive_ux_prompt_example.py` - Move to `examples/` or remove
- [ ] `ai_enhanced_demo.py` - Move to `examples/` or remove
- [ ] `feedback_integration_demo.py` - Move to `examples/` or remove
- [ ] `game_testing_demo.py` - Move to `examples/` or remove

### 4. Test Files in Root
**Status:** Should be in `tests/` directory
**Action:**
- [ ] `test_complete_system.py` → `tests/integration/`
- [ ] `test_cpp_game_integration.py` → `tests/integration/`
- [ ] `test_cpp_game.cpp` → `tests/integration/` or remove
- [ ] `test_dark_theme.py` → `tests/unit/`
- [ ] `test_improvements.py` → `tests/unit/`
- [ ] `test_real_analysis.py` → `tests/integration/`
- [ ] `test_screenshot_demo.py` → `tests/integration/` or `examples/`
- [ ] `test_secure_config.py` → `tests/unit/`
- [ ] `test_sprint2_progress.py` → `tests/integration/`

### 5. Duplicate/Refactored Files
**Status:** May have old and new versions
**Action:**
- [ ] `src/analysis/visual_analysis_refactored.py` - Check if this replaces `visual_analysis.py`
- [ ] If refactored version is better, remove old one
- [ ] If both needed, consolidate or clearly document differences

### 6. Launcher Files
**Status:** Multiple launcher implementations
**Action:**
- [ ] `enhanced_ux_launcher.py` - Check if still used or superseded by `ux_mirror_launcher.py`
- [ ] `launch_ux_mirror.py` - Check if still used
- [ ] `launch_ux_mirror.bat` - Check if still needed
- [ ] Consolidate to single launcher if possible

### 7. Build/Setup Scripts
**Status:** Multiple setup scripts
**Action:**
- [ ] `build_game.bat` / `build_game.sh` - Check if still needed
- [ ] `setup_autonomous_vm.bat` / `setup_autonomous_vm.sh` - Check if still needed
- [ ] `setup_launcher.bat` - Check if still needed
- [ ] `setup_mingw.bat` - Check if still needed
- [ ] Consolidate or document purpose

### 8. Documentation Files
**Status:** Many markdown files in root
**Action:**
- [ ] Move implementation reports to `docs/`:
  - `FINAL_IMPLEMENTATION_REPORT.md`
  - `IMPLEMENTATION_STATUS.md`
  - `BACKGROUND_AGENT_ANALYSIS_REPORT.md`
  - `PROMPT_ANALYSIS_SUMMARY.md`
  - `REPORT_BASED_ARCHITECTURE.md`
  - `CODE_CLEANUP_SUMMARY.md`
  - `OCR_IMPLEMENTATION_SUMMARY.md`
- [ ] Keep in root (user-facing):
  - `README.md`
  - `USAGE_GUIDE.md`
  - `IMAGE_RECOGNITION_ROADMAP.md`
  - `ARCHITECTURE_CHANGES.md`

### 9. Config Files
**Status:** Check for unused configs
**Action:**
- [ ] `config/orchestrator_config.json` - Already deleted ✅
- [ ] `config/schemas/orchestrator_schema.json` - Check if still needed
- [ ] `game_ux_config.json` - Keep (used by game testing)
- [ ] `vulkan_gameoflife_ux_config.json` - Check if still used
- [ ] `config.env` - Keep (main config)

### 10. Old Result Files
**Status:** Test output files
**Action:**
- [ ] `game_ux_results_20250604_171955.json` - Move to `ux_captures/` or remove
- [ ] `ux_captures/` - Keep but may want to archive old captures

## Phase 2: Code Quality Improvements

### 1. Unused Imports
**Action:**
- [ ] Run `pylint` or `flake8` to find unused imports
- [ ] Remove unused imports across codebase

### 2. Dead Code
**Action:**
- [ ] Find unreachable code
- [ ] Remove commented-out code blocks
- [ ] Remove unused functions/classes

### 3. Duplicate Code
**Action:**
- [ ] Identify code duplication
- [ ] Extract common functionality
- [ ] Create shared utilities

### 4. TODO/FIXME Comments
**Action:**
- [ ] Review all TODO/FIXME comments
- [ ] Either implement or create issues
- [ ] Remove outdated TODOs

## Phase 3: File Organization

### 1. Root Directory Cleanup
**Goal:** Reduce root directory clutter
**Action:**
- [ ] Move all examples to `examples/`
- [ ] Move all test files to `tests/`
- [ ] Move implementation docs to `docs/`
- [ ] Keep only essential files in root

### 2. Directory Structure
**Proposed Structure:**
```
ux-mirror/
├── src/              # Main source code
├── tests/            # All tests
├── examples/         # All examples and demos
├── docs/             # All documentation
├── config/           # Configuration files
├── core/             # Core modules
├── cli/              # CLI interface
├── ui/               # UI components
├── legacy/           # Archived legacy code (or remove)
├── README.md         # Main readme
├── requirements.txt  # Dependencies
└── ...               # Essential config files only
```

## Priority Levels

### High Priority (Do First)
1. Remove empty `agents/` directory
2. Move test files from root to `tests/`
3. Move example files to `examples/`
4. Move implementation docs to `docs/`

### Medium Priority
1. Review and consolidate launcher files
2. Review legacy directory
3. Check duplicate analysis files
4. Clean up unused configs

### Low Priority
1. Code quality improvements (unused imports, etc.)
2. Archive old result files
3. Consolidate build scripts

## Implementation Plan

### Week 1: File Organization
- Move examples to `examples/`
- Move tests to `tests/`
- Move docs to `docs/`
- Remove empty directories

### Week 2: Legacy Code Review
- Review legacy directory
- Remove or archive obsolete code
- Consolidate duplicate files

### Week 3: Code Quality
- Remove unused imports
- Remove dead code
- Fix TODO/FIXME items

### Week 4: Final Cleanup
- Review root directory
- Final documentation updates
- Create cleanup summary

## Success Metrics

- **Root directory files**: < 15 essential files
- **Unused code**: 0 dead code blocks
- **Test coverage**: All tests in `tests/` directory
- **Documentation**: All docs organized in `docs/`
- **Code quality**: No unused imports, no duplicate code

