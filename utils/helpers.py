import pandas as pd

def format_metric_value(metric_name, value):
    """Format metric value for display"""
    percentage_metrics = [
        'Cumulative Return', 'CAGR', 'Max Drawdown', 'Avg Drawdown',
        'Volatility (ann.)', 'Win Rate', 'Expected Annual Return',
        'Expected Monthly Return', 'Expected Daily Return',
        'VaR (95%)', 'CVaR (95%)'
    ]

    if metric_name in percentage_metrics:
        return f"{value*100:.2f}%"
    elif metric_name in ['Longest DD Days', 'Max Consecutive Wins', 'Max Consecutive Losses']:
        return f"{int(value)}"
    else:
        return f"{value:.2f}"

def create_metrics_comparison_df(strategy_metrics, benchmark_metrics, strategy_name=None, benchmark_name=None,
                                  strategy_data_period=None, benchmark_data_period=None, comparison_period=None):
    """Create formatted dataframe for metrics comparison with sections"""

    # Define metric categories
    return_metrics_order = [
        'Cumulative Return', 'CAGR', 'Expected Annual Return',
        'Expected Monthly Return', 'Expected Daily Return',
        'Win Rate', 'Max Consecutive Wins'
    ]

    risk_metrics_order = [
        'Volatility (ann.)', 'Max Drawdown', 'Avg Drawdown',
        'Longest DD Days', 'Skewness', 'VaR (95%)', 'CVaR (95%)'
    ]

    ratio_metrics_order = [
        'Sharpe Ratio', 'Sortino Ratio', 'Calmar Ratio',
        'Omega Ratio', 'Lower Tail Ratio', 'Upper Tail Ratio'
    ]

    metrics_data = []

    # Add metadata rows at the top
    if strategy_name and benchmark_name:
        metrics_data.append({'Metric': 'Name', 'Strategy': strategy_name, 'Benchmark': benchmark_name})

    if strategy_data_period and benchmark_data_period:
        metrics_data.append({'Metric': 'Data Period', 'Strategy': strategy_data_period, 'Benchmark': benchmark_data_period})

    if comparison_period:
        metrics_data.append({'Metric': 'Comparison Period', 'Strategy': comparison_period, 'Benchmark': comparison_period})

    if any([strategy_name, strategy_data_period, comparison_period]):
        metrics_data.append({'Metric': '', 'Strategy': '', 'Benchmark': ''})  # Blank row separator

    # Add Return Metrics section
    metrics_data.append({'Metric': '── RETURN METRICS ──', 'Strategy': '', 'Benchmark': ''})
    for metric_name in return_metrics_order:
        if metric_name in strategy_metrics:
            metrics_data.append({
                'Metric': metric_name,
                'Strategy': format_metric_value(metric_name, strategy_metrics[metric_name]),
                'Benchmark': format_metric_value(metric_name, benchmark_metrics.get(metric_name, 0))
            })

    # Add Risk Metrics section
    metrics_data.append({'Metric': '── RISK METRICS ──', 'Strategy': '', 'Benchmark': ''})
    for metric_name in risk_metrics_order:
        if metric_name in strategy_metrics:
            metrics_data.append({
                'Metric': metric_name,
                'Strategy': format_metric_value(metric_name, strategy_metrics[metric_name]),
                'Benchmark': format_metric_value(metric_name, benchmark_metrics.get(metric_name, 0))
            })

    # Add Ratio Metrics section
    metrics_data.append({'Metric': '── RATIO METRICS ──', 'Strategy': '', 'Benchmark': ''})
    for metric_name in ratio_metrics_order:
        if metric_name in strategy_metrics:
            metrics_data.append({
                'Metric': metric_name,
                'Strategy': format_metric_value(metric_name, strategy_metrics[metric_name]),
                'Benchmark': format_metric_value(metric_name, benchmark_metrics.get(metric_name, 0))
            })

    # Add benchmark-relative metrics (Beta, Correlation, R²)
    benchmark_relative_metrics = ['Beta', 'Correlation', 'R²']
    has_benchmark_metrics = any(m in strategy_metrics for m in benchmark_relative_metrics)

    if has_benchmark_metrics:
        metrics_data.append({'Metric': '── BENCHMARK RELATIVE ──', 'Strategy': '', 'Benchmark': ''})
        for metric_name in benchmark_relative_metrics:
            if metric_name in strategy_metrics:
                metrics_data.append({
                    'Metric': metric_name,
                    'Strategy': format_metric_value(metric_name, strategy_metrics[metric_name]),
                    'Benchmark': ''  # Leave blank for benchmark column
                })

    return pd.DataFrame(metrics_data)

def get_period_description(start_date, end_date):
    """Generate human-readable period description"""
    days = (end_date - start_date).days
    years = days / 365.25

    if years < 1:
        return f"{days} days"
    elif years < 2:
        return f"{years:.1f} year"
    else:
        return f"{years:.1f} years"