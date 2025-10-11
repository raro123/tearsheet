"""Page 3: Fund Deepdive

Comprehensive performance analysis for a single fund vs benchmark
This is the original tearsheet functionality
"""
import streamlit as st
import pandas as pd
from src.data_loader import calculate_returns
from src.metrics import calculate_all_metrics
from src.visualizations import (
    create_cumulative_returns_chart,
    create_log_returns_chart,
    create_annual_returns_chart,
    create_drawdown_comparison_chart,
    create_rolling_returns_chart,
    create_monthly_returns_table
)
from utils.helpers import create_metrics_comparison_df, get_period_description


def render(data_loader):
    """Render the Fund Deepdive page

    Args:
        data_loader: R2DataLoader instance from session state
    """
    st.title("🔍 Fund Deepdive")
    st.markdown("Comprehensive performance analysis for a single fund")
    st.markdown("---")

    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Analysis Settings")

        # Get all funds
        all_funds = data_loader.get_available_funds()

        # Category filters
        st.subheader("🏷️ Fund Filters")
        categories_level1 = all_funds.scheme_category_level1.dropna().unique().tolist()

        selected_category_level1 = st.selectbox(
            "Scheme Type",
            categories_level1,
            help="Select high-level scheme category",
            key="fd_cat_l1"
        )

        # Get level 2 categories
        categories_level2 = (all_funds
                            .query("scheme_category_level1 == @selected_category_level1")
                            .scheme_category_level2.unique().tolist())
        categories_level2 = ["ALL"] + categories_level2

        selected_category_level2 = st.selectbox(
            "Scheme Category",
            categories_level2,
            help="Select specific scheme category",
            key="fd_cat_l2"
        )

        # Fund selection
        st.subheader("📈 Fund Selection")

        if selected_category_level2 == "ALL":
            fund_options = (all_funds
                    .query("scheme_category_level1 == @selected_category_level1")
                    ['display_name'].tolist())
        else:
            fund_options = (all_funds
                    .query("scheme_category_level1 == @selected_category_level1 and scheme_category_level2 == @selected_category_level2")
                    ['display_name'].tolist())

        selected_fund_scheme = st.selectbox(
            "Strategy Fund",
            fund_options,
            help="Select the fund to analyze",
            key="fd_fund"
        )

        # Benchmark Selection
        st.subheader("📊 Benchmark Selection")

        index_type = st.selectbox(
            "Index Type",
            options=["TRI", "PRICE"],
            index=0,
            help="Select Total Return Index (TRI) or Price Index",
            key="fd_index_type"
        )

        index_category = st.selectbox(
            "Index Category",
            options=["ALL", "BROAD", "SECTORAL"],
            index=0,
            help="Filter by index category",
            key="fd_index_cat"
        )

        benchmark_options = data_loader.get_benchmark_options(
            index_type=index_type,
            index_category=index_category
        )

        selected_benchmark_index = st.selectbox(
            "Select Index",
            options=benchmark_options,
            help="Select the benchmark index",
            key="fd_benchmark"
        )

        st.caption(f"**Strategy:** {selected_fund_scheme}")
        st.caption(f"**Benchmark:** {selected_benchmark_index} ({index_type})")

        # Date range
        st.subheader("📅 Analysis Period")
        col1, col2 = st.columns(2)

        # Get date ranges
        fund_scheme_code = selected_fund_scheme.split('|')[1]
        fund_min_date, fund_max_date = data_loader.get_fund_date_range(fund_scheme_code)
        benchmark_min_date, benchmark_max_date = data_loader.get_benchmark_date_range(selected_benchmark_index, index_type)

        # Calculate common date range
        common_min_date = max(fund_min_date, benchmark_min_date) if fund_min_date and benchmark_min_date else None
        common_max_date = min(fund_max_date, benchmark_max_date) if fund_max_date and benchmark_max_date else None

        overall_min_date, overall_max_date = data_loader.get_data_date_range()

        with col1:
            start_date = st.date_input(
                "Start Date",
                value=common_min_date if common_min_date else overall_min_date,
                min_value=overall_min_date,
                max_value=overall_max_date,
                key="fd_start_date"
            )

        with col2:
            end_date = st.date_input(
                "End Date",
                value=common_max_date if common_max_date else overall_max_date,
                min_value=overall_min_date,
                max_value=overall_max_date,
                key="fd_end_date"
            )

        period_desc = get_period_description(pd.Timestamp(start_date), pd.Timestamp(end_date))
        st.caption(f"Analysis period: {period_desc}")

        # Risk-free rate
        st.subheader("⚙️ Parameters")
        risk_free_rate = st.number_input(
            "Risk-Free Rate (%)",
            value=2.49,
            min_value=0.0,
            max_value=10.0,
            step=0.1,
            help="Annual risk-free rate for Sharpe/Sortino calculations",
            key="fd_rf_rate"
        ) / 100

        st.markdown("---")
        st.caption("Made with Streamlit 📊")

    # Load data
    with st.spinner("Loading data from R2..."):
        df = data_loader.load_fund_data(
            start_date=start_date,
            end_date=end_date,
            selected_fund_schemes=[selected_fund_scheme]
        )

        benchmark_series = data_loader.load_benchmark_data(
            index_name=selected_benchmark_index,
            index_type=index_type,
            start_date=start_date,
            end_date=end_date
        )

    if df is None or len(df) == 0:
        st.error("❌ No fund data available for selected date range")
        return

    if benchmark_series is None or len(benchmark_series) == 0:
        st.error("❌ No benchmark data available for selected date range")
        return

    # Get names
    strategy_name = selected_fund_scheme
    benchmark_name = f"{selected_benchmark_index} ({index_type})"

    # Calculate returns
    strategy_nav = df[strategy_name]
    benchmark_nav = benchmark_series

    strategy_returns = calculate_returns(strategy_nav)
    benchmark_returns = calculate_returns(benchmark_nav)

    # Calculate metrics
    strategy_metrics = calculate_all_metrics(strategy_returns, benchmark_returns, risk_free_rate)
    benchmark_metrics = calculate_all_metrics(benchmark_returns, risk_free_rate=risk_free_rate)

    # Main Content Area

    # Summary Cards
    st.header(f"📊 Performance Summary")
    st.caption(f"{strategy_name} vs {benchmark_name}")

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
        on = st.toggle("Log Scale Y-Axis", value=False, key="fd_log_scale")
        if not on:
            st.plotly_chart(
                create_cumulative_returns_chart(
                    strategy_returns, benchmark_returns,
                    strategy_name, benchmark_name
                ),
                use_container_width=True
            )
        else:
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

        # Rolling Returns
        rolling_period = st.selectbox(
            "Rolling Period",
            options=[("1 Year", 252), ("3 Years", 756), ("5 Years", 1260)],
            format_func=lambda x: x[0],
            index=0,
            key="fd_rolling_period"
        )

        st.plotly_chart(
            create_rolling_returns_chart(
                strategy_returns, benchmark_returns,
                strategy_name, benchmark_name,
                window=rolling_period[1]
            ),
            use_container_width=True
        )

        # Annual Returns
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

        # Get data periods
        strategy_data_start = strategy_nav.index.min().strftime('%Y-%m-%d')
        strategy_data_end = strategy_nav.index.max().strftime('%Y-%m-%d')
        benchmark_data_start = benchmark_nav.index.min().strftime('%Y-%m-%d')
        benchmark_data_end = benchmark_nav.index.max().strftime('%Y-%m-%d')

        strategy_data_period = f"{strategy_data_start} to {strategy_data_end}"
        benchmark_data_period = f"{benchmark_data_start} to {benchmark_data_end}"
        comparison_period = f"{start_date} to {end_date}"

        # Shorten names
        strategy_display = strategy_name if len(strategy_name) <= 40 else strategy_name[:37] + "..."
        benchmark_display = benchmark_name if len(benchmark_name) <= 40 else benchmark_name[:37] + "..."

        metrics_df = create_metrics_comparison_df(
            strategy_metrics, benchmark_metrics,
            strategy_name=strategy_display,
            benchmark_name=benchmark_display,
            strategy_data_period=strategy_data_period,
            benchmark_data_period=benchmark_data_period,
            comparison_period=comparison_period
        )

        # Styling
        def highlight_section_headers(row):
            if '──' in str(row['Metric']):
                return ['background-color: #1F2937; color: white; font-weight: bold'] * len(row)
            elif row['Metric'] in ['Name', 'Data Period', 'Comparison Period']:
                return ['background-color: #374151; color: white; font-weight: bold'] * len(row)
            return [''] * len(row)

        styled_metrics = metrics_df.style.apply(highlight_section_headers, axis=1)

        st.dataframe(
            styled_metrics,
            hide_index=True,
            use_container_width=True,
            height=1200,
            column_config={
                "Metric": st.column_config.TextColumn("Metric", width="medium"),
                "Strategy": st.column_config.TextColumn("Strategy", width="small"),
                "Benchmark": st.column_config.TextColumn("Benchmark", width="small"),
            }
        )

        # Download
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
