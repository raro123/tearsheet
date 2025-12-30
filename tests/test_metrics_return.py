"""
Tests for return metric calculations

Tests the following functions from src.metrics:
- calculate_cumulative_return()
- calculate_cagr()
- calculate_expected_returns()

Coverage includes:
- Normal cases with positive, negative, and mixed returns
- Edge cases (empty, zero, single value)
- Known value validations
- Return type checks
"""

import pytest
import pandas as pd
import numpy as np
from src.metrics import calculate_cumulative_return, calculate_cagr, calculate_expected_returns


class TestCumulativeReturn:
    """Tests for calculate_cumulative_return()"""

    def test_positive_returns(self, positive_returns):
        """Test cumulative return with all positive returns"""
        result = calculate_cumulative_return(positive_returns)
        assert result > 0
        assert isinstance(result, (int, float))

    def test_negative_returns(self, negative_returns):
        """Test cumulative return with all negative returns"""
        result = calculate_cumulative_return(negative_returns)
        assert result < 0

    def test_zero_returns(self, zero_returns):
        """Test cumulative return with zero returns"""
        result = calculate_cumulative_return(zero_returns)
        assert result == 0.0

    def test_simple_calculation(self):
        """Test with known values: [0.1, -0.05] should give (1.1 * 0.95) - 1 = 0.045"""
        returns = pd.Series([0.1, -0.05])
        result = calculate_cumulative_return(returns)
        assert np.isclose(result, 0.045, rtol=1e-10)

    def test_empty_returns(self, empty_returns):
        """Test with empty series"""
        result = calculate_cumulative_return(empty_returns)
        # Should handle empty series gracefully
        assert result is None or result == 0.0 or np.isnan(result)

    def test_single_value(self, single_value_returns):
        """Test with single value"""
        result = calculate_cumulative_return(single_value_returns)
        assert np.isclose(result, 0.01, rtol=1e-10)

    def test_mixed_returns(self, simple_returns):
        """Test with mixed positive and negative returns"""
        result = calculate_cumulative_return(simple_returns)
        assert isinstance(result, (int, float))
        # Result should be positive for this particular series
        assert result > 0


class TestCAGR:
    """Tests for calculate_cagr()"""

    def test_one_year_positive(self):
        """Test CAGR for exactly 1 year of data"""
        dates = pd.date_range('2020-01-01', '2020-12-31', freq='D')
        returns = pd.Series([0.001] * len(dates), index=dates)
        result = calculate_cagr(returns)
        assert result > 0
        assert isinstance(result, (int, float))

    def test_multi_year(self):
        """Test CAGR for multi-year period"""
        dates = pd.date_range('2020-01-01', periods=504, freq='D')  # ~2 years
        returns = pd.Series([0.001] * 504, index=dates)
        result = calculate_cagr(returns)
        assert result > 0

    def test_negative_cagr(self, negative_returns):
        """Test CAGR with negative returns"""
        result = calculate_cagr(negative_returns)
        assert result < 0

    def test_known_value(self):
        """Test CAGR with known calculation"""
        # 100% return over 252 days should give CAGR = 1.0 (100%)
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        # Need returns that compound to 2x
        daily_return = (2.0 ** (1/252)) - 1
        returns = pd.Series([daily_return] * 252, index=dates)
        result = calculate_cagr(returns)
        assert np.isclose(result, 1.0, rtol=0.01)

    def test_zero_returns(self, zero_returns):
        """Test CAGR with zero returns"""
        result = calculate_cagr(zero_returns)
        assert np.isclose(result, 0.0, atol=1e-10)

    def test_simple_returns(self, simple_returns):
        """Test CAGR with mixed returns"""
        result = calculate_cagr(simple_returns)
        assert isinstance(result, (int, float))
        # Should be positive for this particular series
        assert result > 0


class TestExpectedReturns:
    """Tests for calculate_expected_returns()"""

    def test_return_tuple(self, simple_returns):
        """Test that function returns tuple of (daily, monthly, annual)"""
        result = calculate_expected_returns(simple_returns)
        assert isinstance(result, tuple)
        assert len(result) == 3
        daily, monthly, annual = result
        assert isinstance(daily, (int, float))
        assert isinstance(monthly, (int, float))
        assert isinstance(annual, (int, float))

    def test_scaling_relationship(self, simple_returns, trading_days):
        """Test that annual ≈ daily * 252 and monthly ≈ daily * 21"""
        daily, monthly, annual = calculate_expected_returns(simple_returns)
        assert np.isclose(annual, daily * trading_days, rtol=0.01)
        assert np.isclose(monthly, daily * 21, rtol=0.01)

    def test_positive_mean(self, positive_returns):
        """Test with positive returns"""
        daily, monthly, annual = calculate_expected_returns(positive_returns)
        assert daily > 0
        assert monthly > 0
        assert annual > 0

    def test_negative_mean(self, negative_returns):
        """Test with negative returns"""
        daily, monthly, annual = calculate_expected_returns(negative_returns)
        assert daily < 0
        assert monthly < 0
        assert annual < 0

    def test_zero_mean(self, zero_returns):
        """Test with zero returns"""
        daily, monthly, annual = calculate_expected_returns(zero_returns)
        assert daily == 0.0
        assert monthly == 0.0
        assert annual == 0.0

    def test_known_values(self):
        """Test with known average return"""
        # 1% average daily return
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        returns = pd.Series([0.01] * 100, index=dates)
        daily, monthly, annual = calculate_expected_returns(returns)

        assert np.isclose(daily, 0.01, rtol=1e-10)
        assert np.isclose(monthly, 0.21, rtol=0.01)  # 0.01 * 21
        assert np.isclose(annual, 2.52, rtol=0.01)   # 0.01 * 252
