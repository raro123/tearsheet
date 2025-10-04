import streamlit as st
import pandas as pd

# Import custom modules
from src.data_loader import (
    get_data_loader, calculate_returns
)
from src.metrics import calculate_all_metrics
from src.visualizations import (
    create_cumulative_returns_chart,
    create_log_returns_chart, create_annual_returns_chart,
    create_drawdown_comparison_chart, create_rolling_returns_chart,
    create_monthly_returns_table
)
from utils.helpers import create_metrics_comparison_df, get_period_description

# Page configuration
st.set_page_config(
    page_title="Fund Performance Tearsheet",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F2937;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Configuration
DEFAULT_DATA_FOLDER = "data"
DEFAULT_RISK_FREE_RATE = 0.0249


# # Header
# st.markdown('<div class="main-header">📊 Fund Performance Tearsheet</div>', unsafe_allow_html=True)
# st.markdown('<div class="sub-header">Comprehensive performance analysis and benchmarking tool</div>', unsafe_allow_html=True)
# st.markdown("---")

try:
    data_loader = get_data_loader()
    data_loader.create_db_tables()
except Exception as e:
    st.error(f"Failed to initialize data loader: {str(e)}")
    st.stop()

# Sidebar Configuration
with st.sidebar:
    # Get data information (for date range only)

    # Get available fund categories
    st.subheader("🏷️ Fund Filters")

    # Get all funds to extract categories
    all_funds = data_loader.get_available_funds()

    # Extract unique categories (excluding Uncategorized)
    categories_level1 = all_funds.scheme_category_level1.dropna().unique().tolist()

    # Category filter - Level 1 (required selection)
    selected_category_level1 = st.selectbox(
        "Scheme Type",
        categories_level1,
        help="Select high-level scheme category"
    )

    # Get level 2 categories based on level 1 selection
    categories_level2 = (all_funds
                        .query("scheme_category_level1 == @selected_category_level1")
                        .scheme_category_level2.unique().tolist()
                        )

    # Category filter - Level 2 (required selection)
    selected_category_level2 = st.selectbox(
        "Scheme Category",
        categories_level2,
        help="Select specific scheme category"
    )

    # Filter funds based on both category selections

    st.subheader("📈 Fund Selection")

    # Create display options for selectbox
    fund_options = (all_funds
            .query("scheme_category_level1 == @selected_category_level1 and scheme_category_level2 == @selected_category_level2")
            ['display_name'].tolist()
            )
    selected_fund_scheme = st.selectbox(
        "Strategy Fund",
        fund_options,
        help="Select the fund to analyze"
    )

    # Filter out the selected fund for benchmark selection
    benchmark_display_options = fund_options

    selected_benchmark_scheme = st.selectbox(
        "Benchmark",
        benchmark_display_options,
        help="Select the benchmark for comparison"
    )


    # Show fund details
    st.caption(f"**Strategy:** {selected_fund_scheme}")
    st.caption(f"**Benchmark:** {selected_benchmark_scheme}")

    # Date range
    st.subheader("📅 Analysis Period")
    col1, col2 = st.columns(2)

    min_date, max_date = data_loader.get_data_date_range()
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )

    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    period_desc = get_period_description(pd.Timestamp(start_date), pd.Timestamp(end_date))
    st.caption(f"Analysis period: {period_desc}")

    # Risk-free rate
    st.subheader("⚙️ Parameters")
    risk_free_rate = st.number_input(
        "Risk-Free Rate (%)",
        value=DEFAULT_RISK_FREE_RATE * 100,
        min_value=0.0,
        max_value=10.0,
        step=0.1,
        help="Annual risk-free rate for Sharpe/Sortino calculations"
    ) / 100

    st.markdown("---")
    st.caption("Made with Streamlit 📊")

# Load data from R2 with filtering
with st.spinner("Loading data from R2..."):
    df = data_loader.load_fund_data(
        start_date=start_date,
        end_date=end_date,
        selected_fund_schemes=[selected_fund_scheme, selected_benchmark_scheme]
    )

if df is None or len(df) == 0:
    st.error("No data available for selected date range")
    st.stop()

# Get scheme names for column access
strategy_name = selected_fund_scheme
benchmark_name = selected_benchmark_scheme

# Calculate returns
strategy_nav = df[strategy_name]
benchmark_nav = df[benchmark_name]

strategy_returns = calculate_returns(strategy_nav)
benchmark_returns = calculate_returns(benchmark_nav)

# Calculate metrics
strategy_metrics = calculate_all_metrics(strategy_returns, benchmark_returns, risk_free_rate)
benchmark_metrics = calculate_all_metrics(benchmark_returns, risk_free_rate=risk_free_rate)

# Main Content Area

# Summary Cards
st.header("📊 Performance Summary")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Return",
        f"{strategy_metrics['Cumulative Return']*100:.1f}%",
        delta=f"{(strategy_metrics['Cumulative Return'] - benchmark_metrics['Cumulative Return'])*100:.1f}% vs BM",
        help="Total cumulative return over the period"
    )

with col2:
    st.metric(
        "CAGR",
        f"{strategy_metrics['CAGR']*100:.1f}%",
        delta=f"{(strategy_metrics['CAGR'] - benchmark_metrics['CAGR'])*100:.1f}% vs BM",
        help="Compound Annual Growth Rate"
    )

