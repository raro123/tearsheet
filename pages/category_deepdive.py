"""Page 2: Fund Category Deepdive

Compare multiple funds within a category using various visualizations
"""
import streamlit as st
import pandas as pd
from src.data_loader import calculate_returns
from src.metrics import calculate_all_metrics
from src.visualizations import (
    create_category_equity_curves,
    create_annual_returns_bubble_chart,
    create_bubble_scatter_chart,
    create_rolling_metric_chart
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
    st.title("📈 Fund Category Deepdive")
    st.markdown("Compare multiple funds within a category")
    st.markdown("---")

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
        start_date, end_date, period_desc = render_date_range_selector(all_funds)

        st.markdown("---")

        # Risk-free rate
        risk_free_rate = render_risk_free_rate()

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

                    # Calculate metrics
                    fund_metrics = calculate_all_metrics(fund_returns, benchmark_returns, risk_free_rate)
                    fund_metrics['Fund'] = fund_name
                    funds_metrics.append(fund_metrics)

        if not funds_returns:
            st.error("❌ No valid fund data available for selected funds")
            return

        # Calculate benchmark metrics
        benchmark_metrics = calculate_all_metrics(benchmark_returns, risk_free_rate=risk_free_rate)

        # Create metrics DataFrame
        metrics_df = pd.DataFrame(funds_metrics)

        # Display summary
        st.header(f"📊 Category: {selected_category_level1} - {selected_category_level2}")
        st.caption(f"Period: {start_date} to {end_date} ({period_desc}) | {len(funds_returns)} funds")

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            avg_return = metrics_df['CAGR'].mean() * 100
            st.metric("Avg CAGR", f"{avg_return:.2f}%")

        with col2:
            avg_sharpe = metrics_df['Sharpe Ratio'].mean()
            st.metric("Avg Sharpe", f"{avg_sharpe:.2f}")

        with col3:
            avg_volatility = metrics_df['Volatility (ann.)'].mean() * 100
            st.metric("Avg Volatility", f"{avg_volatility:.2f}%")

        with col4:
            avg_drawdown = metrics_df['Max Drawdown'].mean() * 100
            st.metric("Avg Max DD", f"{avg_drawdown:.2f}%")

        st.markdown("---")

        # Chart 1: Cumulative Returns - Equity Curves
        st.subheader("📈 Equity Curves - Cumulative Returns")
        st.caption("Compare cumulative performance of all funds in the category")

        fig1 = create_category_equity_curves(funds_returns, benchmark_returns, benchmark_name)
        st.plotly_chart(fig1, use_container_width=True)

        st.markdown("---")

        # Chart 2: Annual Returns Bubble Chart
        st.subheader("📊 Annual Returns by Year")
        st.caption("Bubble size represents annual volatility")

        fig2 = create_annual_returns_bubble_chart(
            funds_returns, benchmark_returns, benchmark_name,
            start_date, end_date
        )
        st.plotly_chart(fig2, use_container_width=True)

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

        # Metrics Table
        st.subheader("📊 Detailed Metrics Table")
        st.caption("Complete performance metrics for all funds in the category")

        # Prepare benchmark display
        benchmark_display = benchmark_metrics.copy()
        benchmark_display['Fund'] = f"🔷 {benchmark_name}"

        # Create benchmark DataFrame with Fund column first
        benchmark_df = pd.DataFrame([benchmark_display])
        cols = ['Fund'] + [col for col in benchmark_df.columns if col != 'Fund']
        benchmark_df = benchmark_df[cols]

        # Format benchmark metrics
        pct_cols = ['Cumulative Return', 'CAGR', 'Volatility (ann.)', 'Max Drawdown']
        for col in benchmark_df.columns:
            if col in pct_cols:
                benchmark_df[col] = benchmark_df[col].apply(lambda x: f"{x*100:.2f}%")
            elif col not in ['Fund'] and benchmark_df[col].dtype in ['float64', 'int64']:
                benchmark_df[col] = benchmark_df[col].apply(lambda x: f"{x:.2f}")

        # Display benchmark table (fixed at top)
        st.markdown("**Benchmark Reference**")
        styled_benchmark = benchmark_df.style.apply(
            lambda x: ['background-color: #FEF3C7; font-weight: bold'] * len(x), axis=1
        )
        st.dataframe(
            styled_benchmark,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # Prepare fund metrics for display
        display_metrics = metrics_df.copy()

        # Reorder columns to put Fund first
        cols = ['Fund'] + [col for col in display_metrics.columns if col != 'Fund']
        display_metrics = display_metrics[cols]

        # Convert percentage columns from decimal to percentage (0.1 -> 10.0)
        for col in pct_cols:
            if col in display_metrics.columns:
                display_metrics[col] = display_metrics[col] * 100

        # Create column config for proper formatting
        column_config = {}
        for col in display_metrics.columns:
            if col in pct_cols:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f%%",
                    help=f"{col} as percentage"
                )
            elif col not in ['Fund'] and display_metrics[col].dtype in ['float64', 'int64']:
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
