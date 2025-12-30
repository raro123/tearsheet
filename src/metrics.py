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

def calculate_expected_returns(returns):
    """Calculate expected daily, monthly, and annual returns"""
    expected_daily = returns.mean()
    expected_monthly = expected_daily * 21  # Approximate trading days per month
    expected_annual = expected_daily * TRADING_DAYS
    return expected_daily, expected_monthly, expected_annual

def calculate_average_drawdown(returns):
    """Calculate average drawdown"""
    drawdown_series = calculate_drawdown_series(returns)
    # Only consider drawdown periods (negative values)
    drawdowns = drawdown_series[drawdown_series < 0]
    return drawdowns.mean() if len(drawdowns) > 0 else 0

def calculate_var_cvar(returns, confidence_level=0.95):
    """Calculate Value at Risk (VaR) and Conditional Value at Risk (CVaR)"""
    var = np.percentile(returns.dropna(), (1 - confidence_level) * 100)
    # CVaR is the expected loss given that loss exceeds VaR
    cvar = returns[returns <= var].mean() if (returns <= var).any() else var
    return var, cvar

def calculate_tail_ratios(returns, percentile=95):
    """Calculate upper and lower tail ratios
    Upper tail: average of top percentile returns / overall average
    Lower tail: average of bottom percentile returns / overall average
    """
    upper_threshold = np.percentile(returns.dropna(), percentile)
    lower_threshold = np.percentile(returns.dropna(), 100 - percentile)

    upper_tail_returns = returns[returns >= upper_threshold]
    lower_tail_returns = returns[returns <= lower_threshold]

    mean_return = returns.mean()

    upper_tail_ratio = upper_tail_returns.mean() / abs(mean_return) if mean_return != 0 and len(upper_tail_returns) > 0 else 0
    lower_tail_ratio = abs(lower_tail_returns.mean()) / abs(mean_return) if mean_return != 0 and len(lower_tail_returns) > 0 else 0

    return upper_tail_ratio, lower_tail_ratio

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

def calculate_alpha(fund_cagr, benchmark_cagr, beta, risk_free_rate=0.0249):
    """Calculate Jensen's Alpha (annualized excess return above CAPM prediction)

    Alpha = Fund CAGR - [Risk-free rate + Beta × (Benchmark CAGR - Risk-free rate)]

    Args:
        fund_cagr: Fund's CAGR (annualized return)
        benchmark_cagr: Benchmark's CAGR (annualized return)
        beta: Fund's beta relative to benchmark
        risk_free_rate: Annual risk-free rate

    Returns:
        Annualized alpha
    """
    if fund_cagr is None or benchmark_cagr is None or beta is None:
        return None

    # Jensen's Alpha formula using CAPM
    expected_return = risk_free_rate + beta * (benchmark_cagr - risk_free_rate)
    alpha = fund_cagr - expected_return

    return alpha

def calculate_active_metrics(fund_returns, benchmark_returns):
    """Calculate active return, active risk (tracking error), and information ratio

    Args:
        fund_returns: Series of fund returns
        benchmark_returns: Series of benchmark returns

    Returns:
        tuple: (active_return, active_risk, information_ratio)
    """
    if fund_returns is None or benchmark_returns is None:
        return None, None, None

    # Active returns (fund - benchmark)
    active_returns = fund_returns - benchmark_returns

    # Active return (annualized)
    active_return = active_returns.mean() * TRADING_DAYS

    # Active risk / Tracking error (annualized std of active returns)
    active_risk = active_returns.std() * np.sqrt(TRADING_DAYS)

    # Information ratio (active return / active risk)
    information_ratio = active_return / active_risk if active_risk > 0 else None

    return active_return, active_risk, information_ratio

def calculate_consistency_metrics(fund_returns, benchmark_returns):
    """Calculate monthly and annual consistency (outperformance frequency)

    Args:
        fund_returns: Series of fund returns (daily)
        benchmark_returns: Series of benchmark returns (daily)

    Returns:
        tuple: (monthly_consistency, annual_consistency)
    """
    if fund_returns is None or benchmark_returns is None:
        return None, None

    # Monthly consistency
    fund_monthly = fund_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
    bench_monthly = benchmark_returns.resample('M').apply(lambda x: (1 + x).prod() - 1)
    monthly_consistency = (fund_monthly > bench_monthly).sum() / len(fund_monthly)

    # Annual consistency
    fund_annual = fund_returns.resample('Y').apply(lambda x: (1 + x).prod() - 1)
    bench_annual = benchmark_returns.resample('Y').apply(lambda x: (1 + x).prod() - 1)
    annual_consistency = (fund_annual > bench_annual).sum() / len(fund_annual) if len(fund_annual) > 0 else None

    return monthly_consistency, annual_consistency

