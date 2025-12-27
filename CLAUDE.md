# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is **Fund Investigator** - a production Streamlit application for comprehensive single-fund performance analysis. It loads fund data from Cloudflare R2 (via DuckDB), calculates performance metrics, displays interactive visualizations, and provides SIP (Systematic Investment Plan) analysis with IRR calculations.

**Production App**: `fundinvestigator_app.py` - Single-page Fund Deepdive only
**WIP Features**: `/wip/app.py` - Multi-page app with Category Deepdive and Fund Universe (planned for future releases)

## Commands

### Running the Application

```bash
# Production app (Fund Investigator - Fund Deepdive only)
uv run streamlit run fundinvestigator_app.py

# WIP multi-page app (for development)
uv run streamlit run wip/app.py
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
1. **MktDataLoader** (src/data_loader.py): Connects to Cloudflare R2 via mktdata package
   - Uses mktdata's unified catalog system with DuckDB backend
   - Loads `mf_nav_daily`, `mf_schemes`, and `mf_benhcmark_daily` tables
   - Configuration managed via ~/.mktdata/config.yaml
   - Pivots long-format data to wide format for analysis
   - In-memory database with Streamlit caching (24-hour TTL by default)
   - Auto-refresh: Data automatically reloads from R2 after cache expires
   - Configurable cache TTL via `CACHE_TTL_HOURS` environment variable

2. **Fund Investigator App** (fundinvestigator_app.py): Single-page production entry point
   - Initializes R2DataLoader in session state
   - Renders fund_deepdive page directly (no multi-page navigation)
   - User selects single fund, benchmark, and optional comparison fund
   - Comprehensive analysis: SIP progression, integrated 4-row performance overview, rolling metrics, scatter plots, monthly/annual returns
   - Sidebar filtering: Plan type, categories (L1/L2), fund selection, benchmark selection, date range, parameters

3. **Fund Deepdive Page** (app_pages/fund_deepdive.py): Core analysis functionality
   - Comprehensive single-fund performance analysis (728 lines)
   - Integrated visualizations:
     - Section 1: KPI cards with SIP analysis table
     - Section 2A: Integrated 4-row performance overview subplot (SIP + Cumulative + Drawdown + Annual)
     - Section 2B: Performance metrics comparison table
     - Section 3: Rolling metrics analysis subplot
     - Section 4: Monthly returns heatmap
     - Section 5: Monthly returns scatter plot with regression
   - Side-by-side comparison with benchmark and optional comparison fund
   - SIP IRR calculations for ₹100/month investment simulation

4. **Metrics Module** (src/metrics.py): Calculates all performance metrics
   - Returns: cumulative return, CAGR
   - Risk: volatility, max drawdown, longest drawdown duration
   - Risk-adjusted: Sharpe, Sortino, Calmar, Omega ratios
   - Statistical: skewness, kurtosis, beta, correlation, R², alpha
   - Trading: win rate, consecutive streaks, gain/pain ratio
   - SIP: create_sip_progression_table (monthly investments, portfolio values, IRR calculation)

5. **Visualizations** (src/visualizations.py): Creates Plotly charts (30+ functions, 3429 lines)
   - create_performance_overview_subplot(): Integrated 4-row chart (SIP, Cumulative, Drawdown, Annual)
   - create_rolling_analysis_subplot(): 3-row rolling metrics (returns, Sharpe, volatility)
   - Monthly returns heatmap, scatter plots, distribution charts
   - Cumulative returns (linear and log scale), drawdown time series
   - All charts use consistent color scheme: Fund (#f59e0b amber), Benchmark (#6B7280 gray), Comparison (#10b981 green)

6. **Computation Cache** (src/computation_cache.py): Session-based performance optimization
   - Caches metrics, annual returns, monthly returns by fund+date hash
   - 60% performance improvement (Phase 1 completed Dec 24, 2024)
   - Smart cache invalidation when data selection changes
   - Session state-based, no persistence across sessions

7. **Helpers** (utils/helpers.py): Formatting utilities for metrics display

### Key Design Patterns

- **DuckDB + R2 Integration**: Uses DuckDB with httpfs extension to query parquet files directly from R2, creating local cached tables for performance
- **Long-to-Wide Pivot**: Data stored in long format (date, scheme_code, nav) is pivoted to wide format (date as index, schemes as columns) for return calculations
- **Streamlit Caching**: Heavy operations (data loading, table creation) use `@st.cache_data` and `@st.cache_resource` to avoid recomputation
- **Session-based Computation Caching**: Metrics, annual returns, monthly returns cached in session state with hash-based invalidation
- **Display Names**: Combines scheme_name and scheme_code as "Name | Code" for unique identification in UI
- **Integrated Subplots**: Performance overview combines 4 charts (SIP, Cumulative, Drawdown, Annual) into single unified visualization

### Environment Variables Required

The application requires R2 credentials and configuration in a `.env` file:
```
# R2 Connection (used by mktdata)
R2_ACCESS_KEY_ID=your_access_key
R2_SECRET_ACCESS_KEY=your_secret_key
R2_ENDPOINT_URL=your_account_id.r2.cloudflarestorage.com
R2_REGION=auto
R2_ACCOUNT_ID=your_account_id
R2_BUCKET_NAME=your_bucket_name

