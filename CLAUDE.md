# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a Streamlit application for analyzing mutual fund performance. It loads fund data from Cloudflare R2 (via DuckDB), calculates comprehensive performance metrics, and displays interactive visualizations comparing funds against benchmarks.

## Commands

### Running the Application
```bash
uv run streamlit run app.py
```

### Development Setup
```bash
# Install dependencies
uv sync

# Add new dependency
uv add package-name

# Add dev dependency
uv add --dev package-name
```

### Code Quality (if dev dependencies installed)
```bash
# Format code
uv run black .

# Lint code
uv run ruff check .
```

## Architecture

### Data Flow
1. **R2DataLoader** (src/data_loader.py): Connects to Cloudflare R2 via DuckDB, creates in-memory tables from parquet files
   - Uses DuckDB's httpfs extension with S3-compatible R2 API
   - Loads `mf_nav_daily_long` (NAV data in long format), `mf_scheme_metadata`, and `mf_benchmark_daily_long` tables
   - Pivots long-format data to wide format for analysis
   - In-memory database with Streamlit caching (24-hour TTL by default)
   - Auto-refresh: Data automatically reloads from R2 after cache expires
   - Configurable cache TTL via `CACHE_TTL_HOURS` environment variable

2. **Main App** (app.py): Streamlit UI orchestrating data loading, filtering, and visualization
   - User selects fund categories (Level 1 & 2), specific funds, and date ranges
   - Loads filtered NAV data and converts to returns series
   - Calculates metrics for strategy and benchmark
   - Displays summary cards, charts, and detailed metrics table

3. **Metrics Module** (src/metrics.py): Calculates all performance metrics
   - Returns: cumulative return, CAGR
   - Risk: volatility, max drawdown, longest drawdown duration
   - Risk-adjusted: Sharpe, Sortino, Calmar, Omega ratios
   - Statistical: skewness, kurtosis, beta, correlation, R²
   - Trading: win rate, consecutive streaks, gain/pain ratio

4. **Visualizations** (src/visualizations.py): Creates Plotly charts
   - Cumulative returns (linear and log scale)
   - Drawdown time series
   - Monthly returns heatmap
   - Rolling Sharpe ratio

5. **Helpers** (utils/helpers.py): Formatting utilities for metrics display

### Key Design Patterns

- **DuckDB + R2 Integration**: Uses DuckDB with httpfs extension to query parquet files directly from R2, creating local cached tables for performance
- **Long-to-Wide Pivot**: Data stored in long format (date, scheme_code, nav) is pivoted to wide format (date as index, schemes as columns) for return calculations
- **Streamlit Caching**: Heavy operations (data loading, table creation) use `@st.cache_data` and `@st.cache_resource` to avoid recomputation
- **Display Names**: Combines scheme_name and scheme_code as "Name |Code" for unique identification in UI

### Environment Variables Required

The application requires R2 credentials and configuration in a `.env` file:
```
# R2 Connection
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_ENDPOINT_URL=your_account_id.r2.cloudflarestorage.com
R2_REGION=auto
R2_ACCOUNT_ID=your_account_id
R2_BUCKET_NAME=your_bucket_name
R2_NAV_DATA_PATH=path/to/nav_data.parquet
R2_MF_METADATA_PATH=path/to/metadata.parquet
R2_MF_BENCHMARK_DATA_PATH=path/to/benchmark_data.parquet

# Cache Configuration
CACHE_TTL_HOURS=24  # Data cache TTL in hours (default: 24)
```

### Constants

- `TRADING_DAYS = 252` (used throughout metrics calculations for annualization)
- Default risk-free rate: 2.49% (configurable in UI)

### Data Schema

**mf_nav_daily_long**: Long format NAV data
- `date`: datetime
- `scheme_code`: string
- `scheme_name`: string
- `nav`: float

**mf_scheme_metadata**: Fund metadata
- `scheme_code`: string
- `scheme_name`: string
- `scheme_category_level1`: string (e.g., "Equity")
- `scheme_category_level2`: string (e.g., "Large Cap")
