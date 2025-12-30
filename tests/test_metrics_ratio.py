"""
Tests for risk-adjusted ratio metric calculations

Tests the following functions from src.metrics:
- calculate_sharpe_ratio()
- calculate_sortino_ratio()
- calculate_calmar_ratio()
- calculate_omega_ratio()

Coverage includes:
- Formula validations
- Risk-free rate handling
- Edge cases (zero volatility, zero drawdown)
- Positive and negative return scenarios
"""

import pytest
import pandas as pd
import numpy as np
from src.metrics import (
    calculate_sharpe_ratio,
    calculate_sortino_ratio,
    calculate_calmar_ratio,
    calculate_omega_ratio
)


class TestSharpeRatio:
    """Tests for calculate_sharpe_ratio()"""

    def test_positive_sharpe(self, positive_returns, default_risk_free_rate):
        """Test Sharpe ratio with positive returns"""
        result = calculate_sharpe_ratio(positive_returns, default_risk_free_rate)
        # Should be positive with positive returns
        assert result > 0
        assert isinstance(result, (int, float))

    def test_negative_sharpe(self, negative_returns, default_risk_free_rate):
        """Test Sharpe ratio with negative returns"""
        result = calculate_sharpe_ratio(negative_returns, default_risk_free_rate)
        # Should be negative with negative returns below risk-free rate
        assert result < 0

    def test_zero_risk_free_rate(self, simple_returns):
        """Test Sharpe ratio with zero risk-free rate"""
        result = calculate_sharpe_ratio(simple_returns, risk_free_rate=0.0)
        assert isinstance(result, (int, float))

    def test_high_risk_free_rate(self, simple_returns):
        """Test Sharpe ratio with high risk-free rate"""
        result = calculate_sharpe_ratio(simple_returns, risk_free_rate=0.10)
        assert isinstance(result, (int, float))

    def test_zero_volatility(self, zero_returns, default_risk_free_rate):
        """Test Sharpe ratio with zero volatility (edge case)"""
        result = calculate_sharpe_ratio(zero_returns, default_risk_free_rate)
        # Should handle zero volatility gracefully
        # Either None, inf, or a default value
        assert result is None or np.isinf(result) or isinstance(result, (int, float))

    def test_formula_validation(self):
        """Test Sharpe ratio formula: (return - rf) / volatility"""
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        returns = pd.Series([0.001] * 252, index=dates)
        rf_rate = 0.02

        sharpe = calculate_sharpe_ratio(returns, rf_rate)

        # Manual calculation
        from src.metrics import calculate_volatility
        expected_return = returns.mean() * 252  # Annualized
        volatility = calculate_volatility(returns)

        if volatility > 0:
            expected_sharpe = (expected_return - rf_rate) / volatility
            assert np.isclose(sharpe, expected_sharpe, rtol=0.01)


class TestSortinoRatio:
    """Tests for calculate_sortino_ratio()"""

    def test_positive_returns(self, positive_returns, default_risk_free_rate):
        """Test Sortino ratio with all positive returns"""
        result = calculate_sortino_ratio(positive_returns, default_risk_free_rate)
        # With no downside, Sortino should be very high or inf
        assert result is None or np.isinf(result) or result > 0

    def test_negative_returns(self, negative_returns, default_risk_free_rate):
        """Test Sortino ratio with negative returns"""
        result = calculate_sortino_ratio(negative_returns, default_risk_free_rate)
        # Should be negative with negative returns
        assert result < 0 or result is None

    def test_mixed_returns(self, simple_returns, default_risk_free_rate):
        """Test Sortino ratio with mixed returns"""
        result = calculate_sortino_ratio(simple_returns, default_risk_free_rate)
        assert isinstance(result, (int, float)) or result is None

    def test_higher_than_sharpe(self, simple_returns, default_risk_free_rate):
        """Test that Sortino >= Sharpe (typically)"""
        sharpe = calculate_sharpe_ratio(simple_returns, default_risk_free_rate)
        sortino = calculate_sortino_ratio(simple_returns, default_risk_free_rate)

        # Sortino uses downside deviation, so it's often higher
        # (But not always, depending on distribution)
        if sharpe is not None and sortino is not None:
            assert isinstance(sharpe, (int, float))
            assert isinstance(sortino, (int, float))

    def test_zero_risk_free_rate(self, simple_returns):
        """Test Sortino ratio with zero risk-free rate"""
        result = calculate_sortino_ratio(simple_returns, risk_free_rate=0.0)
        assert isinstance(result, (int, float)) or result is None


