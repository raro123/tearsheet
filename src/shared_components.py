"""Shared UI components for reuse across pages"""
import streamlit as st
from datetime import datetime, timedelta
import pandas as pd


def render_date_range_selector(all_funds_df):
    """Render date range selector with smart defaults

    Args:
        all_funds_df: DataFrame with fund metadata including scheme_code

    Returns:
        tuple: (start_date, end_date, period_desc)
    """
    st.subheader("📅 Date Range")

    # Get min and max dates from available data
    # Note: This is a simplified version. In practice, you'd query the actual data
    max_date = datetime.now().date()
    min_date = max_date - timedelta(days=365 * 10)  # Assume 10 years of history

    date_option = st.radio(
        "Select Period",
        options=["1 Year", "3 Years", "5 Years", "10 Years", "Max", "Custom"],
        index=2,
        horizontal=True,
        help="Choose analysis time period"
    )

    if date_option == "Custom":
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=max_date - timedelta(days=365 * 5),
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
        period_desc = "Custom"
    else:
        end_date = max_date
        if date_option == "1 Year":
            start_date = max_date - timedelta(days=365)
            period_desc = "1Y"
        elif date_option == "3 Years":
            start_date = max_date - timedelta(days=365 * 3)
            period_desc = "3Y"
        elif date_option == "5 Years":
            start_date = max_date - timedelta(days=365 * 5)
            period_desc = "5Y"
        elif date_option == "10 Years":
            start_date = max_date - timedelta(days=365 * 10)
            period_desc = "10Y"
        else:  # Max
            start_date = min_date
            period_desc = "Max"

    return start_date, end_date, period_desc


def render_category_filters(all_funds_df, allow_all_level2=True):
    """Render category filter dropdowns

    Args:
        all_funds_df: DataFrame with fund metadata
        allow_all_level2: If True, includes "ALL" option for Level 2

    Returns:
        tuple: (selected_category_level1, selected_category_level2)
    """
    st.subheader("🏷️ Fund Filters")

    # Extract unique categories
    categories_level1 = all_funds_df.scheme_category_level1.dropna().unique().tolist()

    # Category filter - Level 1 (required selection)
    selected_category_level1 = st.selectbox(
        "Scheme Type",
        categories_level1,
        help="Select high-level scheme category"
    )

    # Get level 2 categories based on level 1 selection
    categories_level2 = all_funds_df.query(
        "scheme_category_level1 == @selected_category_level1"
    ).scheme_category_level2.dropna().unique().tolist()

    if allow_all_level2:
        categories_level2 = ["ALL"] + categories_level2
        default_index = 0
    else:
        default_index = 0

    selected_category_level2 = st.selectbox(
        "Scheme Category",
        categories_level2,
        index=default_index,
        help="Select specific scheme category or ALL for entire type"
    )

    return selected_category_level1, selected_category_level2


def render_plan_type_filter():
    """Render plan type filter (Direct/Regular/All)

    Returns:
        str: Selected plan type
    """
    plan_type = st.radio(
        "Plan Type",
        options=["All", "Direct", "Regular"],
        index=0,
        horizontal=True,
        help="Filter funds by plan type"
    )
    return plan_type


def render_fund_multiselect(filtered_funds_df, key_suffix=""):
    """Render fund multi-select with inclusion/exclusion mode

    Args:
        filtered_funds_df: DataFrame with filtered funds
        key_suffix: Unique suffix for widget keys

    Returns:
        tuple: (selected_funds, selection_mode)
    """
    st.subheader("🎯 Fund Selection")

    # Selection mode
    selection_mode = st.radio(
        "Selection Mode",
        options=["Include", "Exclude"],
        index=0,
        horizontal=True,
        help="Include: Show only selected funds | Exclude: Show all except selected",
        key=f"selection_mode_{key_suffix}"
    )

    # Fund multi-select
    fund_options = filtered_funds_df['display_name'].tolist()

    if selection_mode == "Include":
        default_selection = fund_options[:5] if len(fund_options) > 5 else fund_options
        help_text = "Select funds to include in analysis"
    else:
        default_selection = []
        help_text = "Select funds to exclude from analysis"

    selected_funds = st.multiselect(
        "Select Funds",
        options=fund_options,
        default=default_selection,
        help=help_text,
        key=f"fund_select_{key_suffix}"
    )

    return selected_funds, selection_mode


def render_benchmark_selector(all_funds_df, key_suffix=""):
    """Render benchmark selector

    Args:
        all_funds_df: DataFrame with all funds
        key_suffix: Unique suffix for widget keys

    Returns:
        str: Selected benchmark display name
    """
    st.subheader("📊 Benchmark")

    # Get index funds for benchmark options
    index_funds = all_funds_df.query("scheme_category_level2 == 'Index Fund'")
    benchmark_options = index_funds['display_name'].tolist()

    if not benchmark_options:
        st.warning("No index funds available for benchmark")
        return None

    # Default to Nifty 50 or first option
    default_idx = 0
    for i, name in enumerate(benchmark_options):
        if 'nifty 50' in name.lower() or 'nifty50' in name.lower():
            default_idx = i
            break

    selected_benchmark = st.selectbox(
        "Select Benchmark",
        options=benchmark_options,
        index=default_idx,
        help="Choose benchmark for comparison",
        key=f"benchmark_{key_suffix}"
    )

    return selected_benchmark


def render_risk_free_rate():
    """Render risk-free rate input

    Returns:
        float: Risk-free rate as decimal
    """
    risk_free_rate = st.number_input(
        "Risk-Free Rate (%)",
        min_value=0.0,
        max_value=20.0,
        value=2.49,
        step=0.01,
        help="Annual risk-free rate for Sharpe/Sortino calculations"
    )
    return risk_free_rate / 100


def get_final_fund_list(all_funds, selected_funds, selection_mode):
    """Get final list of funds based on selection mode

    Args:
        all_funds: List of all available fund display names
        selected_funds: List of user-selected fund display names
        selection_mode: "Include" or "Exclude"

    Returns:
        list: Final list of fund display names to analyze
    """
    if selection_mode == "Include":
        return selected_funds if selected_funds else all_funds[:10]  # Default to first 10
    else:  # Exclude
        return [f for f in all_funds if f not in selected_funds]


def filter_funds_by_plan_type(funds_df, plan_type):
    """Filter funds DataFrame by plan type

    Args:
        funds_df: DataFrame with fund metadata
        plan_type: "All", "Direct", or "Regular"

    Returns:
        DataFrame: Filtered funds
    """
    if plan_type == "All":
        return funds_df
    else:
        return funds_df[funds_df['plan_type'] == plan_type]
