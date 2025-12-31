"""Tests for performance metrics updates (Dec 2024)

Tests cover:
- Monthly/Annual VaR/CVaR scaling
- Expected Monthly Return
- Benchmark defaults application
- Capture ratio formatting changes
- N/A replacement with "-"
- 1 decimal rounding for specific metrics
"""

import pytest
import pandas as pd
import numpy as np
from src.metrics import calculate_var_cvar, calculate_all_metrics
from utils.helpers import format_metric_value
from app_pages.fund_deepdive import apply_benchmark_defaults


class TestVarCVarScaling:
    """Test VaR/CVaR monthly and annual scaling"""

    @pytest.fixture
    def simple_returns(self):
        """Create simple returns series for testing"""
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        returns = pd.Series(np.random.normal(0.001, 0.02, 252), index=dates)
        return returns

    def test_monthly_scaling(self, simple_returns):
        """Test that monthly VaR/CVaR are scaled by √21"""
        var_daily, cvar_daily, var_monthly, cvar_monthly = calculate_var_cvar(simple_returns)

        sqrt_21 = np.sqrt(21)
        expected_var_monthly = var_daily * sqrt_21
        expected_cvar_monthly = cvar_daily * sqrt_21

        assert np.isclose(var_monthly, expected_var_monthly, rtol=1e-10)
        assert np.isclose(cvar_monthly, expected_cvar_monthly, rtol=1e-10)

    def test_annual_scaling_in_all_metrics(self, simple_returns):
        """Test that annual VaR/CVaR are scaled by √252 in calculate_all_metrics"""
        metrics = calculate_all_metrics(simple_returns)

        var_daily, cvar_daily, var_monthly, cvar_monthly = calculate_var_cvar(simple_returns)

        sqrt_252 = np.sqrt(252)
        expected_var_annual = var_daily * sqrt_252
        expected_cvar_annual = cvar_daily * sqrt_252

        assert np.isclose(metrics['VaR Annual (95%)'], expected_var_annual, rtol=1e-10)
        assert np.isclose(metrics['CVaR Annual (95%)'], expected_cvar_annual, rtol=1e-10)

    def test_monthly_values_in_all_metrics(self, simple_returns):
        """Test that monthly VaR/CVaR appear in calculate_all_metrics"""
        metrics = calculate_all_metrics(simple_returns)

        var_daily, cvar_daily, var_monthly, cvar_monthly = calculate_var_cvar(simple_returns)

        assert np.isclose(metrics['VaR Monthly (95%)'], var_monthly, rtol=1e-10)
        assert np.isclose(metrics['CVaR Monthly (95%)'], cvar_monthly, rtol=1e-10)


class TestExpectedMonthlyReturn:
    """Test Expected Monthly Return metric"""

    @pytest.fixture
    def simple_returns(self):
        """Create simple returns series"""
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        returns = pd.Series(np.random.normal(0.001, 0.02, 252), index=dates)
        return returns

    def test_expected_monthly_return_exists(self, simple_returns):
        """Test that Expected Monthly Return is in metrics dict"""
        metrics = calculate_all_metrics(simple_returns)
        assert 'Expected Monthly Return' in metrics

    def test_expected_monthly_return_calculation(self, simple_returns):
        """Test Expected Monthly Return is calculated correctly"""
        metrics = calculate_all_metrics(simple_returns)

        expected_daily = simple_returns.mean()
        expected_monthly = expected_daily * 21

        assert np.isclose(metrics['Expected Monthly Return'], expected_monthly, rtol=1e-10)


class TestBenchmarkDefaults:
    """Test benchmark-specific default values"""

    def test_benchmark_defaults_applied(self):
        """Test that benchmark defaults are correctly applied"""
        # Create sample metrics dict
        metrics = {
            'Beta': 0.95,
            'Active Return': 0.02,
            'Active Risk': 0.01,
            'Information Ratio': 1.5,
            'Upcapture Ratio': 0.97,
            'Downcapture Ratio': 0.93,
            'Sharpe Ratio': 1.2
        }

        # Apply benchmark defaults
        result = apply_benchmark_defaults(metrics.copy(), is_benchmark=True)

        assert result['Beta'] == 1.0
        assert result['Active Return'] == 0.0
        assert result['Active Risk'] == 0.0
        assert result['Information Ratio'] == 0.0
        assert result['Upcapture Ratio'] == 1.0
        assert result['Downcapture Ratio'] == 1.0
        # Sharpe should remain unchanged
        assert result['Sharpe Ratio'] == 1.2

    def test_non_benchmark_unchanged(self):
        """Test that non-benchmark metrics are not modified"""
        metrics = {
            'Beta': 0.95,
            'Active Return': 0.02,
            'Upcapture Ratio': 0.97
        }

        result = apply_benchmark_defaults(metrics.copy(), is_benchmark=False)

        assert result['Beta'] == 0.95
        assert result['Active Return'] == 0.02
        assert result['Upcapture Ratio'] == 0.97


