import numpy as np
import pandas as pd
from scipy import stats

TRADING_DAYS = 252

def calculate_cumulative_return(returns):
    """Calculate total cumulative return"""
    return (1 + returns).prod() - 1

def calculate_cagr(returns):
    """Calculate Compound Annual Growth Rate"""
    total_return = calculate_cumulative_return(returns)
    n_years = len(returns) / TRADING_DAYS
    if n_years > 0:
        return (1 + total_return) ** (1 / n_years) - 1
    return 0

def calculate_volatility(returns):
    """Calculate annualized volatility"""
    return returns.std() * np.sqrt(TRADING_DAYS)

def calculate_sharpe_ratio(returns, risk_free_rate):
    """Calculate Sharpe Ratio"""
    excess_returns = returns.mean() * TRADING_DAYS - risk_free_rate
    volatility = calculate_volatility(returns)
    return excess_returns / volatility if volatility != 0 else 0

def calculate_sortino_ratio(returns, risk_free_rate):
    """Calculate Sortino Ratio"""
    excess_returns = returns.mean() * TRADING_DAYS - risk_free_rate
    downside_returns = returns[returns < 0]
    downside_vol = downside_returns.std() * np.sqrt(TRADING_DAYS) if len(downside_returns) > 0 else 0
    return excess_returns / downside_vol if downside_vol != 0 else 0

def calculate_max_drawdown(returns):
    """Calculate maximum drawdown"""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max
    return drawdown.min()

def calculate_calmar_ratio(returns, risk_free_rate):
    """Calculate Calmar Ratio"""
    cagr = calculate_cagr(returns)
    max_dd = calculate_max_drawdown(returns)
    return cagr / abs(max_dd) if max_dd != 0 else 0

def calculate_omega_ratio(returns, risk_free_rate):
    """Calculate Omega Ratio"""
    daily_rf = (1 + risk_free_rate) ** (1/TRADING_DAYS) - 1
    gains = returns[returns > daily_rf].sum()
    losses = abs(returns[returns < daily_rf].sum())
    return gains / losses if losses != 0 else 0

def calculate_drawdown_series(returns):
    """Calculate drawdown time series"""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    return (cumulative - running_max) / running_max

def calculate_longest_drawdown(returns):
    """Calculate longest drawdown period in days"""
    drawdown = calculate_drawdown_series(returns)
    is_dd = drawdown < 0
    dd_periods = is_dd.astype(int).groupby((is_dd != is_dd.shift()).cumsum()).sum()
    return dd_periods.max() if len(dd_periods) > 0 else 0

def calculate_win_rate(returns):
    """Calculate percentage of winning days"""
    winning_days = (returns > 0).sum()
    return winning_days / len(returns) if len(returns) > 0 else 0

def calculate_consecutive_streaks(returns):
    """Calculate max consecutive wins and losses"""
    signs = np.sign(returns)
    sign_changes = signs != signs.shift()
    streak_groups = sign_changes.cumsum()

    # Group by streak and get the sign for each streak group
    streak_info = pd.DataFrame({'sign': signs, 'group': streak_groups})
    streak_counts = streak_info.groupby('group').agg({'sign': ['first', 'count']})

    # Extract first sign and count for each streak
    streak_signs = streak_counts[('sign', 'first')]
    streak_lengths = streak_counts[('sign', 'count')]

    max_wins = streak_lengths[streak_signs > 0].max() if (streak_signs > 0).any() else 0
    max_losses = streak_lengths[streak_signs < 0].max() if (streak_signs < 0).any() else 0

    return max_wins, max_losses

def calculate_gain_pain_ratio(returns):
    """Calculate Gain/Pain Ratio"""
    total_gains = returns[returns > 0].sum()
    total_losses = abs(returns[returns < 0].sum())
    return total_gains / total_losses if total_losses != 0 else 0

def calculate_beta_correlation(returns, benchmark_returns):
    """Calculate Beta and Correlation with benchmark"""
    aligned_returns, aligned_bench = returns.align(benchmark_returns, join='inner')

    if len(aligned_returns) == 0:
        return None, None, None

    covariance = aligned_returns.cov(aligned_bench)
    benchmark_variance = aligned_bench.var()
    beta = covariance / benchmark_variance if benchmark_variance != 0 else 0
    correlation = aligned_returns.corr(aligned_bench)
    r_squared = correlation ** 2

    return beta, correlation, r_squared

def calculate_all_metrics(returns, benchmark_returns=None, risk_free_rate=0.0249):
    """Calculate all performance metrics"""
    max_wins, max_losses = calculate_consecutive_streaks(returns)

    metrics = {
        'Cumulative Return': calculate_cumulative_return(returns),
        'CAGR': calculate_cagr(returns),
        'Sharpe Ratio': calculate_sharpe_ratio(returns, risk_free_rate),
        'Sortino Ratio': calculate_sortino_ratio(returns, risk_free_rate),
        'Max Drawdown': calculate_max_drawdown(returns),
        'Longest DD Days': calculate_longest_drawdown(returns),
        'Volatility (ann.)': calculate_volatility(returns),
        'Calmar Ratio': calculate_calmar_ratio(returns, risk_free_rate),
        'Skew': stats.skew(returns.dropna()),
        'Kurtosis': stats.kurtosis(returns.dropna()),
        'Omega Ratio': calculate_omega_ratio(returns, risk_free_rate),
        'Win Rate': calculate_win_rate(returns),
        'Max Consecutive Wins': max_wins,
        'Max Consecutive Losses': max_losses,
        'Gain/Pain Ratio': calculate_gain_pain_ratio(returns),
        'Time in Market': 1.0,
    }

    # Add benchmark-relative metrics
    if benchmark_returns is not None:
        beta, correlation, r_squared = calculate_beta_correlation(returns, benchmark_returns)
        if beta is not None:
            metrics['Beta'] = beta
            metrics['Correlation'] = correlation
            metrics['R²'] = r_squared

    return metrics