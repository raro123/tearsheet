"""Page 1: Mutual Fund Universe

Placeholder page for future fund universe functionality
"""
import streamlit as st
from src.shared_components import (
    render_date_range_selector,
    render_category_filters,
    render_plan_type_filter,
    render_fund_multiselect,
    render_risk_free_rate,
    get_final_fund_list,
    filter_funds_by_plan_type
)

from src.visualizations import (create_return_box_plot_chart)

from utils.helpers import prepare_data_for_fund_universe, calculate_fund_metrics_table
from src.computation_cache import get_cache_stats, clear_cache_on_data_change
import pandas as pd

def render(data_loader):
    """Render the Fund Universe page"""
    # Page header - compact caption style
    st.caption("🌐 **Mutual Fund Universe** | Explore and compare funds across categories")

    with st.sidebar:
        st.header("⚙️ Analysis Settings")

        # Get all funds
        all_funds = data_loader.get_available_funds()

        # Category filters (no "ALL" for level 2)
        st.subheader("🏷️ Fund Filters")

        # Extract unique categories
        categories_level1 = all_funds.scheme_category_level1.dropna().unique().tolist()

        # Category filter - Level 1 (required selection)
        selected_category_level1 = st.selectbox(
            "Scheme Type",
            categories_level1,
            help="Select high-level scheme category"
        )

        # Plan type filter
        plan_type = render_plan_type_filter()

        # Filter funds by category and plan type
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
        if st.button("🔄 Clear Cache", help="Clear all cached computations", key="fu_clear_cache"):
            clear_cache_on_data_change()
            st.cache_data.clear()
            st.success("✅ Cache cleared!")
            st.rerun()

    # Main Content
    with st.spinner("Loading fund data..."):
        # Load fund data
        df = data_loader.load_fund_data_long(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            selected_fund_schemes=final_fund_list
        )
        
    analysis_df = prepare_data_for_fund_universe(df)

    # === SECTION 1: RETURN DISTRIBUTION ===
    st.caption(f"📊 **Return Distribution by Category** | Period: {start_date} to {end_date} ({period_desc}) | {len(final_fund_list)} funds")
    return_distribution_fig, category_order = create_return_box_plot_chart(analysis_df)
    st.plotly_chart(return_distribution_fig, use_container_width=True)

    # === SECTION 2: CATEGORY & FUND METRICS ===
    st.markdown("---")
    st.caption("📋 **Category & Fund Metrics** | Expand each category to view detailed fund performance")

    with st.spinner("Calculating metrics..."):
        fund_metrics_df, category_metrics_df = calculate_fund_metrics_table(
            df, risk_free_rate / 100, start_date, end_date
        )

    # Sort categories to match boxplot order
    category_metrics_df['category'] = pd.Categorical(
        category_metrics_df['category'],
        categories=category_order,
        ordered=True
    )
    category_metrics_df = category_metrics_df.sort_values('category')

    # Display collapsible table for each category
    for _, cat_row in category_metrics_df.iterrows():
        category = cat_row['category']

        # Create expander header with category-level metrics
        header = f"**{category}** | Median Return: {cat_row['median_return']*100:.0f}% | Mean Return: {cat_row['mean_return']*100:.0f}% | Median Vol: {cat_row['median_volatility']*100:.0f}% | DD Range: {cat_row['min_drawdown']*100:.0f}% to {cat_row['max_drawdown']*100:.0f}% | Sharpe Range: {cat_row['min_sharpe']:.1f} to {cat_row['max_sharpe']:.1f}"

        with st.expander(header, expanded=False):
            # Get funds in this category
            category_funds = fund_metrics_df[fund_metrics_df['category'] == category].copy()

            # Sort by CAGR descending
            category_funds = category_funds.sort_values('CAGR', ascending=False)

            # Prepare display dataframe with ALL metrics
            display_df = category_funds[[
                'display_name',
                'data_range',
                'annual_return_trend',
                'Cumulative Return',
                'CAGR',
                'Volatility (ann.)',
                'Sharpe Ratio',
                'Sortino Ratio',
                'Calmar Ratio',
                'Omega Ratio',
                'Max Drawdown',
                'Avg Drawdown',
                'Longest DD Days',
                'Lower Tail Ratio',
                'Upper Tail Ratio'
            ]].copy()

            # Rename columns for display
            display_df.columns = [
                'Fund',
                'Data Range',
                'Annual Return Trend',
                'Cumulative Return',
                'CAGR',
                'Volatility (ann.)',
                'Sharpe Ratio',
                'Sortino Ratio',
                'Calmar Ratio',
                'Omega Ratio',
                'Max Drawdown',
                'Avg Drawdown',
                'Longest DD Days',
                'Lower Tail Ratio',
                'Upper Tail Ratio'
            ]

            # Convert percentage metrics (stored as 0.15 for 15%)
            pct_cols = ['Cumulative Return', 'CAGR', 'Volatility (ann.)', 'Max Drawdown']
            for col in pct_cols:
                display_df[col] = display_df[col] * 100  # Convert to percentage

            # Configure columns using st.column_config
            column_config = {}

            # Text column for fund name
            column_config['Fund'] = st.column_config.TextColumn(
                'Fund',
                help="Fund name and code",
                width="large"
            )

            # Text column for data range
            column_config['Data Range'] = st.column_config.TextColumn(
                'Data Range',
                help="Date range of available data (YYYY-YYYY format)",
                width="small"
            )

            # Line chart column for annual return trend
            column_config['Annual Return Trend'] = st.column_config.LineChartColumn(
                'Annual Return Trend',
                help="Annual returns (%) for each year in the selected period",
                y_min=-50,
                y_max=100
            )

            # Percentage columns (show as "15.23%" for 15.23)
            for col in pct_cols:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f%%",
                    help=f"{col} as percentage"
                )

            # Other numeric columns (show as "1.25" for 1.25)
            for col in ['Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio', 'Omega Ratio',
                        'Avg Drawdown', 'Lower Tail Ratio', 'Upper Tail Ratio']:
                column_config[col] = st.column_config.NumberColumn(
                    col,
                    format="%.2f"
                )

            # Integer column for longest drawdown days
            column_config['Longest DD Days'] = st.column_config.NumberColumn(
                'Longest DD Days',
                format="%d",
                help="Duration of longest drawdown in days"
            )

            # Display table with configuration
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                height=400,  # Fixed height like category deepdive
                column_config=column_config
            )

            st.caption(f"📊 {len(category_funds)} fund(s) in {category}")

