# Fund Tearsheet - Claude Context

## Project Overview
This is a Streamlit application for comprehensive mutual fund performance analysis and benchmarking. It provides interactive visualizations and detailed metrics for comparing fund performance against benchmarks.

## Architecture

### Directory Structure
- `app.py` - Main Streamlit application entry point
- `src/` - Core business logic modules
  - `data_loader.py` - Data loading and preprocessing functions
  - `metrics.py` - Performance metrics calculations (Sharpe, Sortino, etc.)
  - `visualizations.py` - Plotly chart generation functions
- `utils/` - Helper utilities and formatting functions
- `data/` - Directory for parquet data files (user's fund NAV data)
- `.streamlit/` - Streamlit configuration

### Key Components

#### Data Flow
1. User uploads/selects parquet file with fund NAV data
2. Data is loaded and cached via `src/data_loader.py`
3. Daily returns are calculated from NAV series
4. Metrics are computed via `src/metrics.py`
5. Visualizations are generated via `src/visualizations.py`
6. Results displayed in Streamlit UI

#### Performance Metrics Calculated
- **Return Metrics**: Cumulative Return, CAGR
- **Risk Metrics**: Volatility, Max Drawdown, Downside Deviation
- **Risk-Adjusted**: Sharpe Ratio, Sortino Ratio, Calmar Ratio, Omega Ratio
- **Statistical**: Skewness, Kurtosis, Beta, Correlation, R²
- **Trading**: Win Rate, Max Consecutive Wins/Losses, Gain/Pain Ratio

### Data Format Requirements
Parquet files must contain:
- A `date` column (datetime) or datetime index
- Multiple columns for different funds (NAV values as floats)

Example:
```
date        | Fund_A | Fund_B | Benchmark_60_40
2020-01-01  | 100.0  | 100.0  | 100.0
2020-01-02  | 100.5  | 99.8   | 100.2
```

### Key Technical Decisions

1. **Why Streamlit**: Quick interactive dashboards, good for data apps
2. **Why Plotly**: Interactive charts with hover tooltips, professional look
3. **Why Parquet**: Efficient columnar format, good for time-series data
4. **Package Manager**: Using `uv` for fast, reliable dependency management

### Configuration
- Risk-free rate: Default 2.49% (configurable in UI)
- Trading days per year: 252
- Default rolling window: 252 days (1 year)

### Common Tasks

#### Adding New Metrics
1. Add calculation function to `src/metrics.py`
2. Add to `calculate_all_metrics()` return dict
3. Update `utils/helpers.py` formatting if needed
4. Metric will automatically appear in UI table

#### Adding New Charts
1. Create chart function in `src/visualizations.py`
2. Import in `app.py`
3. Add to appropriate column/section in main()

#### Modifying UI Layout
- Main layout is 2-column: charts (left) and metrics table (right)
- Summary metrics displayed as 4 cards at top
- Additional charts in 2-column grid at bottom
- All controlled in `app.py` main() function

### Dependencies
- **streamlit**: Web app framework
- **pandas**: Data manipulation
- **numpy**: Numerical computations
- **plotly**: Interactive visualizations
- **scipy**: Statistical functions
- **pyarrow**: Parquet file reading

### Running the App
```bash
uv run streamlit run app.py
```

### Testing Strategy
- Test with sample fund data covering various market conditions
- Verify metrics match manual calculations
- Check edge cases: single fund, missing data, date range filters

### Known Limitations
- Assumes daily NAV data (no intraday)
- No transaction cost modeling
- No benchmark construction tools
- Limited to single currency analysis

### Future Enhancements
- [ ] Export tearsheet as PDF
- [ ] Multi-fund comparison (>2 funds)
- [ ] Factor attribution analysis
- [ ] Monte Carlo simulations
- [ ] Custom benchmark construction
- [ ] Portfolio optimization tools

### Debugging Tips
- Check data folder path if files not loading
- Verify parquet file has datetime index or 'date' column
- Ensure at least 2 funds in data for comparison
- Check browser console for JavaScript errors in Plotly charts

### Performance Considerations
- Data loading is cached via @st.cache_data
- Large files (>100MB) may slow initial load
- Consider resampling for very long time series (>10 years daily data)

### Code Style
- Follow PEP 8 conventions
- Use type hints where helpful
- Docstrings for all public functions
- Line length: 100 characters (Black/Ruff configured)