# Cache Configuration
CACHE_TTL_HOURS=24  # Data cache TTL in hours (default: 24)

# Note: R2 parquet file paths are configured in ~/.mktdata/config.yaml
```

### Constants

- `TRADING_DAYS = 252` (used throughout metrics calculations for annualization)
- Default risk-free rate: 2.49% (configurable in UI sidebar)

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

**mf_benchmark_daily_long**: Benchmark/index data (long format)
- Similar structure to NAV data

## Project Organization

### Production Code (actively maintained)
- `fundinvestigator_app.py` - Main production entry point
- `app_pages/fund_deepdive.py` - Core analysis page (728 lines)
- `src/` - All data, metrics, visualization, caching modules
- `utils/` - Helper functions

### Work in Progress (`/wip/`)
- Multi-page app with navigation (wip/app.py)
- Category Deepdive (wip/pages/category_deepdive.py) - Multi-fund comparison within category
- Fund Universe (wip/pages/fund_universe.py) - Portfolio-level analysis
- Notebooks for exploration (wip/notebooks/)

**Note on WIP features**: These use the same src/ and utils/ modules with absolute imports, so no import path changes are needed.

### Tests (`/tests/`)
- R2 data connectivity tests (test_r2_data.py)
- App functionality tests (test_updated_app.py)

### Documentation (`/docs/`)
- `backlog.md` - Feature roadmap and TODOs
- `code_flow.md` - Technical architecture documentation
- `sessions/` - Development session notes with detailed implementation history

## Recent Major Updates

**Dec 27, 2024:**
- Integrated SIP chart into performance overview subplot (4-row unified visualization)
- Adjusted annual returns chart height for better visibility
- Positioned IRR annotation at top-left of SIP section
- Reorganized project: production focus on Fund Investigator, moved WIP to /wip/
- Removed performance monitor UI from production code

**Dec 26, 2024:**
- Enhanced rolling analysis with standardized cumulative returns
- Added Alpha metric calculation
- Reorganized Fund Deepdive charts into integrated subplots
- SIP progression chart with IRR tracking

**Dec 24, 2024:**
- Phase 1 performance optimization completed (60% improvement)
- Session-based caching system for metrics, annual returns, monthly returns
- Smart cache invalidation on data selection changes

## Color Scheme (Consistent Across All Charts)

- **Fund/Strategy**: `#f59e0b` (Amber)
- **Benchmark**: `#6B7280` (Gray, dashed lines)
- **Comparison**: `#10b981` (Green)
- **Amount Invested** (SIP reference): `#9CA3AF` (Light gray, dashed)

## Performance Optimization Notes

- Initial data load from R2: ~2-3 seconds
- Cached metric calculations: <100ms (session-based caching)
- DuckDB in-memory tables provide fast query performance
- Streamlit caching reduces recomputation on page interactions
- Computation caching (Phase 1) achieved 60% performance improvement
