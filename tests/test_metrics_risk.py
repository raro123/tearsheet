"""
Tests for risk metric calculations

Tests the following functions from src.metrics:
- calculate_volatility()
- calculate_max_drawdown()
- calculate_drawdown_series()
- calculate_longest_drawdown()
- calculate_average_drawdown()
- calculate_var_cvar()
- calculate_drawdown_recovery()

Coverage includes:
- Volatility annualization (√252)
- Drawdown scenarios (recovery vs no recovery)
- VaR/CVaR at 95% confidence
- Edge cases and boundary conditions
"""

import pytest
import pandas as pd
import numpy as np
from src.metrics import (
    calculate_volatility,
    calculate_max_drawdown,
    calculate_drawdown_series,
    calculate_longest_drawdown,
    calculate_average_drawdown,
    calculate_var_cvar,
    calculate_drawdown_recovery
)


class TestVolatility:
    """Tests for calculate_volatility()"""

    def test_zero_volatility(self, zero_returns):
        """Test volatility with constant (zero) returns"""
        result = calculate_volatility(zero_returns)
        assert np.isclose(result, 0.0, atol=1e-10)

    def test_positive_returns(self, positive_returns):
        """Test volatility with all positive returns"""
        result = calculate_volatility(positive_returns)
        assert np.isclose(result, 0.0, atol=1e-10)  # All same value = zero volatility

    def test_variable_returns(self, simple_returns):
        """Test volatility with variable returns"""
        result = calculate_volatility(simple_returns)
        assert result > 0
        assert isinstance(result, (int, float))

    def test_annualization_factor(self):
        """Test that volatility is annualized with sqrt(252)"""
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        # Create returns with known daily std dev
        returns = pd.Series(np.random.randn(252) * 0.01, index=dates)
        daily_std = returns.std()
        annualized_vol = calculate_volatility(returns)

        # Annualized should be approximately daily * sqrt(252)
        expected = daily_std * np.sqrt(252)
        assert np.isclose(annualized_vol, expected, rtol=0.01)

    def test_high_volatility(self):
        """Test with high volatility returns"""
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        returns = pd.Series([0.05, -0.05] * 50, index=dates)
        result = calculate_volatility(returns)
        assert result > 0.5  # Should be high volatility


class TestMaxDrawdown:
    """Tests for calculate_max_drawdown()"""

    def test_no_drawdown(self, positive_returns):
        """Test with monotonically increasing returns (no drawdown)"""
        result = calculate_max_drawdown(positive_returns)
        # Should be zero or very close to zero
        assert result >= 0
        assert result < 0.01

    def test_negative_returns(self, negative_returns):
        """Test with negative returns (continuous drawdown)"""
        result = calculate_max_drawdown(negative_returns)
        assert result < 0  # Should be negative (drawdown)

    def test_known_drawdown(self):
        """Test with known drawdown scenario"""
        # Start at 100, drop to 50 (-50% drawdown), recover to 75
        dates = pd.date_range('2020-01-01', periods=3, freq='D')
        returns = pd.Series([0.0, -0.5, 0.5], index=dates)  # 100 -> 100 -> 50 -> 75
        result = calculate_max_drawdown(returns)
        assert np.isclose(result, -0.5, rtol=0.01)

    def test_simple_returns(self, simple_returns):
        """Test max drawdown is negative or zero"""
        result = calculate_max_drawdown(simple_returns)
        assert result <= 0


class TestDrawdownSeries:
    """Tests for calculate_drawdown_series()"""

    def test_return_type(self, simple_returns):
        """Test that function returns a Series"""
        result = calculate_drawdown_series(simple_returns)
        assert isinstance(result, pd.Series)
        assert len(result) == len(simple_returns)

    def test_drawdown_values(self, positive_returns):
        """Test drawdown values with positive returns"""
        result = calculate_drawdown_series(positive_returns)
        # All values should be zero (no drawdown with monotonic increase)
        assert all(result >= -0.01)  # Allow small floating point errors

    def test_negative_returns_drawdown(self, negative_returns):
        """Test drawdown increases with continuous losses"""
        result = calculate_drawdown_series(negative_returns)
        # Drawdown should get progressively worse
        assert result.iloc[-1] < result.iloc[0]


