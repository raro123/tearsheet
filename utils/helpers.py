import pandas as pd

def format_metric_value(metric_name, value):
    """Format metric value for display"""
    percentage_metrics = [
        'Cumulative Return', 'CAGR', 'Max Drawdown',
        'Volatility (ann.)', 'Win Rate'
    ]

    if metric_name in percentage_metrics:
        return f"{value*100:.2f}%"
    elif metric_name in ['Longest DD Days', 'Max Consecutive Wins', 'Max Consecutive Losses']:
        return f"{int(value)}"
    else:
        return f"{value:.2f}"

def create_metrics_comparison_df(strategy_metrics, benchmark_metrics):
    """Create formatted dataframe for metrics comparison"""
    metrics_data = []

    for metric_name in strategy_metrics.keys():
        metrics_data.append({
            'Metric': metric_name,
            'Strategy': format_metric_value(metric_name, strategy_metrics[metric_name]),
            'Benchmark': format_metric_value(metric_name, benchmark_metrics.get(metric_name, 0))
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