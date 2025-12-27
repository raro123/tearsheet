# Fund Investigator - Code Flow Documentation

## Table of Contents
1. [Application Architecture](#application-architecture)
2. [Entry Point and Initialization](#entry-point-and-initialization)
3. [Data Layer](#data-layer)
4. [UI Components Layer](#ui-components-layer)
5. [Page Flow - Category Deepdive](#page-flow---category-deepdive)
6. [Metrics Calculation](#metrics-calculation)
7. [Visualization Layer](#visualization-layer)
8. [Key Design Patterns](#key-design-patterns)

---

## 1. Application Architecture

### Production (Fund Investigator)

```
fundinvestigator_app.py (Production Entry Point)
└── app_pages.fund_deepdive.render()
    └── session_state.data_loader (MktDataLoader singleton)

Single-page focused analysis:
- Fund Deepdive: Comprehensive single-fund performance analysis
  - SIP calculations with IRR
  - Integrated 4-row performance overview
  - Rolling metrics analysis
  - Monthly/annual returns analysis
```

### Work in Progress (Multi-Page App)

Located in `/wip/` directory for future development:

```
wip/app.py (WIP Multi-Page Entry Point)
├── session_state.data_loader (MktDataLoader singleton)
└── Navigation
    ├── Page 1: Fund Universe (wip/pages/fund_universe.py)
    ├── Page 2: Category Deepdive ⭐ (wip/pages/category_deepdive.py) - DEFAULT
    └── Page 3: Fund Deepdive (app_pages/fund_deepdive.py) - Shared with production
```

### Shared Data Layer (src/)

Used by both production and WIP apps:

```
src/
├── data_loader.py (MktDataLoader class)
├── metrics.py (Performance calculations)
├── visualizations.py (Plotly chart functions - 30+ functions)
├── computation_cache.py (Session-based caching - 60% perf improvement)
└── shared_components.py (Reusable UI widgets)
```

**Note**: The remainder of this document describes the multi-page architecture (in `/wip/`). The production Fund Investigator app uses the same data layer and components but with a simplified single-page structure.

---

## 2. Entry Point and Initialization

### File: `app.py`

**Purpose**: Application entry point, configuration, and navigation setup

**Flow**:

```python
1. Set page configuration (wide layout, icon, title)
2. Apply custom CSS
3. Initialize data loader (singleton pattern):
   ├── Check if 'data_loader' exists in st.session_state
   ├── If not: Create MktDataLoader instance
   ├── Call create_db_tables() to load data from R2
   └── Store in st.session_state for cross-page access
4. Create navigation with 3 pages
5. Run selected page (Category Deepdive is default)
```

**Key Code**:
```python
# Lines 41-48: Singleton initialization
if 'data_loader' not in st.session_state:
    data_loader = get_data_loader()  # Creates MktDataLoader
    data_loader.create_db_tables()   # Loads data from R2
    st.session_state.data_loader = data_loader

# Lines 60-64: Navigation setup
pg = st.navigation([
    st.Page(page_fund_universe.render, ...),
    st.Page(category_deepdive_page, ..., default=True),  # DEFAULT PAGE
    st.Page(fund_deepdive_page, ...)
])
pg.run()
```

---

## 3. Data Layer

### File: `src/data_loader.py`

**Purpose**: Interface between Streamlit app and Cloudflare R2 data storage via DuckDB

**Architecture**: In-memory DuckDB database with HTTP access to R2 parquet files

### 3.1 Connection Setup

**Flow** (`__init__` → `_setup_connection`):

```python
1. Create DuckDB in-memory connection (':memory:')
2. Install and load httpfs extension (for S3/R2 support)
3. Load environment variables from .env:
   ├── R2_ACCESS_KEY_ID
   ├── R2_SECRET_ACCESS_KEY
   ├── R2_ENDPOINT_URL
   ├── R2_REGION
   └── R2_ACCOUNT_ID
4. Create DuckDB SECRET for R2 authentication
```

**Key Code** (lines 22-52):
```python
self.conn = duckdb.connect(':memory:')
self.conn.execute("INSTALL httpfs;")
self.conn.execute("LOAD httpfs;")
self.conn.execute(f"""
    CREATE OR REPLACE SECRET r2_secret (
        TYPE S3,
        KEY_ID '{r2_config['key_id']}',
        ...
    )
""")
```

### 3.2 Data Loading with TTL Caching

**Method**: `create_db_tables()` (lines 72-121)

**Caching**: `@st.cache_resource(ttl=86400)` - 24 hours default

**Flow**:
```python
1. Check if connection exists
2. Get cache TTL from environment (default 24 hours)
3. Create 3 in-memory tables from R2 parquet files:
   ├── mf_nav_daily_long (NAV data in long format)
   ├── mf_scheme_metadata (fund information)
   └── mf_benchmark_daily_long (benchmark index data)
4. Log data freshness (latest NAV date)
```

**Data Refresh**:
- Automatic: Cache expires after TTL, data reloads from R2
- Manual: Clear Streamlit cache or restart app

### 3.3 Key Methods

| Method | Caching | Purpose | Returns |
|--------|---------|---------|---------|
| `get_available_funds()` | `@st.cache_data` | Get all growth funds with metadata | DataFrame with scheme info |
| `load_fund_data()` | `@st.cache_data` | Load NAV data for selected funds | Wide-format DataFrame (date × funds) |
| `load_benchmark_data()` | `@st.cache_data` | Load benchmark index data | Series (date → value) |
| `get_benchmark_options()` | `@st.cache_data` | Get available benchmark indices | List of index names |
| `get_data_date_range()` | `@st.cache_data` | Get min/max date in dataset | (min_date, max_date) |
| `calculate_returns()` | No cache | Calculate daily returns from NAV | Series of returns |

### 3.4 Data Format Transformation

**Long to Wide Pivot** (lines 178-179):

```python
# Input (long format):
date       | scheme_code | scheme_name | nav
2024-01-01 | 101         | Fund A      | 100
2024-01-01 | 102         | Fund B      | 50

# Output (wide format):
date       | Fund A - Direct |101 | Fund B - Direct |102
2024-01-01 | 100                  | 50

# Code:
df_wide = df_long.pivot(index='date', columns='display_name', values='nav')
```

**Display Name Format**: `{scheme_name} - {plan_type} |{scheme_code}`

---

## 4. UI Components Layer

### File: `src/shared_components.py`

**Purpose**: Reusable Streamlit widgets for consistent UX across pages

### 4.1 Component Catalog

| Component | Function | Returns | Usage |
|-----------|----------|---------|-------|
| Date Range Selector | `render_date_range_selector()` | (start_date, end_date, period_desc) | Smart defaults: 1Y/3Y/5Y/10Y/Max/Custom |
| Category Filters | `render_category_filters()` | (level1, level2) | Hierarchical dropdown: Type → Category |
| Plan Type Filter | `render_plan_type_filter()` | "All"/"Direct"/"Regular" | Radio buttons |
| Fund Multi-Select | `render_fund_multiselect()` | (selected_funds, mode) | Include/Exclude mode with multiselect |
| Risk-Free Rate | `render_risk_free_rate()` | float (decimal) | Number input, default 2.49% |

### 4.2 Helper Functions

```python
# Get final fund list based on inclusion/exclusion mode
get_final_fund_list(all_funds, selected_funds, selection_mode)
  └── Returns: filtered fund list

# Filter by plan type
filter_funds_by_plan_type(funds_df, plan_type)
  └── Returns: filtered DataFrame
```

---

## 5. Page Flow - Category Deepdive

### File: `pages/category_deepdive.py`

**Purpose**: Compare multiple funds within a category with visualizations and metrics

### 5.1 Execution Flow

```
render(data_loader)
│
├─[SIDEBAR: Filter Configuration]───────────────────────────
│   │
│   ├──1. Get all funds from data_loader
│   ├──2. Render category filters (Level 1 & Level 2)
│   ├──3. Render plan type filter (Direct/Regular/All)
│   ├──4. Filter funds by category + plan type
│   ├──5. Render fund multi-select (Include/Exclude mode)
│   ├──6. Calculate final fund list
│   ├──7. Render benchmark selection (index type, category)
│   ├──8. Render date range selector
│   └──9. Render risk-free rate input
│
├─[MAIN: Data Loading]──────────────────────────────────────
│   │
│   ├──1. Load fund NAV data (wide format DataFrame)
│   ├──2. Load benchmark data (Series)
│   ├──3. Calculate returns for all funds
│   ├──4. Calculate metrics for all funds
│   └──5. Calculate benchmark metrics
│
├─[MAIN: Summary Cards]─────────────────────────────────────
│   │
│   └──Display: Avg CAGR, Avg Sharpe, Avg Volatility, Avg Max DD
│
├─[MAIN: Visualizations]────────────────────────────────────
│   │
│   ├──Chart 1: Equity Curves (Monthly Resolution)
│   │   └──create_category_equity_curves()
│   │
│   ├──Chart 2: Annual Returns Subplots (Vertical Stack)
│   │   └──create_annual_returns_subplots()
│   │
│   ├──Chart 3: Bubble Scatter (3 Metrics)
│   │   └──create_bubble_scatter_chart()
│   │
│   ├──Chart 4: Rolling Metrics
│   │   └──create_rolling_metric_chart()
│   │
│   └──Chart 5: Performance Ranking Grid
│       └──create_performance_ranking_grid()
│
└─[MAIN: Metrics Tables]────────────────────────────────────
    │
    ├──Benchmark Table (Fixed Reference)
    │   ├──Annual Return Trend (Line Chart Column)
    │   ├──Data Range (Text Column)
    │   └──Metrics (formatted columns)
    │
    ├──Fund Performance Table (Sortable)
    │   ├──Annual Return Trend (Line Chart Column)
    │   ├──Data Range (Text Column)
    │   └──Metrics (formatted columns)
    │
    └──Download Button (CSV export)
```

### 5.2 Data Processing Pipeline

**Step-by-Step Data Transformation**:

```python
# 1. User selects filters → final_fund_list
final_fund_list = ["Fund A - Direct |101", "Fund B - Direct |102", ...]

# 2. Load NAV data (wide format)
df = data_loader.load_fund_data(start_date, end_date, final_fund_list)
# Result:
#    date       | Fund A - Direct |101 | Fund B - Direct |102
#    2024-01-01 | 100                  | 50

# 3. Calculate returns for each fund
for fund_name in final_fund_list:
    fund_nav = df[fund_name].dropna()
    fund_returns = calculate_returns(fund_nav)  # pct_change()
    funds_returns[fund_name] = fund_returns

# 4. Calculate metrics for each fund
for fund_name, returns in funds_returns.items():
    metrics = calculate_all_metrics(returns, benchmark_returns, risk_free_rate)
    metrics['Fund'] = fund_name
    funds_metrics.append(metrics)

# 5. Create metrics DataFrame
metrics_df = pd.DataFrame(funds_metrics)
```

### 5.3 Table Enhancements

**Annual Return Trend Column** (lines 444-482):

```python
# For each fund:
1. Resample returns to year-end: returns.resample('YE')
2. Calculate annual returns: (1 + x).prod() - 1
3. Align to common year range: [2020, 2021, 2022, 2023, 2024, 2025]
4. Fill missing years with 0 (not NaN - important for LineChartColumn)
5. Store as list for that fund

# Display as inline line chart:
st.column_config.LineChartColumn('Annual Return Trend', y_min=-50, y_max=100)
```

**Data Range Column** (lines 467-476):

```python
# Track years with actual data
years_with_data = [2020, 2022, 2023, 2025]  # Example (no 2021, 2024)

# Format:
if first_year == last_year:
    data_range = "2025"
else:
    data_range = "2020-2025"  # Shows range, not gaps
```

---

## 6. Metrics Calculation

### File: `src/metrics.py`

**Purpose**: Calculate comprehensive performance metrics

### 6.1 Constants

```python
TRADING_DAYS = 252  # Used for annualization
```

### 6.2 Metrics Categories

**Returns Metrics**:
- `calculate_cumulative_return()` - Total return over period
- `calculate_cagr()` - Compound Annual Growth Rate
- `calculate_expected_returns()` - Daily/Monthly/Annual expected returns

**Risk Metrics**:
- `calculate_volatility()` - Annualized standard deviation
- `calculate_max_drawdown()` - Maximum peak-to-trough decline
- `calculate_average_drawdown()` - Average drawdown depth
- `calculate_longest_drawdown()` - Longest drawdown period (days)
- `calculate_var_cvar()` - Value at Risk and Conditional VaR

**Risk-Adjusted Metrics**:
- `calculate_sharpe_ratio()` - Excess return per unit of volatility
- `calculate_sortino_ratio()` - Excess return per unit of downside volatility
- `calculate_calmar_ratio()` - CAGR divided by max drawdown
- `calculate_omega_ratio()` - Probability-weighted gains/losses

**Statistical Metrics**:
- `calculate_beta_correlation()` - Beta, correlation, R² vs benchmark
- `calculate_tail_ratios()` - Upper/lower tail behavior

**Trading Metrics**:
- `calculate_win_rate()` - Percentage of positive days
- `calculate_consecutive_streaks()` - Max winning/losing streaks
- `calculate_gain_pain_ratio()` - Total gains / total losses

### 6.3 Calculation Formulas

**CAGR** (lines 11-17):
```python
total_return = (1 + returns).prod() - 1
n_years = len(returns) / 252
cagr = (1 + total_return) ** (1 / n_years) - 1
```

**Sharpe Ratio** (lines 23-27):
```python
excess_returns = returns.mean() * 252 - risk_free_rate
volatility = returns.std() * sqrt(252)
sharpe = excess_returns / volatility
```

**Max Drawdown** (lines 36-41):
```python
cumulative = (1 + returns).cumprod()
running_max = cumulative.expanding().max()
drawdown = (cumulative - running_max) / running_max
max_dd = drawdown.min()
```

---

## 7. Visualization Layer

### File: `src/visualizations.py`

**Purpose**: Create interactive Plotly charts

### 7.1 Key Visualizations

**1. Category Equity Curves** (`create_category_equity_curves`)

```python
Flow:
1. Resample all returns to monthly (ME = Month End)
   └── monthly_returns = returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
2. Calculate cumulative returns: (1 + monthly_returns).cumprod()
3. Create dual-axis chart:
   ├── Linear scale (default)
   └── Log scale (toggle button)
4. Add benchmark as reference line
```

**2. Annual Returns Subplots** (`create_annual_returns_subplots`)

```python
Flow:
1. Extract year range from start_date to end_date
2. For each year:
   ├── Calculate annual returns for all funds
   ├── Create subplot (row) with horizontal bars
   ├── Add benchmark as vertical line
   └── Add data labels on bar tops
3. Stack subplots vertically with minimal spacing (0.02)
4. Use mono-color (#3b82f6) for all bars
5. No legend (x-axis labels identify funds)
```

**3. Performance Ranking Grid** (`create_performance_ranking_grid`)

```python
Flow:
1. For each year in range:
   ├── For each fund:
   │   ├── Extract year's returns
   │   ├── Calculate metrics: CAGR, Sharpe, Volatility, Max DD, Annual Return
   │   └── Store in fund_year_data list
   └── Add benchmark data

2. Create DataFrame from fund_year_data

3. Rank funds by CAGR within each year:
   └── df['Rank'] = df.groupby('Year')['CAGR'].rank(ascending=False)

4. Create pivot table (Rank × Year → CAGR for heatmap coloring):
   └── pivot_cagr = df.pivot(index='Rank', columns='Year', values='CAGR')

5. Create heatmap with annotations:
   ├── Color scale: Cyan (#a5f3fc) → Blue (#3b82f6) → Dark Blue (#1e40af)
   ├── Cell annotations:
   │   ├── Fund name (bold, truncated)
   │   ├── Ann Ret: {annual_return}%
   │   ├── CAGR: {cagr}%
   │   ├── SR: {sharpe} | DD: {max_dd}%
   │   └── Vol: {volatility}%
   └── Font color: White for |CAGR| > 10%, black otherwise

6. Layout:
   ├── X-axis: Years
   ├── Y-axis: Rank (1 = best)
   └── No gaps (consecutive ranks within each year)
```

**Ranking Modes**:
- **Annual**: Rank by performance in that specific year only
- **Cumulative**: Rank by cumulative performance from start_date to year-end

**4. Rolling Metrics Chart** (`create_rolling_metric_chart`)

```python
Flow:
1. Convert returns to monthly resolution
2. Convert window from days to months (e.g., 252 days → 12 months)
3. For each fund:
   ├── Calculate rolling metric (Return/Volatility/Sharpe/Drawdown)
   ├── Drop NaN values (insufficient data periods)
   └── Add trace to chart
4. Add benchmark as reference
5. Update annualization factor from 252 (days/year) to 12 (months/year)
```

### 7.2 Chart Design Patterns

**Common Features**:
- Template: `plotly_white` (clean, minimal)
- Hover mode: `x unified` (vertical line with all values)
- Legends: Positioned at bottom for multi-line charts
- Color scheme: Consistent across charts (blue for benchmark, varied for funds)

**Responsive Design**:
- `use_container_width=True` - Adapts to screen size
- Height specified in pixels for consistency

---

## 8. Key Design Patterns

### 8.1 Caching Strategy

**Three-Tier Caching**:

| Level | Decorator | Scope | Use Case |
|-------|-----------|-------|----------|
| Resource | `@st.cache_resource` | Global, shared | Data loader instance, DB connection |
| Data | `@st.cache_data(ttl=86400)` | Per-session, 24hr | DB tables, fund lists |
| Data | `@st.cache_data` | Per-session, permanent | Derived data (filtered funds) |

**Cache Flow**:
```
App Start
├── @st.cache_resource: Create MktDataLoader (once per deployment)
├── @st.cache_resource(ttl=24h): Load R2 data into DuckDB (refreshes daily)
└── @st.cache_data: Query results (per unique parameter set)
```

### 8.2 Data Flow Architecture

```
R2 Parquet Files (Cloud Storage)
    ↓ [DuckDB httpfs, cached 24h]
In-Memory DuckDB Tables
    ↓ [SQL queries, cached per params]
Pandas DataFrames (NAV data)
    ↓ [pct_change()]
Returns Series
    ↓ [metrics.py functions]
Performance Metrics
    ↓ [visualizations.py + st.dataframe]
Charts & Tables (UI)
```

### 8.3 State Management

**Session State Usage**:
```python
st.session_state.data_loader  # Shared MktDataLoader instance
# Widget states managed implicitly by Streamlit with unique keys
```

**Widget Key Strategy**:
- Unique keys per page: `key=f"fund_select_{key_suffix}"`
- Prevents conflicts in multipage app

### 8.4 Error Handling

**Graceful Degradation**:
```python
if df is None or len(df) == 0:
    st.error("❌ No data available")
    return  # Stop execution, show error

if len(fund_nav) < 10:
    continue  # Skip fund, insufficient data
```

### 8.5 Performance Optimizations

**Monthly Resampling**:
- Reduces data points by ~95% (252 daily → 12 monthly)
- Faster chart rendering, cleaner visualizations
- Applied to: Equity curves, rolling metrics

**Pivot Operations**:
- Long format in DB (efficient storage)
- Wide format in memory (efficient analysis)

**Lazy Loading**:
- Data loaded only when page is accessed
- Cached after first load

---

## 9. Current State Summary

### Active Features

✅ **Multipage Architecture** (Fund Universe, Category Deepdive, Fund Deepdive)
✅ **R2 Integration** with DuckDB (in-memory, auto-refresh)
✅ **Monthly Resolution Charts** (equity curves, rolling metrics)
✅ **Performance Ranking Grid** (cyan-blue gradient, no gaps, annual return in cells)
✅ **Annual Returns Subplots** (vertical stack, mono-color bars, data labels)
✅ **Metrics Tables** with inline charts (Annual Return Trend, Data Range)
✅ **Include/Exclude Fund Selection** mode
✅ **Plan Type Filtering** (Direct/Regular/All)
✅ **Benchmark Integration** (TRI/PRICE indices)

### Recent Changes

🔄 **Performance Ranking Grid**:
- Changed color scale from red-green to cyan-blue gradient
- Added Annual Return metric to cell annotations
- Removed max_funds slider (now shows all selected funds)
- Fixed ranking gaps issue (consecutive ranks per year)

🔄 **Annual Returns Chart**:
- Switched from bubble chart to vertical subplots
- One subplot per year with all funds
- Mono-color bars (#3b82f6) with data labels
- Minimal spacing between subplots (0.02)

🔄 **Metrics Tables**:
- Added "Annual Return Trend" column (inline line chart)
- Added "Data Range" column (YYYY-YYYY format)
- Removed columns: Expected Returns, Win Rate, VaR, CVaR, R²
- Fixed alignment with common year axis

---

**Last Updated**: 2025-10-18
**Generated by**: Claude Code
