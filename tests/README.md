# Tests

This folder contains test files for verifying R2 data connectivity and application functionality.

## Test Files

### test_r2_data.py
Tests Cloudflare R2 bucket connectivity and data loading functionality:
- R2 credential validation
- DuckDB httpfs extension
- Parquet file reading from R2
- Table creation in DuckDB
- Data schema validation

### test_updated_app.py
Tests application data flow and functionality:
- Data loader initialization
- Returns calculation
- Metrics computation
- Caching functionality

## Running Tests

From the project root:

```bash
# Run R2 connectivity test
uv run python tests/test_r2_data.py

# Run application functionality test
uv run python tests/test_updated_app.py
```

## Requirements

Tests require:
- Valid `.env` file with R2 credentials
- Active internet connection for R2 access
- DuckDB with httpfs extension

## Note

These are exploratory test scripts, not a formal test suite. For production testing, consider:
- Migrating to pytest framework
- Adding unit tests for individual functions
- Adding integration tests for end-to-end workflows
- Implementing CI/CD pipeline with automated testing