def calculate_drawdown_recovery(returns):
    """Calculate time to recover from maximum drawdown in years

    Args:
        returns: Series of returns

    Returns:
        float: Recovery time in years, or None if still in drawdown
    """
    if returns is None or len(returns) < 2:
        return None

    # Calculate cumulative returns
    cum_returns = (1 + returns).cumprod()

    # Calculate running maximum
    running_max = cum_returns.expanding().max()

    # Find max drawdown point
    drawdown = (cum_returns - running_max) / running_max
    max_dd_idx = drawdown.idxmin()

    # Find when it recovered (first time cum_returns >= running_max after max_dd)
    after_max_dd = cum_returns.loc[max_dd_idx:]
    recovery_point = running_max.loc[max_dd_idx]

    recovery_idx = after_max_dd[after_max_dd >= recovery_point].first_valid_index()

    if recovery_idx is None or recovery_idx == max_dd_idx:
        # Still in drawdown
        return None

    # Calculate recovery time in years
    recovery_days = (recovery_idx - max_dd_idx).days
    recovery_years = recovery_days / TRADING_DAYS

    return recovery_years

def calculate_capture_ratios(fund_returns, benchmark_returns):
    """Calculate upcapture and downcapture ratios

    Args:
        fund_returns: Series of fund returns
        benchmark_returns: Series of benchmark returns

    Returns:
        tuple: (upcapture_ratio, downcapture_ratio)
    """
    if fund_returns is None or benchmark_returns is None:
        return None, None

    # Separate up and down periods based on benchmark
    up_periods = benchmark_returns > 0
    down_periods = benchmark_returns < 0

    # Calculate average returns in each period
    fund_up_avg = fund_returns[up_periods].mean() if up_periods.sum() > 0 else 0
    bench_up_avg = benchmark_returns[up_periods].mean() if up_periods.sum() > 0 else 0

    fund_down_avg = fund_returns[down_periods].mean() if down_periods.sum() > 0 else 0
    bench_down_avg = benchmark_returns[down_periods].mean() if down_periods.sum() > 0 else 0

    # Calculate ratios (annualized for consistency)
    upcapture = (fund_up_avg / bench_up_avg) if bench_up_avg != 0 else None
    downcapture = (fund_down_avg / bench_down_avg) if bench_down_avg != 0 else None

    return upcapture, downcapture

def calculate_all_metrics(returns, benchmark_returns=None, risk_free_rate=0.0249):
    """Calculate all performance metrics organized by category"""
    max_wins, max_losses = calculate_consecutive_streaks(returns)
    expected_daily, expected_monthly, expected_annual = calculate_expected_returns(returns)
    var, cvar = calculate_var_cvar(returns)
    upper_tail, lower_tail = calculate_tail_ratios(returns)

    # Calculate active metrics if benchmark available
    active_return, active_risk, information_ratio = None, None, None
    monthly_consistency, annual_consistency = None, None
    upcapture_ratio, downcapture_ratio = None, None
    if benchmark_returns is not None:
        active_return, active_risk, information_ratio = calculate_active_metrics(returns, benchmark_returns)
        monthly_consistency, annual_consistency = calculate_consistency_metrics(returns, benchmark_returns)
        upcapture_ratio, downcapture_ratio = calculate_capture_ratios(returns, benchmark_returns)

    # Return Metrics
    return_metrics = {
        'Cumulative Return': calculate_cumulative_return(returns),
        'CAGR': calculate_cagr(returns),
        'Expected Annual Return': expected_annual,
        'Active Return': active_return,
        'Monthly Consistency': monthly_consistency,
        'Annual Consistency': annual_consistency,
    }

    # Add Beta to return metrics if benchmark available
    if benchmark_returns is not None:
        beta, correlation, r_squared = calculate_beta_correlation(returns, benchmark_returns)
        if beta is not None:
            return_metrics['Beta'] = beta

    # Calculate drawdown recovery
    recovery_years = calculate_drawdown_recovery(returns)

    # Annualize CVaR
    cvar_annualized = cvar * np.sqrt(TRADING_DAYS)

    # Convert Longest DD to years
    longest_dd_days = calculate_longest_drawdown(returns)
    longest_dd_years = longest_dd_days / TRADING_DAYS if longest_dd_days is not None else None

    # Risk Metrics
    risk_metrics = {
        'Volatility (ann.)': calculate_volatility(returns),
        'Max Drawdown': calculate_max_drawdown(returns),
        'Avg Drawdown': calculate_average_drawdown(returns),
        'Longest DD Years': longest_dd_years,
        'CVaR (95%)': cvar_annualized,
        'Drawdown Recovery Years': recovery_years,
        'Active Risk': active_risk,
    }

    # Ratio Metrics (now called Risk Adjusted Metrics in UI)
    ratio_metrics = {
        'Sharpe Ratio': calculate_sharpe_ratio(returns, risk_free_rate),
        'Sortino Ratio': calculate_sortino_ratio(returns, risk_free_rate),
        'Calmar Ratio': calculate_calmar_ratio(returns, risk_free_rate),
        'Omega Ratio': calculate_omega_ratio(returns, risk_free_rate),
        'Information Ratio': information_ratio,
        'Upcapture Ratio': upcapture_ratio,
        'Downcapture Ratio': downcapture_ratio,
        'Lower Tail Ratio': lower_tail,
        'Upper Tail Ratio': upper_tail,
    }

    # Combine all metrics
    metrics = {**return_metrics, **risk_metrics, **ratio_metrics}

    # Add remaining benchmark-relative metrics (Beta already added to return_metrics above)
    if benchmark_returns is not None:
        beta, correlation, r_squared = calculate_beta_correlation(returns, benchmark_returns)
        if correlation is not None:
            metrics['Correlation'] = correlation
            metrics['R²'] = r_squared

            # Calculate Alpha using CAGR values
            fund_cagr = metrics['CAGR']
            benchmark_cagr = calculate_cagr(benchmark_returns)
            alpha = calculate_alpha(fund_cagr, benchmark_cagr, beta, risk_free_rate)
            if alpha is not None:
                metrics['Alpha'] = alpha

    return metrics

