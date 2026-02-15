# Test Plan

> This document describes the testing strategy for this project. It serves as the single source of truth for testing decisions and rationale.

## Overview

**Project:** ap-move-light-to-data
**Primary functionality:** Move complete directory trees containing light frames and their calibration to the data directory atomically when all required calibration is present and self-contained.

## Testing Philosophy

This project follows the [ap-base Testing Standards](https://github.com/jewzaam/ap-base/blob/main/standards/standards/testing.md) and [CLI Testing Standards](https://github.com/jewzaam/ap-base/blob/main/standards/standards/cli-testing.md).

Key testing principles for this project:

- **TDD for bug fixes** - All bugs must have a failing test before implementation
- **Business logic isolation** - Core processing functions tested independently from CLI and I/O
- **Integration testing** - Verify complete workflows with realistic directory structures
- **CLI argument mapping** - Prevent argparse attribute name typos through dedicated tests

## Test Categories

### Unit Tests

Tests for isolated functions with mocked dependencies.

| Module | Function | Test Coverage | Notes |
|--------|----------|---------------|-------|
| `move_lights_to_data.py` | `build_search_dirs()` | Path traversal from directory to source | Core matching logic |
| `move_lights_to_data.py` | `find_all_light_directories()` | Directory discovery with pattern matching | Uses tmp_path fixtures |
| `move_lights_to_data.py` | `get_metadata()` | Caching of FITS metadata | Mock filesystem access |
| `move_lights_to_data.py` | `find_matching_files()` | Calibration frame matching | Various match scenarios |
| `move_lights_to_data.py` | `print_summary()` | Summary output with scale_darks variations | Both modes tested |
| `config.py` | Constants and configuration | Values match documentation | |
| `matching.py` | File matching utilities | Pattern matching edge cases | |

### Integration Tests

Tests for multiple components working together.

| Workflow | Components | Test Coverage | Notes |
|----------|------------|---------------|-------|
| Complete tree move | Directory search, metadata, matching, move | End-to-end with realistic directory tree | Uses tmp_path |
| Missing calibration handling | Detection of missing darks/flats/bias | Skipping behavior | |
| Metadata caching | get_metadata + process flow | Verifies single call per source dir | Performance critical |

### CLI/Main Function Tests

**Purpose:** Verify command-line argument parsing and main() entry point integration.

**Standard:** Follows [CLI Testing Standards](../../standards/standards/cli-testing.md)

**Coverage:**
- Argument name mapping (prevents args.attribute_name typos like args.scale_darks vs args.scale_dark)
- Each CLI flag individually with kwargs verification
- Multiple flags combined
- Error handling for invalid arguments
- Exit code validation

**Pattern:**
- Mocks sys.argv to simulate CLI invocation
- Mocks business logic function (process_light_directories) to isolate argparse
- Verifies call_args to catch attribute name mismatches

**Rationale:** Prevents runtime AttributeError from CLI argument typos. Catches bugs that
linters, type checkers, and unit tests cannot detect. Regression test for args.scale_darks
vs args.scale_dark bug fixed in Phase 2.

**Test File:** `tests/test_move_lights_to_data.py::TestMainCLIArguments`

**Test Coverage:**
- `test_scale_dark_flag_mapping` - Regression test for --scale-dark attribute bug
- `test_scale_dark_disabled` - Test --no-scale-dark flag
- `test_scale_dark_default` - Test default value when flag omitted
- `test_dryrun_flag` - Verify --dryrun parameter mapping
- `test_quiet_flag` - Verify --quiet parameter and print_summary behavior
- `test_debug_flag` - Verify --debug parameter mapping
- `test_path_pattern_flag` - Verify custom --path-pattern value
- `test_multiple_flags_combined` - Test flag interactions
- `test_error_exit_code` - Verify EXIT_ERROR when process returns errors

## Untested Areas

| Area | Reason Not Tested |
|------|-------------------|
| Physical file I/O | Integration tests use tmp_path but don't test actual FITS file reading - mocked in unit tests |
| ap_common.move_file() | External dependency, tested in ap-common |
| Logging output details | Logging tested at setup level, not specific message content |

## Bug Fix Testing Protocol

All bug fixes to existing functionality **must** follow TDD:

1. Write a failing test that exposes the bug
2. Verify the test fails before implementing the fix
3. Implement the fix
4. Verify the test passes
5. Verify reverting the fix causes the test to fail again
6. Commit test and fix together with issue reference

### Regression Tests

| Issue | Test | Description |
|-------|------|-------------|
| args.scale_darks AttributeError | `test_scale_dark_flag_mapping` | Typo in argparse attribute name (args.scale_darks vs args.scale_dark) |

## Coverage Goals

**Target:** 80%+ line coverage

**Philosophy:** Coverage measures completeness, not quality. A test that executes code without meaningful assertions provides no value. Focus on:

- Testing behavior, not implementation details
- Covering edge cases and error conditions
- Ensuring assertions verify expected outcomes

**Current Coverage:** See [Coverage Badge](https://github.com/jewzaam/ap-move-light-to-data/actions/workflows/coverage.yml)

## Running Tests

```bash
# Run all tests
make test

# Run with coverage
make coverage

# Run specific test
pytest tests/test_move_lights_to_data.py::TestClass::test_function

# Run CLI tests specifically
pytest tests/test_move_lights_to_data.py::TestMainCLIArguments -v
```

## Test Data

Test data is:
- Generated programmatically in fixtures (tmp_path)
- Minimal FITS metadata mocked via mocker.patch
- No binary FITS files stored in repository

**No Git LFS** - all test data must be small (< 100KB) or generated.

## Maintenance

When modifying this project:

1. **Adding features**: Add tests for new functionality after implementation
2. **Fixing bugs**: Follow TDD protocol above (test first, then fix)
3. **Refactoring**: Existing tests should pass without modification (behavior unchanged)
4. **Removing features**: Remove associated tests
5. **Adding CLI flags**: Add CLI tests following [CLI Testing Standards](../../standards/standards/cli-testing.md)

## Changelog

| Date | Change | Rationale |
|------|--------|-----------|
| 2026-02-14 | Initial TEST_PLAN.md with CLI testing section | Document existing test strategy and new CLI testing standard |
| 2026-02-14 | Add regression test for args.scale_dark bug | TDD fix for AttributeError at runtime |
