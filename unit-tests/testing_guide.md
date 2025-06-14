# Git Log Scraper Testing Guide

## Test Structure

```
tests/
├── unit/               # Unit tests for individual functions
├── integration/        # End-to-end workflow tests
├── fixtures/           # Test data files
├── conftest.py         # Shared pytest fixtures
└── testing_guide.md    # This document
```

## Running Tests

### Local Development

1. Install test requirements:
```bash
pip install pytest rich pytest-cov
```

2. Run all tests:
```bash
pytest -v --cov=scraplog --cov-report=term-missing
```

3. Run with rich output:
```bash
pytest -v --rich
```

### GitHub Actions

The project includes a GitHub Actions workflow that:
- Runs tests on Python 3.8+
- Generates coverage reports
- Fails if coverage < 80%

## Key Test Cases

### Core Functionality
- ✅ Email parsing (including IBM special cases)
- ✅ Commit block parsing
- ✅ File change detection
- ✅ Date filtering

### Network Construction
- ✅ Contributor aggregation
- ✅ Edge creation (collaboration detection)
- ✅ Graph property validation

### Filtering
- ✅ Email filtering
- ✅ Date range filtering
- ✅ File path filtering

## Adding New Tests

1. For new features:
   - Add unit tests in `tests/unit/`
   - Add integration tests if needed in `tests/integration/`

2. For bug fixes:
   - Add regression test reproducing the bug
   - Verify fix makes test pass

## Test Coverage

Maintain >80% coverage. Key areas:
- All parsing functions
- Network construction
- Filtering logic
- Error handling
