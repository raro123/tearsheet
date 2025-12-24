"""
Computation Cache Module

Provides session-based caching for expensive metric calculations and data transformations.
Prevents redundant calculations across visualization functions and UI interactions.
"""

import streamlit as st
import pandas as pd
import numpy as np
from src.metrics import calculate_all_metrics


def get_cache_key(fund_name, start_date, end_date, risk_free_rate):
    """
    Generate cache key for metrics computation.

    Parameters:
    -----------
    fund_name : str
        Fund name or identifier
    start_date : str or datetime
        Start date of analysis period
    end_date : str or datetime
        End date of analysis period
    risk_free_rate : float
        Annual risk-free rate

    Returns:
    --------
    str
        Unique cache key
    """
    return f"{fund_name}_{start_date}_{end_date}_{risk_free_rate:.4f}"


def get_cached_metrics(fund_name, returns, benchmark_returns, risk_free_rate,
                       start_date, end_date):
    """
    Get metrics from session state cache or calculate if not cached.

    This function prevents redundant metric calculations across:
    - Initial metrics loop
    - Distribution chart functions
    - Final metrics table

    Parameters:
    -----------
    fund_name : str
        Fund name or identifier
    returns : pd.Series
        Fund returns series
    benchmark_returns : pd.Series or None
        Benchmark returns series
    risk_free_rate : float
        Annual risk-free rate
    start_date : str or datetime
        Start date of analysis period
    end_date : str or datetime
        End date of analysis period

    Returns:
    --------
    dict
        Dictionary containing all calculated metrics
    """
    # Initialize cache if not exists
    if 'metrics_cache' not in st.session_state:
        st.session_state.metrics_cache = {}

    cache_key = get_cache_key(fund_name, start_date, end_date, risk_free_rate)

    # Calculate only if not in cache
    if cache_key not in st.session_state.metrics_cache:
        metrics = calculate_all_metrics(returns, benchmark_returns, risk_free_rate)
        st.session_state.metrics_cache[cache_key] = metrics

    return st.session_state.metrics_cache[cache_key]


def get_cached_annual_returns(fund_name, returns, start_date, end_date):
    """
    Cache annual returns resampling.

    Prevents redundant .resample('YE') operations across visualization functions.

    Parameters:
    -----------
    fund_name : str
        Fund name or identifier
    returns : pd.Series
        Daily returns series with datetime index
    start_date : str or datetime
        Start date of analysis period
    end_date : str or datetime
        End date of analysis period

    Returns:
    --------
    pd.Series
        Annual returns (compounded from daily returns)
    """
    # Initialize cache if not exists
    if 'annual_returns_cache' not in st.session_state:
        st.session_state.annual_returns_cache = {}

    cache_key = f"{fund_name}_{start_date}_{end_date}"

    # Calculate only if not in cache
    if cache_key not in st.session_state.annual_returns_cache:
        annual_returns = returns.resample('YE').apply(lambda x: (1 + x).prod() - 1)
        st.session_state.annual_returns_cache[cache_key] = annual_returns

    return st.session_state.annual_returns_cache[cache_key]


def get_cached_monthly_returns(fund_name, returns, start_date, end_date):
    """
    Cache monthly returns resampling.

    Prevents redundant .resample('ME') operations for heatmaps and tables.

    Parameters:
    -----------
    fund_name : str
        Fund name or identifier
    returns : pd.Series
        Daily returns series with datetime index
    start_date : str or datetime
        Start date of analysis period
    end_date : str or datetime
        End date of analysis period

    Returns:
    --------
    pd.Series
        Monthly returns (compounded from daily returns)
    """
    # Initialize cache if not exists
    if 'monthly_returns_cache' not in st.session_state:
        st.session_state.monthly_returns_cache = {}

    cache_key = f"{fund_name}_{start_date}_{end_date}"

    # Calculate only if not in cache
    if cache_key not in st.session_state.monthly_returns_cache:
        monthly_returns = returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)
        st.session_state.monthly_returns_cache[cache_key] = monthly_returns

    return st.session_state.monthly_returns_cache[cache_key]


def clear_cache_on_data_change():
    """
    Clear all computation caches when data parameters change.

    Should be called when:
    - Date range changes
    - Fund selection changes
    - Risk-free rate changes
    - Category selection changes
    """
    cache_keys = ['metrics_cache', 'annual_returns_cache', 'monthly_returns_cache']

    for key in cache_keys:
        if key in st.session_state:
            st.session_state[key] = {}


def get_cache_stats():
    """
    Get statistics about current cache usage.

    Returns:
    --------
    dict
        Cache statistics including entry counts and estimated memory usage
    """
    stats = {
        'metrics_entries': 0,
        'annual_returns_entries': 0,
        'monthly_returns_entries': 0,
        'total_entries': 0
    }

    if 'metrics_cache' in st.session_state:
        stats['metrics_entries'] = len(st.session_state.metrics_cache)

    if 'annual_returns_cache' in st.session_state:
        stats['annual_returns_entries'] = len(st.session_state.annual_returns_cache)

    if 'monthly_returns_cache' in st.session_state:
        stats['monthly_returns_entries'] = len(st.session_state.monthly_returns_cache)

    stats['total_entries'] = sum([
        stats['metrics_entries'],
        stats['annual_returns_entries'],
        stats['monthly_returns_entries']
    ])

    return stats
