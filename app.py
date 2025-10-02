import streamlit as st
import pandas as pd
import os

# Import custom modules
from src.data_loader import (
    get_data_loader, get_fund_columns, get_available_funds_list,
    filter_by_date_range, calculate_returns
)
from src.metrics import calculate_all_metrics
from src.visualizations import (
    create_cumulative_returns_chart, create_drawdown_chart,
    create_monthly_returns_heatmap, create_rolling_sharpe_chart,
    create_log_returns_chart
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

def main():
    # Header
    st.markdown('<div class="main-header">📊 Fund Performance Tearsheet</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Comprehensive performance analysis and benchmarking tool</div>', unsafe_allow_html=True)
    st.markdown("---")

    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Initialize R2 data loader
        data_loader = get_data_loader()

        # Test R2 connection
        st.subheader("🔗 R2 Data Connection")
        connection_status, connection_msg = data_loader.test_connection()

        if connection_status:
            st.success(f"✅ {connection_msg}")
        else:
            st.error(f"❌ {connection_msg}")
            st.info("Please check your .env file and R2 credentials")
            st.stop()

        # Get data information
        data_info = data_loader.get_data_info()
        if data_info:
            st.info(f"""
            📊 **Dataset Info:**
            - Total rows: {data_info['total_rows']:,}
            - Date range: {data_info['min_date']} to {data_info['max_date']}
            - Unique dates: {data_info['unique_dates']:,}
            - File: {data_info['file_path']}
            """)

            # Store min/max dates for date picker
            min_date = pd.to_datetime(data_info['min_date']).date()
            max_date = pd.to_datetime(data_info['max_date']).date()
        else:
            st.error("❌ Could not retrieve dataset information")
            st.stop()

        # Get available funds
        available_funds = get_available_funds_list(data_loader)

        if len(available_funds) < 2:
            st.error("❌ Need at least 2 funds in the dataset")
            st.info("Please ensure your dataset has multiple fund schemes")
            st.stop()

        st.subheader("📈 Fund Selection")

        # Create display options for selectbox
        fund_options = [fund['display_name'] for fund in available_funds]

        selected_fund_idx = st.selectbox(
            "Strategy Fund",
            range(len(fund_options)),
            format_func=lambda x: fund_options[x],
            help="Select the fund to analyze"
        )
        selected_fund_scheme = available_funds[selected_fund_idx]

        # Filter out the selected fund for benchmark selection
        benchmark_options = [fund for i, fund in enumerate(available_funds) if i != selected_fund_idx]
        benchmark_display_options = [fund['display_name'] for fund in benchmark_options]

        selected_benchmark_idx = st.selectbox(
            "Benchmark",
            range(len(benchmark_options)),
            format_func=lambda x: benchmark_display_options[x],
            help="Select the benchmark for comparison"
        )
        selected_benchmark_scheme = benchmark_options[selected_benchmark_idx]

        # Show fund details
        st.caption(f"**Strategy:** {selected_fund_scheme['scheme_name']}")
        st.caption(f"**Benchmark:** {selected_benchmark_scheme['scheme_name']}")

        # Date range
        st.subheader("📅 Analysis Period")
        col1, col2 = st.columns(2)

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
    strategy_name = selected_fund_scheme['scheme_name']
    benchmark_name = selected_benchmark_scheme['scheme_name']

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
    st.subheader("📊 Performance Summary")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Return",
            f"{strategy_metrics['Cumulative Return']*100:.2f}%",
            delta=f"{(strategy_metrics['Cumulative Return'] - benchmark_metrics['Cumulative Return'])*100:.2f}% vs BM",
            help="Total cumulative return over the period"
        )

    with col2:
        st.metric(
            "Sharpe Ratio",
            f"{strategy_metrics['Sharpe Ratio']:.2f}",
            delta=f"{strategy_metrics['Sharpe Ratio'] - benchmark_metrics['Sharpe Ratio']:.2f} vs BM",
            help="Risk-adjusted return metric"
        )

    with col3:
        st.metric(
            "Max Drawdown",
            f"{strategy_metrics['Max Drawdown']*100:.2f}%",
            delta=f"{(strategy_metrics['Max Drawdown'] - benchmark_metrics['Max Drawdown'])*100:.2f}% vs BM",
            delta_color="inverse",
            help="Maximum peak-to-trough decline"
        )

    with col4:
        st.metric(
            "Volatility",
            f"{strategy_metrics['Volatility (ann.)']*100:.2f}%",
            delta=f"{(strategy_metrics['Volatility (ann.)'] - benchmark_metrics['Volatility (ann.)'])*100:.2f}% vs BM",
            delta_color="inverse",
            help="Annualized standard deviation"
        )

    st.markdown("---")

    # Charts and Metrics
    col_left, col_right = st.columns([2, 1])

    with col_left:
        # Cumulative Returns
        st.plotly_chart(
            create_cumulative_returns_chart(
                strategy_returns, benchmark_returns,
                strategy_name, benchmark_name
            ),
            use_container_width=True
        )

        # Log Returns
        st.plotly_chart(
            create_log_returns_chart(
                strategy_returns, benchmark_returns,
                strategy_name, benchmark_name
            ),
            use_container_width=True
        )

        # Monthly Heatmap
        st.plotly_chart(
            create_monthly_returns_heatmap(strategy_returns, strategy_name),
            use_container_width=True
        )

    with col_right:
        # Metrics Table
        st.subheader("📋 Detailed Metrics")

        metrics_df = create_metrics_comparison_df(strategy_metrics, benchmark_metrics)

        st.dataframe(
            metrics_df,
            hide_index=True,
            use_container_width=True,
            height=500
        )

        # Download button
        csv = metrics_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Metrics CSV",
            data=csv,
            file_name=f"metrics_{strategy_name}_vs_{benchmark_name}.csv",
            mime="text/csv"
        )

    # Additional Analysis
    st.markdown("---")
    st.subheader("📈 Additional Analysis")

    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(
            create_drawdown_chart(strategy_returns, strategy_name),
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            create_rolling_sharpe_chart(
                strategy_returns, benchmark_returns,
                strategy_name, benchmark_name,
                risk_free_rate=risk_free_rate
            ),
            use_container_width=True
        )

    # Footer
    st.markdown("---")
    st.caption(
        f"📅 Analysis Period: {start_date} to {end_date} ({period_desc}) | "
        f"💰 Risk-Free Rate: {risk_free_rate*100:.2f}% | "
        f"📊 Data Points: {len(df)} | "
        f"🗄️ Data Source: Cloudflare R2"
    )

if __name__ == "__main__":
    main()