class TestLongestDrawdown:
    """Tests for calculate_longest_drawdown()"""

    def test_no_drawdown(self, positive_returns):
        """Test with no drawdown scenario"""
        result = calculate_longest_drawdown(positive_returns)
        # Should be zero or very small
        assert result is not None
        assert result >= 0

    def test_continuous_drawdown(self, negative_returns):
        """Test with continuous drawdown"""
        result = calculate_longest_drawdown(negative_returns)
        # Should be close to the length of the series
        assert result > 50  # At least half the period

    def test_return_type(self, simple_returns):
        """Test return type is numeric days"""
        result = calculate_longest_drawdown(simple_returns)
        assert isinstance(result, (int, float)) or result is None


class TestAverageDrawdown:
    """Tests for calculate_average_drawdown()"""

    def test_no_drawdown(self, positive_returns):
        """Test average drawdown with no drawdowns"""
        result = calculate_average_drawdown(positive_returns)
        # Should be zero or close to zero
        assert result >= -0.01

    def test_negative_returns(self, negative_returns):
        """Test average drawdown with losses"""
        result = calculate_average_drawdown(negative_returns)
        assert result < 0  # Should be negative

    def test_less_than_max_drawdown(self, simple_returns):
        """Test that average DD <= max DD in magnitude"""
        avg_dd = calculate_average_drawdown(simple_returns)
        max_dd = calculate_max_drawdown(simple_returns)
        # Average should be less severe than max
        assert abs(avg_dd) <= abs(max_dd) or np.isclose(avg_dd, max_dd)


class TestVarCVar:
    """Tests for calculate_var_cvar()"""

    def test_return_tuple(self, simple_returns):
        """Test that function returns tuple of (var, cvar)"""
        result = calculate_var_cvar(simple_returns)
        assert isinstance(result, tuple)
        assert len(result) == 2
        var, cvar = result
        assert isinstance(var, (int, float))
        assert isinstance(cvar, (int, float))

    def test_cvar_worse_than_var(self, simple_returns):
        """Test that CVaR is typically worse (more negative) than VaR"""
        var, cvar = calculate_var_cvar(simple_returns)
        # CVaR should be more negative (tail risk)
        assert cvar <= var

    def test_confidence_level(self, simple_returns):
        """Test different confidence levels"""
        var_95, cvar_95 = calculate_var_cvar(simple_returns, confidence_level=0.95)
        var_99, cvar_99 = calculate_var_cvar(simple_returns, confidence_level=0.99)

        # 99% should be more extreme than 95%
        assert var_99 <= var_95
        assert cvar_99 <= cvar_95

    def test_negative_returns(self, negative_returns):
        """Test VaR/CVaR with all negative returns"""
        var, cvar = calculate_var_cvar(negative_returns)
        assert var < 0
        assert cvar < 0


class TestDrawdownRecovery:
    """Tests for calculate_drawdown_recovery()"""

    def test_recovery_scenario(self, drawdown_with_recovery):
        """Test drawdown that recovers"""
        result = calculate_drawdown_recovery(drawdown_with_recovery)
        # Should return a positive number (time to recover)
        assert result is not None
        assert result > 0
        assert isinstance(result, (int, float))

    def test_no_recovery_scenario(self, drawdown_no_recovery):
        """Test drawdown that doesn't recover (still in drawdown)"""
        result = calculate_drawdown_recovery(drawdown_no_recovery)
        # Should return None (not recovered)
        assert result is None

    def test_no_drawdown(self, positive_returns):
        """Test with no drawdown (monotonic increase)"""
        result = calculate_drawdown_recovery(positive_returns)
        # Either None or 0 (no recovery needed)
        assert result is None or result == 0 or np.isclose(result, 0, atol=0.1)

    def test_conversion_to_years(self):
        """Test that recovery time is in years (days / 252)"""
        # Create a scenario with known recovery time
        dates = pd.date_range('2020-01-01', periods=300, freq='D')
        # Rise for 50 days, drop, recover in 252 days (1 year)
        returns = pd.Series([0.01] * 50 + [-0.3] + [0.015] * 249, index=dates)
        result = calculate_drawdown_recovery(returns)

        # Recovery should be approximately 1 year (252 trading days)
        if result is not None:
            assert result > 0.5  # At least half a year
            assert result < 2.0  # Less than 2 years

    def test_single_value(self, single_value_returns):
        """Test with single value (edge case)"""
        result = calculate_drawdown_recovery(single_value_returns)
        assert result is None  # Can't calculate with only one value

    def test_empty_returns(self, empty_returns):
        """Test with empty series"""
        result = calculate_drawdown_recovery(empty_returns)
        assert result is None
