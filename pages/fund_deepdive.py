"""Page 3: Fund Deepdive

Comprehensive performance analysis for a single fund vs benchmark
This is the original tearsheet functionality
"""
import streamlit as st
import pandas as pd
import hashlib
from src.data_loader import calculate_returns
from src.metrics import calculate_all_metrics, create_sip_progression_table
from src.computation_cache import (
    get_cached_metrics,
    get_cached_annual_returns,
    get_cached_monthly_returns,
    get_cache_stats,
    clear_cache_on_data_change
)
from src.visualizations import (
    create_cumulative_returns_chart,
    create_log_returns_chart,
    create_annual_returns_chart,
    create_drawdown_comparison_chart,
    create_rolling_returns_chart,
    create_monthly_returns_table,
    create_monthly_returns_scatter,
    create_comparison_metrics_table,
    create_performance_overview_subplot,
    create_rolling_analysis_subplot
)
from utils.helpers import create_metrics_comparison_df, get_period_description, create_metric_category_df, highlight_outliers_in_monthly_table, format_sip_table
from src.shared_components import filter_funds_by_plan_type


def render(data_loader):
    """Render the Fund Deepdive page

    Args:
        data_loader: R2DataLoader instance from session state
    """
    # Page header - compact caption style
    st.caption("🔍 **Fund Deepdive** | Comprehensive performance analysis for a single fund")

    # Sidebar Configuration
    with st.sidebar:
        st.header("⚙️ Analysis Settings")

        # Get all funds
        all_funds = data_loader.get_available_funds()

        # Plan Type filter
        st.subheader("🏷️ Plan Type")
        plan_type = st.radio(
            "Plan Type",
            options=["All", "Direct", "Regular"],
            index=0,  # Default to "All"
            horizontal=True,
            help="Filter funds by plan type",
            key="fd_plan_type"
        )

        # Apply plan type filter to all_funds
        all_funds = filter_funds_by_plan_type(all_funds, plan_type)

        st.markdown("---")

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

        st.markdown("---")

        # Comparison Fund Selection (Optional)
        st.subheader("🔬 Add Comparison Fund (Optional)")

        enable_comparison = st.checkbox(
            "Enable Comparison Fund",
            value=False,
            help="Add a third fund to compare alongside strategy and benchmark",
            key="fd_enable_comparison"
        )

        if enable_comparison:
            # Category filters for comparison fund
            st.caption("**Fund Filters**")

            comparison_categories_level1 = all_funds.scheme_category_level1.dropna().unique().tolist()

            selected_comparison_category_level1 = st.selectbox(
                "Scheme Type",
                comparison_categories_level1,
                help="Select high-level scheme category",
                key="fd_comp_cat_l1"
            )

            # Get level 2 categories for comparison
            comparison_categories_level2 = (all_funds
                                           .query("scheme_category_level1 == @selected_comparison_category_level1")
                                           .scheme_category_level2.unique().tolist())
            comparison_categories_level2 = ["ALL"] + comparison_categories_level2

            selected_comparison_category_level2 = st.selectbox(
                "Scheme Category",
                comparison_categories_level2,
                help="Select specific scheme category",
                key="fd_comp_cat_l2"
            )

            # Filter funds based on category selection
            if selected_comparison_category_level2 == "ALL":
                comparison_fund_options = (all_funds
                    .query("scheme_category_level1 == @selected_comparison_category_level1")
                    ['display_name'].tolist())
            else:
                comparison_fund_options = (all_funds
                    .query("scheme_category_level1 == @selected_comparison_category_level1 and scheme_category_level2 == @selected_comparison_category_level2")
                    ['display_name'].tolist())

            # Exclude currently selected strategy fund
            comparison_fund_options = [f for f in comparison_fund_options if f != selected_fund_scheme]

            st.caption("**Fund Selection**")
            selected_comparison_fund = st.selectbox(
                "Comparison Fund",
                comparison_fund_options,
                help="Select a fund to compare",
                key="fd_comparison_fund"
            )
        else:
            selected_comparison_fund = None

        st.caption(f"**Strategy:** {selected_fund_scheme}")
        st.caption(f"**Benchmark:** {selected_benchmark_index} ({index_type})")
        if enable_comparison and selected_comparison_fund:
            st.caption(f"**Comparison:** {selected_comparison_fund}")

        # Date range
        st.subheader("📅 Analysis Period")
        col1, col2 = st.columns(2)

        # Get date ranges
        fund_scheme_code = selected_fund_scheme.split('|')[1]
        fund_min_date, fund_max_date = data_loader.get_fund_date_range(fund_scheme_code)
        benchmark_min_date, benchmark_max_date = data_loader.get_benchmark_date_range(selected_benchmark_index, index_type)

        # Get comparison fund date range if enabled
        comparison_min_date = None
        comparison_max_date = None
        if enable_comparison and selected_comparison_fund:
            comparison_scheme_code = selected_comparison_fund.split('|')[1]
            comparison_min_date, comparison_max_date = data_loader.get_fund_date_range(comparison_scheme_code)

        # Calculate common date range across all selected items
        date_ranges_start = [d for d in [fund_min_date, benchmark_min_date, comparison_min_date] if d is not None]
        date_ranges_end = [d for d in [fund_max_date, benchmark_max_date, comparison_max_date] if d is not None]

        common_min_date = max(date_ranges_start) if date_ranges_start else None
        common_max_date = min(date_ranges_end) if date_ranges_end else None

        overall_min_date, overall_max_date = data_loader.get_data_date_range()

        # Create dynamic keys based on selections to reset dates when selections change
        # This ensures date inputs update to new common ranges when fund selections change
        comparison_part = selected_comparison_fund if (enable_comparison and selected_comparison_fund) else ""
        selections_str = f"{selected_fund_scheme}_{selected_benchmark_index}_{comparison_part}"
        selections_hash = hashlib.md5(selections_str.encode()).hexdigest()[:8]

        with col1:
            start_date = st.date_input(
                "Start Date",
                value=common_min_date if common_min_date else overall_min_date,
                min_value=overall_min_date,
                max_value=overall_max_date,
                key=f"fd_start_{selections_hash}"
            )

        with col2:
            end_date = st.date_input(
                "End Date",
                value=common_max_date if common_max_date else overall_max_date,
                min_value=overall_min_date,
                max_value=overall_max_date,
                key=f"fd_end_{selections_hash}"
            )

        period_desc = get_period_description(pd.Timestamp(start_date), pd.Timestamp(end_date))
        # Show which items' data availability determined the default range
        if enable_comparison and selected_comparison_fund:
            st.caption(f"Analysis period: {period_desc} | Common data range for Main Fund, Benchmark & Comp Fund")
        else:
            st.caption(f"Analysis period: {period_desc} | Common data range for Main Fund & Benchmark")

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

        # Log scale toggle
        log_scale = st.toggle(
            "Log Scale for Cumulative Returns",
            value=True,
            help="Apply logarithmic scale to cumulative returns chart",
            key="fd_log_scale"
        )

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
        if st.button("🔄 Clear Cache", help="Clear all cached computations", key="fd_clear_cache"):
            clear_cache_on_data_change()
            st.cache_data.clear()
            st.success("✅ Cache cleared!")
            st.rerun()

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

    # Calculate metrics using session cache
    strategy_metrics = get_cached_metrics(
        strategy_name, strategy_returns, benchmark_returns,
        risk_free_rate, start_date, end_date
    )
    benchmark_metrics = get_cached_metrics(
        benchmark_name, benchmark_returns, None,
        risk_free_rate, start_date, end_date
    )

    # Load comparison fund data if enabled
    if enable_comparison and selected_comparison_fund:
        with st.spinner("Loading comparison fund data..."):
            comparison_df = data_loader.load_fund_data(
                start_date=start_date,
                end_date=end_date,
                selected_fund_schemes=[selected_comparison_fund]
            )

            if comparison_df is not None and len(comparison_df) > 0:
                comparison_nav = comparison_df[selected_comparison_fund]
                comparison_returns = calculate_returns(comparison_nav)
                comparison_name = selected_comparison_fund

                # Calculate metrics for comparison fund
                comparison_metrics = get_cached_metrics(
                    comparison_name, comparison_returns, benchmark_returns,
                    risk_free_rate, start_date, end_date
                )
            else:
                st.warning("⚠️ No data available for comparison fund in selected date range")
                comparison_returns = None
                comparison_name = None
                comparison_metrics = None
    else:
        comparison_returns = None
        comparison_name = None
        comparison_metrics = None

    # Calculate SIP table for IRR extraction (used in KPI and chart later)
    sip_table_df = create_sip_progression_table(
        strategy_returns,
        benchmark_returns,
        comparison_returns,
        monthly_investment=100
    )

    # Extract IRR values from SIP table (last row)
    irr_row = sip_table_df.iloc[-1]
    fund_irr = irr_row['Fund Value']
    benchmark_irr = irr_row['Benchmark Value']
    comparison_irr = irr_row['Comp Value'] if 'Comp Value' in irr_row and comparison_returns is not None else None

    # === SECTION 1: PERFORMANCE SUMMARY ===
    # Dynamic header based on comparison fund selection
    if comparison_returns is not None:
        st.caption(
            f"📊 <span style='color:#f59e0b; font-weight:bold'>{strategy_name}</span> vs "
            f"<span style='color:#6B7280; font-weight:bold'>{benchmark_name}</span> vs "
            f"<span style='color:#10b981; font-weight:bold'>{comparison_name}</span> | "
            f"Period: {start_date} to {end_date} ({period_desc})",
            unsafe_allow_html=True
        )
    else:
        st.caption(
            f"📊 <span style='color:#f59e0b; font-weight:bold'>{strategy_name}</span> vs "
            f"<span style='color:#6B7280; font-weight:bold'>{benchmark_name}</span> | "
            f"Period: {start_date} to {end_date} ({period_desc})",
            unsafe_allow_html=True
        )

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:
        st.metric(
            "IRR",
            f"{fund_irr:.1f}%",
            delta=f"{(fund_irr - benchmark_irr):.1f}% vs BM",
            help="Internal Rate of Return (annualized) for ₹100/month SIP"
        )
        if comparison_returns is not None and comparison_irr is not None:
            st.metric(
                label="",
                value="",
                delta=f"{(fund_irr - comparison_irr):.1f}% vs CF",
                label_visibility="collapsed"
            )

    with col2:
        st.metric(
            "CAGR",
            f"{strategy_metrics['CAGR']*100:.1f}%",
            delta=f"{(strategy_metrics['CAGR'] - benchmark_metrics['CAGR'])*100:.1f}% vs BM",
            help="Compound Annual Growth Rate"
        )
        if comparison_returns is not None:
            delta_cf = (strategy_metrics['CAGR'] - comparison_metrics['CAGR'])*100
            st.metric(
                label="",
                value="",
                delta=f"{delta_cf:.1f}% vs CF",
                label_visibility="collapsed"
            )

    with col3:
        st.metric(
            "Total Return",
            f"{strategy_metrics['Cumulative Return']*100:.1f}%",
            delta=f"{(strategy_metrics['Cumulative Return'] - benchmark_metrics['Cumulative Return'])*100:.1f}% vs BM",
            help="Total cumulative return over the period"
        )
        if comparison_returns is not None:
            delta_cf = (strategy_metrics['Cumulative Return'] - comparison_metrics['Cumulative Return'])*100
            st.metric(
                label="",
                value="",
                delta=f"{delta_cf:.1f}% vs CF",
                label_visibility="collapsed"
            )

    with col4:
        st.metric(
            "Sharpe Ratio",
            f"{strategy_metrics['Sharpe Ratio']:.2f}",
            delta=f"{strategy_metrics['Sharpe Ratio'] - benchmark_metrics['Sharpe Ratio']:.2f} vs BM",
            help="Risk-adjusted return metric"
        )
        if comparison_returns is not None:
            delta_cf = strategy_metrics['Sharpe Ratio'] - comparison_metrics['Sharpe Ratio']
            st.metric(
                label="",
                value="",
                delta=f"{delta_cf:.2f} vs CF",
                label_visibility="collapsed"
            )

    with col5:
        st.metric(
            "Max Drawdown",
            f"{strategy_metrics['Max Drawdown']*100:.1f}%",
            delta=f"{(benchmark_metrics['Max Drawdown'] - strategy_metrics['Max Drawdown'])*100:.1f}% vs BM",
            delta_color="inverse",
            help="Maximum peak-to-trough decline"
        )
        if comparison_returns is not None:
            delta_cf = (comparison_metrics['Max Drawdown'] - strategy_metrics['Max Drawdown'])*100
            st.metric(
                label="",
                value="",
                delta=f"{delta_cf:.1f}% vs CF",
                delta_color="inverse",
                label_visibility="collapsed"
            )

    with col6:
        st.metric(
            "Volatility",
            f"{strategy_metrics['Volatility (ann.)']*100:.1f}%",
            delta=f"{(strategy_metrics['Volatility (ann.)'] - benchmark_metrics['Volatility (ann.)'])*100:.1f}% vs BM",
            delta_color="inverse",
            help="Annualized standard deviation"
        )
        if comparison_returns is not None:
            delta_cf = (strategy_metrics['Volatility (ann.)'] - comparison_metrics['Volatility (ann.)'])*100
            st.metric(
                label="",
                value="",
                delta=f"{delta_cf:.1f}% vs CF",
                delta_color="inverse",
                label_visibility="collapsed"
            )

    st.markdown("---")

    # === SECTION 2A: PERFORMANCE OVERVIEW ===

    # Integrated 4-row performance overview (SIP + Cumulative + Drawdown + Annual)
    st.plotly_chart(
        create_performance_overview_subplot(
            strategy_returns, benchmark_returns,
            strategy_name, benchmark_name,
            comparison_returns, comparison_name,
            log_scale=log_scale,
            sip_table_df=sip_table_df
        ),
        use_container_width=True
    )

    # === SECTION 2B: PERFORMANCE METRICS ===
    st.markdown("---")
    st.caption("📊 **Performance Metrics** | Comprehensive metrics across return, risk, and ratio categories")

    # Shorten names for display
    strategy_display = strategy_name if len(strategy_name) <= 30 else strategy_name[:27] + "..."
    benchmark_display = benchmark_name if len(benchmark_name) <= 30 else benchmark_name[:27] + "..."
    comparison_display = None
    if comparison_name:
        comparison_display = comparison_name if len(comparison_name) <= 30 else comparison_name[:27] + "..."

    # Define metric categories
    return_metrics = ['Cumulative Return', 'CAGR', 'Expected Annual Return', 'Expected Monthly Return', 'Expected Daily Return', 'Win Rate', 'Max Consecutive Wins']
    risk_metrics = ['Volatility (ann.)', 'Max Drawdown', 'Avg Drawdown', 'Longest DD Days', 'Skewness', 'VaR (95%)', 'CVaR (95%)']
    ratio_metrics = ['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio', 'Omega Ratio', 'Lower Tail Ratio', 'Upper Tail Ratio']

    col1, col2, col3 = st.columns(3)

    with col1:
        st.caption("📊 **Return Metrics**")
        return_df = create_metric_category_df(strategy_metrics, benchmark_metrics, return_metrics,
                                              strategy_display, benchmark_display,
                                              comparison_metrics, comparison_display)
        st.dataframe(return_df, hide_index=True, use_container_width=True)

    with col2:
        st.caption("⚠️ **Risk Metrics**")
        risk_df = create_metric_category_df(strategy_metrics, benchmark_metrics, risk_metrics,
                                            strategy_display, benchmark_display,
                                            comparison_metrics, comparison_display)
        st.dataframe(risk_df, hide_index=True, use_container_width=True)

    with col3:
        st.caption("📈 **Ratio Metrics**")
        ratio_df = create_metric_category_df(strategy_metrics, benchmark_metrics, ratio_metrics,
                                             strategy_display, benchmark_display,
                                             comparison_metrics, comparison_display)
        st.dataframe(ratio_df, hide_index=True, use_container_width=True)

    # Helper text with color indicators (shown once below all tables)
    if comparison_metrics is not None:
        st.caption(f"🟠 Main Fund: {strategy_display} | 🔵 Benchmark: {benchmark_display} | 🟢 Comp Fund: {comparison_display}")
    else:
        st.caption(f"🟠 Main Fund: {strategy_display} | 🔵 Benchmark: {benchmark_display}")

    # === SECTION 2C: ADDITIONAL CHARTS ===
    st.markdown("---")

    # === SECTION 2C: ROLLING ANALYSIS ===
    st.caption("📊 **Rolling Analysis** | Multi-metric performance tracking over time")

    # Period selection only
    rolling_period_option = st.radio(
        "Rolling Period",
        options=["6 months", "1 year", "3 years", "5 years"],
        index=1,  # Default: 1 year
        horizontal=True,
        key="fd_rolling_period_radio"
    )

    # Map selections to parameters
    period_mapping = {
        "6 months": {"days": 126, "span": 63, "label": "6 Months"},
        "1 year": {"days": 252, "span": 126, "label": "1 Year"},
        "3 years": {"days": 756, "span": 378, "label": "3 Years"},
        "5 years": {"days": 1260, "span": 630, "label": "5 Years"}
    }

    period_config = period_mapping[rolling_period_option]

    # Display subplot (always use simple rolling)
    st.plotly_chart(
        create_rolling_analysis_subplot(
            strategy_returns, benchmark_returns,
            strategy_name, benchmark_name,
            window=period_config["days"],
            ewm_span=period_config["span"],
            use_ewm=False,  # Always use simple rolling
            period_label=period_config["label"],
            comparison_returns=comparison_returns,
            comparison_name=comparison_name
        ),
        use_container_width=True
    )

    # === SECTION 3: MONTHLY RETURNS ANALYSIS ===
    st.markdown("---")

    # Create toggle in the header area
    col_header, col_toggle = st.columns([5, 1])

    with col_header:
        st.caption("📊 **Monthly Returns Analysis** | Scatter plot and detailed monthly breakdown")

    # Get monthly returns for scatter plot (needed for both subsections)
    strategy_monthly = get_cached_monthly_returns(strategy_name, strategy_returns, start_date, end_date)
    benchmark_monthly = get_cached_monthly_returns(benchmark_name, benchmark_returns, start_date, end_date)

    if comparison_returns is not None:
        comparison_monthly = get_cached_monthly_returns(comparison_name, comparison_returns, start_date, end_date)
    else:
        comparison_monthly = None

    # Checkbox to toggle comparison fund (only show if comparison exists)
    show_comp_in_section = True
    if comparison_returns is not None:
        with col_toggle:
            show_comp_in_section = st.checkbox(
                "Show Comp Fund",
                value=True,
                key="fd_show_comp_monthly_section",
                help="Toggle comparison fund in scatter and tables"
            )

    # Subsection 1: Scatter Plot
    st.markdown("#### Scatter: Fund vs Benchmark Returns")

    col_scatter, col_metrics = st.columns([2, 1])

    with col_metrics:
        st.caption("**Comparison Metrics vs Benchmark**")

        metrics_df = create_comparison_metrics_table(
            strategy_metrics, benchmark_name,
            comparison_metrics if comparison_returns is not None else None,
            comparison_name if comparison_returns is not None else None
        )

        st.dataframe(metrics_df, hide_index=True, use_container_width=True)

        # Helper text
        st.caption("**R²**: % variance explained by benchmark")
        st.caption("**Correlation**: Strength of relationship (-1 to 1)")
        st.caption("**Beta**: Sensitivity to benchmark moves")

    with col_scatter:
        # Only pass comparison data if checkbox is checked
        scatter_comparison_monthly = comparison_monthly if show_comp_in_section else None
        scatter_comparison_name = comparison_name if show_comp_in_section else None

        scatter_fig = create_monthly_returns_scatter(
            strategy_monthly, benchmark_monthly,
            strategy_name, benchmark_name,
            scatter_comparison_monthly, scatter_comparison_name
        )
        st.plotly_chart(scatter_fig, use_container_width=True)

    # Subsection 2: Monthly Returns Tables (Collapsible)
    with st.expander("📅 **Monthly Returns Tables** | Outlier-highlighted (±2σ)", expanded=False):
        st.caption("Detailed monthly breakdown with statistical outliers highlighted")

        # Determine number of columns based on toggle
        if comparison_returns is not None and show_comp_in_section:
            col1, col2, col3 = st.columns(3)
        else:
            col1, col2 = st.columns(2)

        with col1:
            st.caption(f"**{strategy_name}**")
            strategy_monthly_table = create_monthly_returns_table(strategy_returns)
            styled_strategy = highlight_outliers_in_monthly_table(strategy_monthly_table)

            st.dataframe(
                styled_strategy,
                hide_index=True,
                use_container_width=True,
                height=400
            )

        with col2:
            st.caption(f"**{benchmark_name}**")
            benchmark_monthly_table = create_monthly_returns_table(benchmark_returns)
            styled_benchmark = highlight_outliers_in_monthly_table(benchmark_monthly_table)

            st.dataframe(
                styled_benchmark,
                hide_index=True,
                use_container_width=True,
                height=400
            )

        # Add third column for comparison fund if toggle is ON
        if comparison_returns is not None and show_comp_in_section:
            with col3:
                st.caption(f"**{comparison_name}**")
                comparison_monthly_table = create_monthly_returns_table(comparison_returns)
                styled_comparison = highlight_outliers_in_monthly_table(comparison_monthly_table)

                st.dataframe(
                    styled_comparison,
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