class TestMetricFormatting:
    """Test metric value formatting changes"""

    def test_na_replacement(self):
        """Test that None values are formatted as '-' instead of 'N/A'"""
        result = format_metric_value('CAGR', None)
        assert result == '-'

        result = format_metric_value('Beta', None)
        assert result == '-'

    def test_drawdown_recovery_special_case(self):
        """Test that Drawdown Recovery Years still shows 'In Drawdown'"""
        result = format_metric_value('Drawdown Recovery Years', None)
        assert result == 'In Drawdown'

    def test_capture_ratio_percentage_format(self):
        """Test that capture ratios are formatted as percentage, not 'x'"""
        # 0.97 should become "97%" not "0.97x"
        result = format_metric_value('Upcapture Ratio', 0.97)
        assert result == '97%'

        result = format_metric_value('Downcapture Ratio', 1.03)
        assert result == '103%'

        # Benchmark capture ratios (1.0 -> 100%)
        result = format_metric_value('Upcapture Ratio', 1.0)
        assert result == '100%'

    def test_one_decimal_rounding(self):
        """Test that specific metrics use 1 decimal place"""
        one_decimal_metrics = [
            'Cumulative Return',
            'CAGR',
            'Expected Annual Return',
            'Expected Monthly Return',
            'Monthly Consistency',
            'Annual Consistency'
        ]

        for metric in one_decimal_metrics:
            result = format_metric_value(metric, 0.12345)
            assert result == '12.3%', f"{metric} should use 1 decimal"

    def test_two_decimal_default(self):
        """Test that other percentage metrics use 2 decimals"""
        two_decimal_metrics = [
            'Volatility (ann.)',
            'Max Drawdown',
            'VaR Annual (95%)',
            'CVaR Monthly (95%)',
            'Active Risk'
        ]

        for metric in two_decimal_metrics:
            result = format_metric_value(metric, 0.12345)
            assert result == '12.35%', f"{metric} should use 2 decimals"

    def test_irr_formatting(self):
        """Test that IRR is formatted as percentage with 2 decimals"""
        result = format_metric_value('IRR', 0.1234)
        assert result == '12.34%'


class TestMetricPresenceInAllMetrics:
    """Test that all new metrics appear in calculate_all_metrics"""

    @pytest.fixture
    def sample_returns(self):
        """Create sample returns with benchmark"""
        np.random.seed(42)
        dates = pd.date_range('2020-01-01', periods=252, freq='D')
        fund_returns = pd.Series(np.random.normal(0.001, 0.02, 252), index=dates)
        bench_returns = pd.Series(np.random.normal(0.0008, 0.015, 252), index=dates)
        return fund_returns, bench_returns

    def test_all_new_metrics_present(self, sample_returns):
        """Test that all new metrics are in the result dict"""
        fund_returns, bench_returns = sample_returns
        metrics = calculate_all_metrics(fund_returns, bench_returns)

        # New metrics that should be present
        expected_new_metrics = [
            'Expected Monthly Return',
            'VaR Annual (95%)',
            'CVaR Annual (95%)',
            'VaR Monthly (95%)',
            'CVaR Monthly (95%)'
        ]

        for metric in expected_new_metrics:
            assert metric in metrics, f"{metric} should be in metrics dict"
            assert metrics[metric] is not None, f"{metric} should have a value"

    def test_old_cvar_renamed(self, sample_returns):
        """Test that old 'CVaR (95%)' is now 'CVaR Annual (95%)'"""
        fund_returns, _ = sample_returns
        metrics = calculate_all_metrics(fund_returns)

        # Old name should not exist
        assert 'CVaR (95%)' not in metrics

        # New name should exist
        assert 'CVaR Annual (95%)' in metrics
