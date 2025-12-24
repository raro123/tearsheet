"""Page 2: Fund Category Deepdive

Compare multiple funds within a category using various visualizations
"""
import streamlit as st
import pandas as pd
from src.data_loader import calculate_returns
from src.metrics import calculate_all_metrics
from src.computation_cache import (
    get_cached_metrics,
    get_cached_annual_returns,
    get_cached_monthly_returns,
    get_cache_stats,
    clear_cache_on_data_change
)
from src.visualizations import (
    create_category_equity_curves,
    create_annual_returns_table,
    create_correlation_heatmap,
    create_cagr_distribution,
    create_annual_returns_distribution,
    create_volatility_distribution,
    create_sharpe_distribution,
    create_max_drawdown_distribution,
    create_bubble_scatter_chart,
    create_rolling_metric_chart,
    create_performance_ranking_grid
)
from src.shared_components import (
    render_date_range_selector,
    render_category_filters,
    render_plan_type_filter,
    render_fund_multiselect,
    render_risk_free_rate,
    get_final_fund_list,
    filter_funds_by_plan_type
)


def render(data_loader):
    """Render the Fund Category Deepdive page

    Args:
        data_loader: R2DataLoader instance from session state
    """
    # Sidebar Filters
    with st.sidebar:
        st.header("⚙️ Analysis Settings")

        # Get all funds
        all_funds = data_loader.get_available_funds()

        # Category filters (no "ALL" for level 2)
        selected_category_level1, selected_category_level2 = render_category_filters(
            all_funds, allow_all_level2=False
        )

        # Plan type filter
        plan_type = render_plan_type_filter()

        # Filter funds by category and plan type
        if selected_category_level2:
            category_funds = all_funds.query(
                "scheme_category_level1 == @selected_category_level1 and "
                "scheme_category_level2 == @selected_category_level2"
            )
        else:
            category_funds = all_funds.query("scheme_category_level1 == @selected_category_level1")

        # Apply plan type filter
        category_funds = filter_funds_by_plan_type(category_funds, plan_type)

        # Fund multi-select
        selected_funds, selection_mode = render_fund_multiselect(category_funds, key_suffix="category")

        # Get final fund list
        all_category_funds = category_funds['display_name'].tolist()
        final_fund_list = get_final_fund_list(all_category_funds, selected_funds, selection_mode)

        if not final_fund_list:
            st.error("⚠️ No funds selected. Please adjust your filters.")
            return

        st.success(f"✅ Analyzing {len(final_fund_list)} fund(s)")

        st.markdown("---")

        # Benchmark Selection
        st.subheader("📊 Benchmark Selection")

        index_type = st.selectbox(
            "Index Type",
            options=["TRI", "PRICE"],
            index=0,
            help="Select Total Return Index (TRI) or Price Index",
            key="cat_index_type"
        )

        index_category = st.selectbox(
            "Index Category",
            options=["ALL", "BROAD", "SECTORAL"],
            index=0,
            help="Filter by index category",
            key="cat_index_cat"
        )

        benchmark_options = data_loader.get_benchmark_options(
            index_type=index_type,
            index_category=index_category
        )

        if not benchmark_options:
            st.error("⚠️ No benchmarks available")
            return

        selected_benchmark_index = st.selectbox(
            "Select Index",
            options=benchmark_options,
            help="Select the benchmark index",
            key="cat_benchmark"
        )

        benchmark_name = f"{selected_benchmark_index} ({index_type})"

        st.markdown("---")

        # Date range selector
        start_date, end_date, period_desc = render_date_range_selector(all_funds, data_loader)

        st.markdown("---")

        # Risk-free rate
        risk_free_rate = render_risk_free_rate()

        st.markdown("---")

        # Cache monitoring and control
        st.subheader("🔍 Performance Monitor")

        # Display cache stats
        cache_stats = get_cache_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Metrics Cached", cache_stats['metrics_entries'])
            st.metric("Annual Returns", cache_stats['annual_returns_entries'])
        with col2:
            st.metric("Monthly Returns", cache_stats['monthly_returns_entries'])
            st.metric("Total Entries", cache_stats['total_entries'])

        # Clear cache button
        if st.button("🔄 Clear Cache", help="Clear all cached computations"):
            clear_cache_on_data_change()
            st.cache_data.clear()
            st.success("✅ Cache cleared!")
            st.rerun()

    # Main Content
    with st.spinner("Loading fund data..."):
        # Load fund data
        df = data_loader.load_fund_data(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            selected_fund_schemes=final_fund_list
        )

        # Load benchmark data separately
        benchmark_series = data_loader.load_benchmark_data(
            index_name=selected_benchmark_index,
            index_type=index_type,
            start_date=start_date,
            end_date=end_date
        )

        if df is None or len(df) == 0:
            st.error("❌ No fund data available for selected period and funds")
            return

        if benchmark_series is None or len(benchmark_series) == 0:
            st.error("❌ No benchmark data available for selected period")
            return

        benchmark_nav = benchmark_series
        benchmark_returns = calculate_returns(benchmark_nav)

        # Calculate returns and metrics for each fund
        funds_returns = {}
        funds_metrics = []

        for fund_name in final_fund_list:
            if fund_name in df.columns:
                fund_nav = df[fund_name].dropna()  # Drop NaN values to use only available data
                if len(fund_nav) > 10:  # At least 10 data points
                    fund_returns = calculate_returns(fund_nav)
                    funds_returns[fund_name] = fund_returns

                    # Calculate metrics using session cache (prevents triple calculation)
                    fund_metrics = get_cached_metrics(
                        fund_name, fund_returns, benchmark_returns,
                        risk_free_rate, start_date, end_date
                    )
                    fund_metrics['Fund'] = fund_name
                    funds_metrics.append(fund_metrics)

        if not funds_returns:
            st.error("❌ No valid fund data available for selected funds")
            return

        # Calculate benchmark metrics using cache
        benchmark_metrics = get_cached_metrics(
            selected_benchmark_index, benchmark_returns, None,
            risk_free_rate, start_date, end_date
        )

        # Create metrics DataFrame
        metrics_df = pd.DataFrame(funds_metrics)

        # Pre-compute annual and monthly returns for all funds (prevents redundant resampling)
        annual_returns_cache = {}
        monthly_returns_cache = {}

        for fund_name in funds_returns.keys():
            annual_returns_cache[fund_name] = get_cached_annual_returns(
                fund_name, funds_returns[fund_name], start_date, end_date
            )
            monthly_returns_cache[fund_name] = get_cached_monthly_returns(
                fund_name, funds_returns[fund_name], start_date, end_date
            )

        # Cache benchmark annual/monthly returns
        benchmark_annual = get_cached_annual_returns(
            selected_benchmark_index, benchmark_returns, start_date, end_date
        )
        benchmark_monthly = get_cached_monthly_returns(
            selected_benchmark_index, benchmark_returns, start_date, end_date
        )

        # Display summary (caption only, no header)
        st.caption(f"**{selected_category_level1} - {selected_category_level2}** | Period: {start_date} to {end_date} ({period_desc}) | {len(funds_returns)} funds")

        # Summary metrics - 5 columns with sleek visualizations
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            # CAGR Distribution
            fig_cagr = create_cagr_distribution(metrics_df, benchmark_metrics['CAGR'])
            st.plotly_chart(fig_cagr, use_container_width=True)

        with col2:
            # Annual Returns Distribution
            fig_returns_dist = create_annual_returns_distribution(
                funds_returns, benchmark_returns, start_date, end_date
            )
            st.plotly_chart(fig_returns_dist, use_container_width=True)

        with col3:
            # Volatility Distribution
            fig_vol_dist = create_volatility_distribution(
                funds_returns, benchmark_returns, start_date, end_date, risk_free_rate
            )
            st.plotly_chart(fig_vol_dist, use_container_width=True)

        with col4:
            # Sharpe Ratio Distribution
            fig_sharpe_dist = create_sharpe_distribution(
                funds_returns, benchmark_returns, start_date, end_date, risk_free_rate
            )
            st.plotly_chart(fig_sharpe_dist, use_container_width=True)

        with col5:
            # Max Drawdown Distribution
            fig_dd_dist = create_max_drawdown_distribution(
                funds_returns, benchmark_returns
            )
            st.plotly_chart(fig_dd_dist, use_container_width=True)

        st.markdown("---")

        # === SECTION 2: CUMULATIVE RETURN CHART (Always visible) ===
        st.caption("📈 Compare fund performance over time on linear or logarithmic scale")

        col_caption, col_log = st.columns([4, 1])
        with col_log:
            log_scale = st.checkbox("Log Scale", value=True, key="equity_log_scale")

        fig1 = create_category_equity_curves(funds_returns, benchmark_returns, benchmark_name, log_scale=log_scale)
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("---")

        # Chart 2: Annual Returns Table
        st.subheader("📊 Annual Returns by Year")
        st.caption("Sortable table with Beat Benchmark count (X/Y format), CAGR, and annual returns. Green = beat benchmark, Red = underperformed. Click column headers to sort.")

        styled_df = create_annual_returns_table(
            funds_returns, benchmark_returns, benchmark_name,
            start_date, end_date
        )
        st.dataframe(styled_df, use_container_width=True, height=600)

        # # Chart 2: Annual Returns Bubble Chart (Commented for experimentation)
        # # st.subheader("📊 Annual Returns by Year")
        # # st.caption("Bubble size represents annual volatility")
        # # fig2 = create_annual_returns_bubble_chart(
        # #     funds_returns, benchmark_returns, benchmark_name,
        # #     start_date, end_date
        # # )
        # # st.plotly_chart(fig2, use_container_width=True)

        st.markdown("---")

        # Correlation Matrix
        st.subheader("🔗 Correlation Matrix")
        st.caption("Correlation of monthly returns between all funds and benchmark. Red indicates lower correlation, green indicates stronger positive correlation.")

        fig_corr = create_correlation_heatmap(
            funds_returns, benchmark_returns, benchmark_name
        )
        st.plotly_chart(fig_corr, use_container_width=True)

        st.markdown("---")

        # Chart 3: Bubble Scatter Chart
        st.subheader("🔵 Multi-Metric Bubble Comparison")
        st.caption("Explore fund relationships across three metrics simultaneously")

        # Metric selectors
        col1, col2, col3 = st.columns(3)

        available_metrics = [
            'Cumulative Return', 'CAGR', 'Volatility (ann.)', 'Max Drawdown',
            'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio'
        ]

        with col1:
            x_metric = st.selectbox("X-Axis Metric", available_metrics, index=1, key="x_metric")

        with col2:
            y_metric = st.selectbox("Y-Axis Metric", available_metrics, index=4, key="y_metric")

        with col3:
            size_metric = st.selectbox("Bubble Size Metric", available_metrics, index=2, key="size_metric")

        if x_metric == y_metric:
            st.warning("⚠️ X and Y metrics are the same. Please select different metrics for better visualization.")

        # Get benchmark values for the selected metrics
        benchmark_x = benchmark_metrics.get(x_metric)
        benchmark_y = benchmark_metrics.get(y_metric)

        fig3 = create_bubble_scatter_chart(
            metrics_df, x_metric, y_metric, size_metric,
            benchmark_x=benchmark_x, benchmark_y=benchmark_y
        )
        st.plotly_chart(fig3, use_container_width=True)

        st.markdown("---")

        # Chart 4: Rolling Metrics
        st.subheader("📉 Rolling Metrics Over Time")
        st.caption("Analyze how fund metrics evolve over rolling time windows")

        col1, col2 = st.columns([2, 1])

        with col1:
            metric_type = st.selectbox(
                "Select Metric",
                ["Return", "Volatility", "Sharpe", "Drawdown"],
                index=0,
                key="rolling_metric_type"
            )

        with col2:
            rolling_period = st.selectbox(
                "Rolling Period",
                options=[("1 Year", 252), ("3 Years", 756), ("5 Years", 1260)],
                format_func=lambda x: x[0],
                index=0,
                key="rolling_period_cat"
            )
            window_label = rolling_period[0]
            window = rolling_period[1]

        fig4 = create_rolling_metric_chart(
            funds_returns, benchmark_returns, benchmark_name,
            metric_type, window, risk_free_rate, window_label=window_label
        )
        st.plotly_chart(fig4, use_container_width=True)

        st.markdown("---")

        # Chart 5: Performance Ranking Grid
        st.subheader("🏆 Performance Ranking Grid")
        st.caption("Visual ranking of funds by year with embedded metrics")

        ranking_mode = st.radio(
            "Ranking Mode",
            options=['annual', 'cumulative'],
            format_func=lambda x: 'Annual (Rank by each year)' if x == 'annual' else 'Cumulative (Rank from start to year end)',
            index=0,
            horizontal=True,
            key="ranking_mode"
        )

        fig5 = create_performance_ranking_grid(
            funds_returns, benchmark_returns, benchmark_name,
            start_date, end_date, risk_free_rate,
            ranking_mode=ranking_mode
        )
        st.plotly_chart(fig5, use_container_width=True)

        st.markdown("---")

        # Metrics Table
        st.subheader("📊 Detailed Metrics Table")
        st.caption("Complete performance metrics for all funds in the category")

        # Prepare benchmark display
        benchmark_display = benchmark_metrics.copy()
        benchmark_display['Fund'] = f"🔷 {benchmark_name}"

        # Calculate annual returns for benchmark with common year range
        # Include all years from start to end (including current year if end_date is in it)
        all_years = list(range(start_date.year, end_date.year + 1))
        benchmark_annual_returns = benchmark_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100

        # Align benchmark returns to all years
        aligned_benchmark_returns = []
        benchmark_years_with_data = []
        for year in all_years:
            year_data = benchmark_annual_returns[benchmark_annual_returns.index.year == year]
            if len(year_data) > 0:
                aligned_benchmark_returns.append(year_data.iloc[0])
                benchmark_years_with_data.append(year)
            else:
                aligned_benchmark_returns.append(0)

        # Create data range string for benchmark
        if len(benchmark_years_with_data) > 0:
            first_year = benchmark_years_with_data[0]
            last_year = benchmark_years_with_data[-1]
            if first_year == last_year:
                benchmark_data_range = str(first_year)
            else:
                benchmark_data_range = f"{first_year}-{last_year}"
        else:
            benchmark_data_range = "N/A"

        benchmark_display['Annual Return Trend'] = aligned_benchmark_returns
        benchmark_display['Data Range'] = benchmark_data_range

        # Create benchmark DataFrame with Fund column first
        benchmark_df = pd.DataFrame([benchmark_display])

        # Remove unwanted columns from benchmark
        columns_to_remove = [
            'Expected Monthly Return',
            'Expected Daily Return',
            'Win Rate',
            'Max Consecutive Wins',
            'Skewness',
            'VaR (95%)',
            'CVaR (95%)',
            'R²'
        ]
        benchmark_df = benchmark_df.drop(columns=[col for col in columns_to_remove if col in benchmark_df.columns])

        # Reorder columns to put Fund first, then Data Range, then Annual Return Trend
        cols = ['Fund', 'Data Range', 'Annual Return Trend'] + [col for col in benchmark_df.columns if col not in ['Fund', 'Data Range', 'Annual Return Trend']]
        benchmark_df = benchmark_df[cols]

        # Convert percentage columns from decimal to percentage (0.1 -> 10.0) for benchmark
        pct_cols = ['Cumulative Return', 'CAGR', 'Volatility (ann.)', 'Max Drawdown']
        for col in pct_cols:
            if col in benchmark_df.columns:
                benchmark_df[col] = benchmark_df[col] * 100

        # Create column config for benchmark
        benchmark_column_config = {}
        benchmark_column_config['Data Range'] = st.column_config.TextColumn(
            'Data Range',
            help="Date range of available data (YYYY-YYYY format)",
            width="small"
        )
        benchmark_column_config['Annual Return Trend'] = st.column_config.LineChartColumn(
            'Annual Return Trend',
            help="Annual returns (%) for each year in the selected period",
            y_min=-50,
            y_max=100
        )
        for col in benchmark_df.columns:
            if col in pct_cols:
                benchmark_column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f%%",
                    help=f"{col} as percentage"
                )
            elif col not in ['Fund', 'Annual Return Trend'] and benchmark_df[col].dtype in ['float64', 'int64']:
                benchmark_column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f"
                )

        # Display benchmark table (fixed at top)
        st.markdown("**Benchmark Reference**")
        st.dataframe(
            benchmark_df,
            use_container_width=True,
            hide_index=True,
            column_config=benchmark_column_config
        )

        st.markdown("---")

        # Prepare fund metrics for display
        display_metrics = metrics_df.copy()

        # Remove unwanted columns
        columns_to_remove = [
            'Expected Monthly Return',
            'Expected Daily Return',
            'Win Rate',
            'Max Consecutive Wins',
            'Skewness',
            'VaR (95%)',
            'CVaR (95%)',
            'R²'
        ]
        display_metrics = display_metrics.drop(columns=[col for col in columns_to_remove if col in display_metrics.columns])

        # Calculate annual returns for each fund with common year range
        # Use the same all_years calculated for benchmark (includes current year)
        annual_returns_data = {}
        data_range_map = {}

        for fund_name in final_fund_list:
            if fund_name in funds_returns:
                returns = funds_returns[fund_name]
                annual_returns = returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100

                # Create a series aligned to all years, with 0 for missing years
                aligned_returns = []
                years_with_data = []
                for year in all_years:
                    year_data = annual_returns[annual_returns.index.year == year]
                    if len(year_data) > 0:
                        aligned_returns.append(year_data.iloc[0])
                        years_with_data.append(year)
                    else:
                        aligned_returns.append(0)

                annual_returns_data[fund_name] = aligned_returns

                # Create data range string for this fund
                if len(years_with_data) > 0:
                    first_year = years_with_data[0]
                    last_year = years_with_data[-1]
                    if first_year == last_year:
                        data_range_map[fund_name] = str(first_year)
                    else:
                        data_range_map[fund_name] = f"{first_year}-{last_year}"
                else:
                    data_range_map[fund_name] = "N/A"

        # Add annual returns trend column
        display_metrics['Annual Return Trend'] = display_metrics['Fund'].map(annual_returns_data)

        # Add data range column
        display_metrics['Data Range'] = display_metrics['Fund'].map(data_range_map)

        # Reorder columns to put Fund first, then Data Range, then Annual Return Trend
        cols = ['Fund', 'Data Range', 'Annual Return Trend'] + [col for col in display_metrics.columns if col not in ['Fund', 'Data Range', 'Annual Return Trend']]
        display_metrics = display_metrics[cols]

        # Convert percentage columns from decimal to percentage (0.1 -> 10.0)
        for col in pct_cols:
            if col in display_metrics.columns:
                display_metrics[col] = display_metrics[col] * 100

        # Create column config for proper formatting
        column_config = {}

        # Add Data Range column config
        column_config['Data Range'] = st.column_config.TextColumn(
            'Data Range',
            help="Date range of available data (YYYY-YYYY format)",
            width="small"
        )

        # Add line chart config for Annual Return Trend
        column_config['Annual Return Trend'] = st.column_config.LineChartColumn(
            'Annual Return Trend',
            help="Annual returns (%) for each year in the selected period",
            y_min=-50,
            y_max=100
        )

        for col in display_metrics.columns:
            if col in pct_cols:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f%%",
                    help=f"{col} as percentage"
                )
            elif col not in ['Fund', 'Annual Return Trend'] and display_metrics[col].dtype in ['float64', 'int64']:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f"
                )

        # Display fund metrics table (sortable)
        st.markdown(f"**Fund Performance ({len(display_metrics)} funds)**")
        st.dataframe(
            display_metrics,
            use_container_width=True,
            height=400,
            hide_index=True,
            column_config=column_config
        )

        # Download button
        csv = metrics_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Metrics CSV",
            data=csv,
            file_name=f"category_metrics_{selected_category_level1}_{selected_category_level2}_{start_date}_{end_date}.csv",
            mime="text/csv"
        )

        # Footer
        st.markdown("---")
        st.caption(
            f"📅 Analysis Period: {start_date} to {end_date} ({period_desc}) | "
            f"💰 Risk-Free Rate: {risk_free_rate*100:.2f}% | "
            f"📊 Funds Analyzed: {len(funds_returns)} | "
            f"🗄️ Data Source: Cloudflare R2"
        )
