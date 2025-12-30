"""
Pytest fixtures for metrics testing

Provides reusable test data for all metric calculation tests including:
- Basic return series (simple, positive, negative, zero)
- Benchmark series (aligned and misaligned)
- Edge cases (empty, single value, NaN)
- Drawdown scenarios (with/without recovery)
- Consistency test data
- Constants (TRADING_DAYS, risk-free rate)
"""

import pytest
import pandas as pd
import numpy as np


# ============================================================================
# Basic Return Series
# ============================================================================

@pytest.fixture
def simple_returns():
    """Simple daily returns series for basic tests"""
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns = pd.Series([0.01, -0.005, 0.02, -0.01, 0.015] * 50 + [0.0, 0.0], index=dates)
    return returns


@pytest.fixture
def positive_returns():
    """All positive returns"""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    returns = pd.Series([0.01] * 100, index=dates)
    return returns


@pytest.fixture
def negative_returns():
    """All negative returns"""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    returns = pd.Series([-0.01] * 100, index=dates)
    return returns


@pytest.fixture
def zero_returns():
    """All zero returns"""
    dates = pd.date_range('2020-01-01', periods=50, freq='D')
    return pd.Series([0.0] * 50, index=dates)


# ============================================================================
# Benchmark Series
# ============================================================================

@pytest.fixture
def benchmark_returns():
    """Benchmark returns aligned with simple_returns"""
    dates = pd.date_range('2020-01-01', periods=252, freq='D')
    returns = pd.Series([0.008, -0.003, 0.015, -0.008, 0.012] * 50 + [0.0, 0.0], index=dates)
    return returns


@pytest.fixture
def misaligned_benchmark():
    """Benchmark with different dates (for alignment testing)"""
    dates = pd.date_range('2020-01-15', periods=200, freq='D')
    returns = pd.Series([0.008] * 200, index=dates)
    return returns


# ============================================================================
# Edge Case Series
# ============================================================================

@pytest.fixture
def single_value_returns():
    """Single value series (edge case)"""
    return pd.Series([0.01], index=pd.date_range('2020-01-01', periods=1))


@pytest.fixture
def empty_returns():
    """Empty series"""
    return pd.Series([], dtype=float)


@pytest.fixture
def returns_with_nan():
    """Returns with NaN values"""
    dates = pd.date_range('2020-01-01', periods=10, freq='D')
    return pd.Series([0.01, np.nan, 0.02, -0.01, np.nan, 0.015, 0.0, 0.005, np.nan, 0.01], index=dates)


# ============================================================================
# Drawdown Scenarios
# ============================================================================

@pytest.fixture
def drawdown_with_recovery():
    """Returns that have a drawdown and recover"""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    # Rise, fall (drawdown), recover
    returns = pd.Series([0.02] * 20 + [-0.05] * 30 + [0.08] * 50, index=dates)
    return returns


@pytest.fixture
def drawdown_no_recovery():
    """Returns still in drawdown (never recover)"""
    dates = pd.date_range('2020-01-01', periods=100, freq='D')
    # Rise, then continuous decline
    returns = pd.Series([0.02] * 20 + [-0.01] * 80, index=dates)
    return returns


# ============================================================================
# Consistency Test Data
# ============================================================================

@pytest.fixture
def consistent_outperformer():
    """Fund that consistently beats benchmark"""
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    fund = pd.Series([0.015] * 500, index=dates)
    bench = pd.Series([0.01] * 500, index=dates)
    return fund, bench


@pytest.fixture
def inconsistent_performer():
    """Fund that beats benchmark 50% of the time"""
    dates = pd.date_range('2020-01-01', periods=500, freq='D')
    fund = pd.Series([0.02, 0.005] * 250, index=dates)
    bench = pd.Series([0.01, 0.01] * 250, index=dates)
    return fund, bench


# ============================================================================
# Constants
# ============================================================================

@pytest.fixture
def trading_days():
    """TRADING_DAYS constant"""
    return 252


@pytest.fixture
def default_risk_free_rate():
    """Default risk-free rate"""
    return 0.0249