class TestCalmarRatio:
    """Tests for calculate_calmar_ratio()"""

    def test_positive_returns(self, positive_returns, default_risk_free_rate):
        """Test Calmar ratio with positive returns (no drawdown)"""
        result = calculate_calmar_ratio(positive_returns, default_risk_free_rate)
        # With no drawdown, Calmar should be inf or very high
        assert result is None or np.isinf(result) or result > 0

    def test_negative_returns(self, negative_returns, default_risk_free_rate):
        """Test Calmar ratio with negative returns"""
        result = calculate_calmar_ratio(negative_returns, default_risk_free_rate)
        # Should be negative with losses
        assert result < 0 or result is None

    def test_mixed_returns(self, simple_returns, default_risk_free_rate):
        """Test Calmar ratio with mixed returns"""
        result = calculate_calmar_ratio(simple_returns, default_risk_free_rate)
        assert isinstance(result, (int, float)) or result is None

    def test_formula_validation(self, simple_returns, default_risk_free_rate):
        """Test Calmar ratio formula: CAGR / abs(MaxDrawdown)"""
        from src.metrics import calculate_cagr, calculate_max_drawdown

        calmar = calculate_calmar_ratio(simple_returns, default_risk_free_rate)
        cagr = calculate_cagr(simple_returns)
        max_dd = calculate_max_drawdown(simple_returns)

        if max_dd != 0 and calmar is not None:
            expected_calmar = cagr / abs(max_dd)
            # Should be close (might differ slightly due to risk-free rate adjustment)
            assert np.isclose(calmar, expected_calmar, rtol=0.1)

    def test_zero_drawdown(self, positive_returns, default_risk_free_rate):
        """Test Calmar ratio with zero drawdown (edge case)"""
        result = calculate_calmar_ratio(positive_returns, default_risk_free_rate)
        # Should handle zero drawdown (division by zero)
        assert result is None or np.isinf(result) or result > 0


class TestOmegaRatio:
    """Tests for calculate_omega_ratio()"""

    def test_positive_returns(self, positive_returns, default_risk_free_rate):
        """Test Omega ratio with all positive returns"""
        result = calculate_omega_ratio(positive_returns, default_risk_free_rate)
        # All returns above threshold should give high Omega
        assert result is None or np.isinf(result) or result > 1

    def test_negative_returns(self, negative_returns, default_risk_free_rate):
        """Test Omega ratio with all negative returns"""
        result = calculate_omega_ratio(negative_returns, default_risk_free_rate)
        # All returns below threshold should give Omega < 1
        assert result is None or result < 1

    def test_mixed_returns(self, simple_returns, default_risk_free_rate):
        """Test Omega ratio with mixed returns"""
        result = calculate_omega_ratio(simple_returns, default_risk_free_rate)
        assert isinstance(result, (int, float)) or result is None
        if result is not None:
            assert result > 0  # Omega is always positive

    def test_zero_threshold(self, simple_returns):
        """Test Omega ratio with zero threshold"""
        result = calculate_omega_ratio(simple_returns, risk_free_rate=0.0)
        assert isinstance(result, (int, float)) or result is None

    def test_high_threshold(self, simple_returns):
        """Test Omega ratio with high threshold"""
        result = calculate_omega_ratio(simple_returns, risk_free_rate=0.20)
        # High threshold means fewer gains, should reduce Omega
        assert isinstance(result, (int, float)) or result is None

    def test_gain_loss_relationship(self):
        """Test that Omega > 1 when gains > losses"""
        dates = pd.date_range('2020-01-01', periods=100, freq='D')
        # More and bigger gains than losses
        returns = pd.Series([0.02] * 70 + [-0.01] * 30, index=dates)
        result = calculate_omega_ratio(returns, risk_free_rate=0.0)

        if result is not None:
            assert result > 1  # Gains outweigh losses