with col3:
    st.metric(
        "Sharpe Ratio",
        f"{strategy_metrics['Sharpe Ratio']:.2f}",
        delta=f"{strategy_metrics['Sharpe Ratio'] - benchmark_metrics['Sharpe Ratio']:.2f} vs BM",
        help="Risk-adjusted return metric"
    )

with col4:
    st.metric(
        "Max Drawdown",
        f"{strategy_metrics['Max Drawdown']*100:.1f}%",
        delta=f"{(benchmark_metrics['Max Drawdown'] - strategy_metrics['Max Drawdown'])*100:.1f}% vs BM",
        delta_color="inverse",
        help="Maximum peak-to-trough decline"
    )

with col5:
    st.metric(
        "Volatility",
        f"{strategy_metrics['Volatility (ann.)']*100:.1f}%",
        delta=f"{(strategy_metrics['Volatility (ann.)'] - benchmark_metrics['Volatility (ann.)'])*100:.1f}% vs BM",
        delta_color="inverse",
        help="Annualized standard deviation"
    )

st.markdown("---")

# Charts and Metrics
col_left, col_right = st.columns([2, 1])

with col_left:
    # Cumulative Returns
    on = st.toggle("Log Scale Y-Axis", value=False, key="log_scale_toggle")
    if not on:
        st.plotly_chart(
            create_cumulative_returns_chart(
                strategy_returns, benchmark_returns,
                strategy_name, benchmark_name
            ),
            use_container_width=True
        )
    else:
    # Log Returns
        st.plotly_chart(
            create_log_returns_chart(
                strategy_returns, benchmark_returns,
                strategy_name, benchmark_name
            ),
            use_container_width=True
        )

    # Drawdown Comparison
    st.plotly_chart(
        create_drawdown_comparison_chart(
            strategy_returns, benchmark_returns,
            strategy_name, benchmark_name
        ),
        use_container_width=True
    )

    # Rolling Returns with period selector
    rolling_period = st.selectbox(
        "Rolling Period",
        options=[("1 Year", 252), ("3 Years", 756), ("5 Years", 1260)],
        format_func=lambda x: x[0],
        index=0,
        key="rolling_period_selector"
    )

    st.plotly_chart(
        create_rolling_returns_chart(
            strategy_returns, benchmark_returns,
            strategy_name, benchmark_name,
            window=rolling_period[1]
        ),
        use_container_width=True
    )

    # Annual Returns Bar Chart
    st.plotly_chart(
        create_annual_returns_chart(
            strategy_returns, benchmark_returns,
            strategy_name, benchmark_name
        ),
        use_container_width=True
    )

with col_right:
    # Metrics Table
    st.subheader("📊 Performance Metrics")

    metrics_df = create_metrics_comparison_df(strategy_metrics, benchmark_metrics)

    # Apply styling to the metrics table
    def highlight_section_headers(row):
        if '──' in str(row['Metric']):
            return ['background-color: #1F2937; color: white; font-weight: bold'] * len(row)
        return [''] * len(row)

    styled_metrics = metrics_df.style.apply(highlight_section_headers, axis=1)

    st.dataframe(
        styled_metrics,
        hide_index=True,
        use_container_width=True,
        height=1000,
        column_config={
            "Metric": st.column_config.TextColumn(
                "Metric",
                width="medium",
            ),
            "Strategy": st.column_config.TextColumn(
                "Strategy",
                width="small",
            ),
            "Benchmark": st.column_config.TextColumn(
                "Benchmark",
                width="small",
            ),
        }
    )

    # Download button
    csv = metrics_df.to_csv(index=False)
    st.download_button(
        label="📥 Download Metrics CSV",
        data=csv,
        file_name=f"metrics_{strategy_name}_vs_{benchmark_name}.csv",
        mime="text/csv"
    )

# Monthly Returns Tables
st.markdown("---")
st.subheader("📅 Monthly Returns (%)")

col1, col2 = st.columns(2)

with col1:
    st.caption(f"**{strategy_name}**")
    strategy_monthly_table = create_monthly_returns_table(strategy_returns)

    # Apply conditional formatting
    styled_strategy = strategy_monthly_table.style.background_gradient(
        cmap='RdYlGn',
        subset=[col for col in strategy_monthly_table.columns if col != 'Year'],
        vmin=-10,
        vmax=10
    ).format({col: '{:.2f}' for col in strategy_monthly_table.columns if col != 'Year'})

    st.dataframe(
        styled_strategy,
        hide_index=True,
        use_container_width=True,
        height=400
    )

with col2:
    st.caption(f"**{benchmark_name}**")
    benchmark_monthly_table = create_monthly_returns_table(benchmark_returns)

    # Apply conditional formatting
    styled_benchmark = benchmark_monthly_table.style.background_gradient(
        cmap='RdYlGn',
        subset=[col for col in benchmark_monthly_table.columns if col != 'Year'],
        vmin=-10,
        vmax=10
    ).format({col: '{:.2f}' for col in benchmark_monthly_table.columns if col != 'Year'})

    st.dataframe(
        styled_benchmark,
        hide_index=True,
        use_container_width=True,
        height=400
    )

# Footer
st.markdown("---")
st.caption(
    f"📅 Analysis Period: {start_date} to {end_date} ({period_desc}) | "
    f"💰 Risk-Free Rate: {risk_free_rate*100:.2f}% | "
    f"📊 Data Points: {len(df)} | "
    f"🗄️ Data Source: Cloudflare R2"
)
