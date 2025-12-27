# Fund Investigator

A comprehensive Streamlit application for deep-dive analysis of individual mutual fund performance with benchmark comparisons, SIP calculations, and interactive visualizations.

## Features

### Core Analysis
- **Fund Deepdive**: Comprehensive single-fund performance analysis
  - Side-by-side comparison with benchmark and optional comparison fund
  - SIP portfolio growth simulation with IRR calculations (₹100/month)
  - Integrated 4-row performance overview (SIP, Cumulative Returns, Drawdown, Annual Returns)
  - Rolling metrics analysis (returns, Sharpe, volatility)
  - Monthly returns heatmap and scatter plots
  - Detailed performance metrics table

### Metrics Calculated
- **Return Metrics**: Cumulative Return, CAGR
- **Risk Metrics**: Volatility, Max Drawdown, Longest Drawdown Duration
- **Risk-Adjusted Returns**: Sharpe Ratio, Sortino Ratio, Calmar Ratio, Omega Ratio
- **Statistical Measures**: Skewness, Kurtosis, Beta, Correlation, R², Alpha
- **Trading Statistics**: Win Rate, Max Consecutive Wins/Losses, Gain/Pain Ratio
- **SIP Analysis**: Internal Rate of Return (IRR), Final Portfolio Value

### Interactive Features
- Dynamic fund and benchmark selection with category filters
- Optional comparison fund (compare 3 funds side-by-side)
- Customizable date ranges with period descriptions
- Adjustable risk-free rate
- Log scale toggle for cumulative returns
- Plan type filtering (All/Direct/Regular)

## Installation

This project uses [uv](https://github.com/astral-sh/uv) as the package manager.

### Install uv (if not already installed)
```bash
# On macOS and Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# On Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### Setup Project
```bash
# Clone the repository
cd fund-investigator

# Install dependencies using uv
uv sync

# Create .env file with R2 credentials
cp .env.example .env
# Edit .env with your Cloudflare R2 credentials
```

## Environment Configuration

Create a `.env` file in the project root with your Cloudflare R2 credentials:

```env
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

## Usage

### Run Production App (Fund Investigator)
```bash
uv run streamlit run fundinvestigator_app.py
```

Open your browser to the provided URL (usually http://localhost:8501)

### Run WIP Multi-Page App (Development)
```bash
uv run streamlit run wip/app.py
```

This version includes additional pages (Category Deepdive, Fund Universe) that are under development.

## Project Structure

```
fund-investigator/
├── fundinvestigator_app.py  # Production entry point (Fund Deepdive only)
├── README.md                 # This file
├── CLAUDE.md                 # Project instructions for AI assistant
├── pyproject.toml           # Project configuration and dependencies
├── uv.lock                  # Locked dependencies (auto-generated)
├── .python-version          # Python version specification (3.11)
├── .env                     # R2 credentials (not committed)
│
├── app_pages/
│   ├── fund_deepdive.py     # Core single-fund analysis page
│   └── __init__.py
│
├── src/
│   ├── data_loader.py       # R2 data connectivity via DuckDB
│   ├── metrics.py           # Performance metrics calculations
│   ├── visualizations.py    # Plotly chart components (30+ functions)
│   ├── computation_cache.py # Session-based caching (60% perf improvement)
│   └── shared_components.py # Reusable UI widgets
│
├── utils/
│   └── helpers.py           # Formatting utilities
│
├── docs/
│   ├── backlog.md           # Feature roadmap and TODOs
│   ├── code_flow.md         # Technical architecture documentation
│   └── sessions/            # Development session notes
│       ├── README.md        # Session index
│       └── *.md             # Detailed session documentation
│
├── tests/                   # Test files
│   ├── README.md            # Testing documentation
│   ├── test_r2_data.py      # R2 connectivity tests
│   └── test_updated_app.py  # App functionality tests
│
├── wip/                     # Work-in-progress features
│   ├── README.md            # WIP documentation
│   ├── app.py               # Multi-page app (future)
│   ├── main.py              # Placeholder entry point
│   ├── pages/               # Additional pages under development
│   │   ├── category_deepdive.py
│   │   └── fund_universe.py
│   └── notebooks/           # Exploration notebooks
│
├── data/
│   └── mf_data.db           # DuckDB local cache (auto-created)
│
└── .streamlit/
    └── config.toml          # Streamlit theme configuration
```

## Data Architecture

Fund Investigator loads data directly from Cloudflare R2 (S3-compatible) using DuckDB's httpfs extension:

1. **R2 Storage**: Parquet files stored in Cloudflare R2 bucket
2. **DuckDB Loading**: Direct parquet file reading via httpfs
3. **In-Memory Tables**: Data loaded into DuckDB in-memory database
4. **Caching**: 24-hour TTL with automatic refresh (configurable)
5. **Format Conversion**: Long-format data pivoted to wide format for analysis

### Data Schema

**mf_nav_daily_long** (NAV data in long format):
- `date`: datetime
- `scheme_code`: string
- `scheme_name`: string
- `nav`: float

**mf_scheme_metadata** (Fund metadata):
- `scheme_code`: string
- `scheme_name`: string
- `scheme_category_level1`: string (e.g., "Equity")
- `scheme_category_level2`: string (e.g., "Large Cap")

**mf_benchmark_daily_long** (Benchmark data in long format):
- Similar structure to NAV data

## Configuration

- **Risk-free rate**: Default 2.49% (adjustable in sidebar)
- **Trading days**: 252 days per year (used for annualization)
- **Cache TTL**: 24 hours (configurable via CACHE_TTL_HOURS env var)
- **Theme**: Customizable in `.streamlit/config.toml`
- **Log scale**: Default enabled for cumulative returns

## Development

### Add new dependencies
```bash
uv add package-name
```

### Add development dependencies
```bash
uv add --dev package-name
```

### Code formatting (if dev dependencies installed)
```bash
uv run black .
uv run ruff check .
```

## Performance

**Optimization History:**
- **Phase 1 (Dec 24, 2024)**: Session-based caching implementation
  - 60% performance improvement
  - Metrics, annual returns, monthly returns caching
  - Smart cache invalidation on data changes

**Current Performance:**
- Initial data load: ~2-3 seconds (from R2)
- Cached operations: <100ms
- Metric calculations: Cached per fund/date selection

## Troubleshooting

### R2 Connection Issues
- Verify `.env` file has correct R2 credentials
- Check R2_ENDPOINT_URL format (should be account_id.r2.cloudflarestorage.com)
- Ensure R2 bucket and file paths are correct
- Verify internet connectivity

### Data Loading Errors
- Check parquet file schema matches expected format
- Verify date columns are in datetime format
- Ensure scheme_code and scheme_name columns exist

### Performance Issues
- Default 24-hour cache should handle most scenarios
- For frequent data updates, reduce CACHE_TTL_HOURS
- Large date ranges may take longer to process initially

## Future Features (in /wip/)

- **Category Deepdive**: Compare multiple funds within the same category
- **Fund Universe**: Portfolio-level analysis and fund screening
- **Multi-page navigation**: Unified platform for all analysis types

See `/docs/backlog.md` for detailed feature roadmap.

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.

For questions or issues, please open an issue on GitHub.
