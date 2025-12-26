import pandas as pd
import numpy as np

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

    return pd.DataFrame(metrics_data)

def create_metric_category_df(strategy_metrics, benchmark_metrics, metric_names,
                              strategy_display=None, benchmark_display=None,
                              comparison_metrics=None, comparison_display=None):
    """
    Create a formatted dataframe for a specific category of metrics

    Args:
        strategy_metrics: Dict of all strategy metrics
        benchmark_metrics: Dict of all benchmark metrics
        metric_names: List of metric names to include in this category
        strategy_display: Optional display name for strategy (used in helper text, not column header)
        benchmark_display: Optional display name for benchmark (used in helper text, not column header)
        comparison_metrics: Optional dict of comparison fund metrics
        comparison_display: Optional display name for comparison (used in helper text, not column header)

    Returns:
        DataFrame with columns: Metric | Main Fund | Benchmark [| Comp Fund]
    """
    metrics_data = []

    for metric_name in metric_names:
        if metric_name in strategy_metrics:
            row_data = {
                'Metric': metric_name,
                'Main Fund': format_metric_value(metric_name, strategy_metrics[metric_name]),
                'Benchmark': format_metric_value(metric_name, benchmark_metrics.get(metric_name, 0))
            }

            # Add comparison column if provided
            if comparison_metrics is not None and comparison_display is not None:
                row_data['Comp Fund'] = format_metric_value(
                    metric_name, comparison_metrics.get(metric_name, 0)
                )

            metrics_data.append(row_data)

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
    

group_cols = ['scheme_code', 
        'scheme_name',
      'plan_type','scheme_category_level1','scheme_category_level2','display_name']
    
def prepare_data_for_fund_universe(df,group_cols=group_cols):
        analysis_df = (df
                        .sort_values(['scheme_code', 'date'], ascending=[True, True])
                        .assign(
                        perc_return = lambda x:x.groupby('scheme_code') ['nav'].pct_change(),
                        log_return  = lambda x:np.log1p(x['perc_return'])
                        )
            )
        
        annual_df = (analysis_df
        .groupby([*group_cols, pd.Grouper(key='date',freq='YE')],dropna=False)['log_return'].sum()
        .reset_index()
        )
        
        return annual_df


def calculate_fund_metrics_table(df, risk_free_rate=0.0249, start_date=None, end_date=None):
    """
    Calculate comprehensive metrics for each fund and category.

    Parameters:
    -----------
    df : pandas.DataFrame
        Raw fund data with columns: date, scheme_code, scheme_name, nav,
        scheme_category_level2, display_name
    risk_free_rate : float
        Annual risk-free rate (default: 2.49%)
    start_date : str or datetime, optional
        Start date for cache key
    end_date : str or datetime, optional
        End date for cache key

    Returns:
    --------
    tuple: (fund_metrics_df, category_metrics_df)
        - fund_metrics_df: DataFrame with all metrics for each fund
        - category_metrics_df: DataFrame with aggregated category metrics
    """
    from src.metrics import calculate_all_metrics
    from src.computation_cache import get_cached_metrics, get_cached_annual_returns

    # Calculate daily returns for each fund
    fund_data = (df
        .sort_values(['scheme_code', 'date'], ascending=[True, True])
        .assign(
            returns=lambda x: x.groupby('scheme_code')['nav'].pct_change()
        )
    )

    # Calculate metrics for each fund
    fund_metrics = []

    for (scheme_code, scheme_name, category, display_name), group in fund_data.groupby(
        ['scheme_code', 'scheme_name', 'scheme_category_level2', 'display_name']
    ):
        returns = group['returns'].dropna()

        if len(returns) > 0:
            # Calculate all metrics using session cache
            if start_date and end_date:
                all_metrics = get_cached_metrics(
                    display_name, returns, None,
                    risk_free_rate, start_date, end_date
                )
            else:
                # Fallback if dates not provided
                all_metrics = calculate_all_metrics(
                    returns=returns,
                    benchmark_returns=None,
                    risk_free_rate=risk_free_rate
                )

            # Calculate annual returns using cache
            if start_date and end_date:
                returns_with_date = group.set_index('date')['returns'].dropna()
                annual_returns = get_cached_annual_returns(
                    display_name, returns_with_date, start_date, end_date
                )
                annual_returns_list = (annual_returns * 100).tolist()
            else:
                # Fallback calculation
                returns_with_date = group.set_index('date')['returns'].dropna()
                annual_returns = returns_with_date.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
                annual_returns_list = annual_returns.tolist()

            # Get date range
            start_year = group['date'].min().year
            end_year = group['date'].max().year
            data_range = f"{start_year}-{end_year}"

            # Combine everything
            metrics = {
                'scheme_code': scheme_code,
                'scheme_name': scheme_name,
                'display_name': display_name,
                'category': category,
                'data_range': data_range,
                'annual_return_trend': annual_returns_list,
                **all_metrics  # Unpack all calculated metrics
            }
            fund_metrics.append(metrics)

    fund_metrics_df = pd.DataFrame(fund_metrics)

    # Calculate category-level aggregates
    category_metrics = fund_metrics_df.groupby('category').agg({
        'CAGR': ['median', 'mean'],
        'Volatility (ann.)': 'median',
        'Max Drawdown': ['min', 'max'],
        'Sharpe Ratio': ['min', 'max']
    }).reset_index()

    # Flatten column names
    category_metrics.columns = [
        'category',
        'median_return',
        'mean_return',
        'median_volatility',
        'min_drawdown',
        'max_drawdown',
        'min_sharpe',
        'max_sharpe'
    ]

    return fund_metrics_df, category_metrics


def highlight_outliers_in_monthly_table(monthly_table_df):
    """Apply highlighting to outlier cells (2 std dev away from mean)

    Args:
        monthly_table_df: DataFrame with monthly returns (Year column + month columns)

    Returns:
        Styled DataFrame with outliers highlighted
    """
    import pandas as pd
    import numpy as np

    # Get month columns (exclude 'Year' and 'YTD')
    month_cols = [col for col in monthly_table_df.columns if col not in ['Year', 'YTD']]

    # Calculate statistics across all monthly returns (excluding YTD)
    all_returns = monthly_table_df[month_cols].values.flatten()
    all_returns = all_returns[~np.isnan(all_returns)]  # Remove NaN values

    mean_return = np.mean(all_returns)
    std_return = np.std(all_returns)

    # Define thresholds
    upper_threshold = mean_return + 2 * std_return
    lower_threshold = mean_return - 2 * std_return

    def highlight_cell(val):
        """Return background color for outlier cells"""
        if pd.isna(val):
            return ''

        if val > upper_threshold:
            return 'background-color: #d4edda; font-weight: bold'  # Light green for positive outliers
        elif val < lower_threshold:
            return 'background-color: #f8d7da; font-weight: bold'  # Light red for negative outliers
        else:
            return ''

    # Apply styling to monthly columns only (not YTD)
    styled_df = monthly_table_df.style.applymap(
        highlight_cell,
        subset=month_cols
    )

    # Make YTD column bold (if it exists)
    if 'YTD' in monthly_table_df.columns:
        styled_df = styled_df.applymap(
            lambda val: 'font-weight: bold',
            subset=['YTD']
        )

    # Format all numeric columns (including YTD)
    all_numeric_cols = [col for col in monthly_table_df.columns if col != 'Year']
    styled_df = styled_df.format({col: '{:.2f}' for col in all_numeric_cols})

    return styled_df