def create_sip_progression_table(strategy_returns, benchmark_returns,
                                  comparison_returns=None, monthly_investment=100):
    """Create SIP progression table with monthly investment tracking

    Args:
        strategy_returns: Series with main fund daily returns
        benchmark_returns: Series with benchmark daily returns
        comparison_returns: Optional Series with comparison fund returns
        monthly_investment: Monthly investment amount (default 100)

    Returns:
        DataFrame with columns: Period, Invested, Fund Value, Benchmark Value, [Comp Value]
        Plus two footer rows: TOTAL and IRR (%)
    """
    from scipy.optimize import newton

    # 1. Resample all returns to monthly frequency
    strategy_monthly = strategy_returns.dropna().resample('ME').apply(lambda x: (1 + x).prod() - 1)
    benchmark_monthly = benchmark_returns.dropna().resample('ME').apply(lambda x: (1 + x).prod() - 1)

    if comparison_returns is not None:
        comparison_monthly = comparison_returns.dropna().resample('ME').apply(lambda x: (1 + x).prod() - 1)
    else:
        comparison_monthly = None

    # 2. Align all series to same date range
    if comparison_monthly is not None:
        # Align all three
        strategy_monthly, benchmark_monthly = strategy_monthly.align(benchmark_monthly, join='inner')
        strategy_monthly, comparison_monthly = strategy_monthly.align(comparison_monthly, join='inner')
        benchmark_monthly = benchmark_monthly.loc[strategy_monthly.index]
    else:
        # Align just two
        strategy_monthly, benchmark_monthly = strategy_monthly.align(benchmark_monthly, join='inner')

    # 3. Calculate SIP progression
    n_months = len(strategy_monthly)

    # Initialize tracking arrays
    data = []

    strategy_portfolio = 0
    benchmark_portfolio = 0
    comparison_portfolio = 0 if comparison_monthly is not None else None

    for i, date in enumerate(strategy_monthly.index):
        # Add monthly investment at start of month
        cumulative_invested = (i + 1) * monthly_investment

        # Apply returns to portfolios
        strategy_portfolio += monthly_investment
        strategy_portfolio *= (1 + strategy_monthly.iloc[i])

        benchmark_portfolio += monthly_investment
        benchmark_portfolio *= (1 + benchmark_monthly.iloc[i])

        if comparison_monthly is not None:
            comparison_portfolio += monthly_investment
            comparison_portfolio *= (1 + comparison_monthly.iloc[i])

        # Build row
        row = {
            'Period': date.strftime('%Y-%m'),
            'Invested': cumulative_invested,
            'Fund Value': strategy_portfolio,
            'Benchmark Value': benchmark_portfolio
        }

        if comparison_monthly is not None:
            row['Comp Value'] = comparison_portfolio

        data.append(row)

    # 4. Create DataFrame
    df = pd.DataFrame(data)

    # 5. Calculate IRR for each investment
    def calculate_irr(portfolio_value, months_invested):
        """Calculate annualized IRR"""
        total_invested = months_invested * monthly_investment
        cash_flows = np.full(months_invested + 1, -monthly_investment, dtype=float)
        cash_flows[-1] = portfolio_value

        try:
            def npv(rate, cash_flows):
                return sum(cf / (1 + rate) ** i for i, cf in enumerate(cash_flows))

            monthly_irr = newton(lambda r: npv(r, cash_flows), x0=0.01, maxiter=100)
            annual_irr = (1 + monthly_irr) ** 12 - 1
            return annual_irr * 100  # Return as percentage
        except (RuntimeError, ValueError):
            return None

    # 6. Add TOTAL row
    total_row = {
        'Period': 'TOTAL',
        'Invested': n_months * monthly_investment,
        'Fund Value': strategy_portfolio,
        'Benchmark Value': benchmark_portfolio
    }
    if comparison_monthly is not None:
        total_row['Comp Value'] = comparison_portfolio

    df = pd.concat([df, pd.DataFrame([total_row])], ignore_index=True)

    # 7. Add IRR row
    irr_row = {
        'Period': 'IRR (%)',
        'Invested': '',
        'Fund Value': calculate_irr(strategy_portfolio, n_months),
        'Benchmark Value': calculate_irr(benchmark_portfolio, n_months)
    }
    if comparison_monthly is not None:
        irr_row['Comp Value'] = calculate_irr(comparison_portfolio, n_months)

    df = pd.concat([df, pd.DataFrame([irr_row])], ignore_index=True)

    return df