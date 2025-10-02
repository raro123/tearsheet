# Fund Performance Tearsheet

A comprehensive Streamlit application for analyzing mutual fund performance and comparing against benchmarks.

## Features

- Interactive performance charts (cumulative returns, drawdown, heatmaps)
- Comprehensive metrics (Sharpe, Sortino, Calmar, Omega ratios)
- Dynamic fund and benchmark selection
- Customizable date ranges
- Export metrics to CSV

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
# Clone or create the project directory
cd fund-tearsheet

# Install dependencies using uv
uv sync

# Create the data directory if it doesn't exist
mkdir -p data
```

## Usage

1. Place your parquet files in the `data/` folder
2. Run the application using uv:
   ```bash
   uv run streamlit run app.py
   ```
3. Open your browser to the provided URL (usually http://localhost:8501)

## Data Format

Your parquet files should have:
- A `date` column (datetime format) or datetime index
- Multiple columns for different funds (NAV values)

Example structure:
```
date        | Fund_A | Fund_B | Benchmark_60_40
2020-01-01  | 100.0  | 100.0  | 100.0
2020-01-02  | 100.5  | 99.8   | 100.2
```

## Project Structure

```
fund-tearsheet/
├── app.py                    # Main Streamlit application
├── pyproject.toml           # Project configuration and dependencies
├── uv.lock                  # Locked dependencies (auto-generated)
├── .python-version          # Python version specification
├── claude.md                # Claude AI context file
├── README.md                # This file
├── .streamlit/
│   └── config.toml         # Streamlit theme configuration
├── src/
│   ├── data_loader.py      # Data loading and preprocessing
│   ├── metrics.py          # Performance metrics calculations
│   └── visualizations.py   # Chart creation functions
├── utils/
│   └── helpers.py          # Helper utilities
└── data/                    # Your parquet files go here
```

## Configuration

- **Risk-free rate**: Default 2.49% (adjustable in the UI)
- **Trading days**: 252 days per year
- **Theme**: Customizable in `.streamlit/config.toml`

## Development

### Add new dependencies
```bash
uv add package-name
```

### Add development dependencies
```bash
uv add --dev package-name
```

### Run with specific Python version
```bash
uv run --python 3.11 streamlit run app.py
```

## Metrics Calculated

- **Return Metrics**: Cumulative Return, CAGR
- **Risk Metrics**: Volatility, Max Drawdown, Longest Drawdown
- **Risk-Adjusted Returns**: Sharpe Ratio, Sortino Ratio, Calmar Ratio, Omega Ratio
- **Statistical Measures**: Skewness, Kurtosis, Beta, Correlation, R²
- **Trading Statistics**: Win Rate, Max Consecutive Wins/Losses, Gain/Pain Ratio

## Troubleshooting

### No parquet files found
- Ensure your data files are in the `data/` folder
- Check that files have `.parquet` extension
- Verify the data folder path in the sidebar

### Data format errors
- Ensure your parquet file has a `date` column or datetime index
- Check that NAV values are numeric
- Verify at least 2 fund columns exist

### Performance issues
- Large files (>100MB) may take time to load initially
- Consider resampling very long time series (>10 years)
- Data loading is cached after first load

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit a Pull Request.