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

from src.visualizations import (create_return_distribution_chart)

from utils.helpers import prepare_data_for_fund_universe

def render(data_loader):
    """Render the Fund Universe page"""
    st.title("🌐 Mutual Fund Universe")
    st.markdown("---")
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

    # Main Content
    with st.spinner("Loading fund data..."):
        # Load fund data
        df = data_loader.load_fund_data_long(
            start_date=start_date.strftime("%Y-%m-%d"),
            end_date=end_date.strftime("%Y-%m-%d"),
            selected_fund_schemes=final_fund_list
        )
        
    analysis_df = prepare_data_for_fund_universe(df)
    
    # Chart 1: Cumulative Returns - Equity Curves
    st.subheader("📈 Fund Universe Metrics")
    return_distribution_fig = create_return_distribution_chart(analysis_df)
    st.plotly_chart(return_distribution_fig, use_container_width=True)

        
        

