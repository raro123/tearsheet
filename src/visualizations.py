import plotly.graph_objects as go
import pandas as pd
import numpy as np
from plotly.subplots import make_subplots
from scipy import stats

def create_cumulative_returns_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name,
                                    comparison_returns=None, comparison_name=None):
    """Create cumulative returns comparison chart"""
    strategy_cum = (1 + strategy_returns).cumprod()
    benchmark_cum = (1 + benchmark_returns).cumprod()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=strategy_cum.index,
        y=(strategy_cum - 1) * 100,
        name=strategy_name,
        line=dict(color='#1E3A5F', width=2),
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=benchmark_cum.index,
        y=(benchmark_cum - 1) * 100,
        name=benchmark_name,
        line=dict(color='#94A3B8', width=2, dash='dash'),
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    # Add comparison fund if provided
    if comparison_returns is not None and comparison_name is not None:
        comparison_cum = (1 + comparison_returns).cumprod()
        fig.add_trace(go.Scatter(
            x=comparison_cum.index,
            y=(comparison_cum - 1) * 100,
            name=comparison_name,
            line=dict(color='#D4AF37', width=2),
            hovertemplate='%{y:.2f}%<extra></extra>'
        ))

    fig.update_layout(
        title=dict(text="Cumulative Returns vs Benchmark", font=dict(size=18, weight='bold')),
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)",
        yaxis=dict(side='right'),
        hovermode='x unified',
        height=450,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        margin=dict(b=100)
    )

    return fig

def create_drawdown_chart(returns, name):
    """Create drawdown chart"""
    cumulative = (1 + returns).cumprod()
    running_max = cumulative.expanding().max()
    drawdown = (cumulative - running_max) / running_max * 100

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=drawdown.index,
        y=drawdown,
        fill='tozeroy',
        name='Drawdown',
        line=dict(color='#ef4444', width=1),
        fillcolor='rgba(239, 68, 68, 0.3)',
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=f"Drawdown - {name}",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        yaxis=dict(side='right'),
        hovermode='x unified',
        height=300,
        template='plotly_white'
    )

    return fig

def create_drawdown_comparison_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name,
                                     comparison_returns=None, comparison_name=None):
    """Create drawdown comparison chart for strategy vs benchmark"""
    # Calculate strategy drawdown
    strategy_cumulative = (1 + strategy_returns).cumprod()
    strategy_running_max = strategy_cumulative.expanding().max()
    strategy_drawdown = (strategy_cumulative - strategy_running_max) / strategy_running_max * 100

    # Calculate benchmark drawdown
    benchmark_cumulative = (1 + benchmark_returns).cumprod()
    benchmark_running_max = benchmark_cumulative.expanding().max()
    benchmark_drawdown = (benchmark_cumulative - benchmark_running_max) / benchmark_running_max * 100

    fig = go.Figure()

    # Add benchmark drawdown as area (drawn first, appears at bottom)
    fig.add_trace(go.Scatter(
        x=benchmark_drawdown.index,
        y=benchmark_drawdown,
        name=benchmark_name,
        fill='tozeroy',
        line=dict(color='#94A3B8', width=2, dash='dash'),
        fillcolor='rgba(148, 163, 184, 0.2)',
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    # Add comparison fund drawdown if provided (drawn second)
    if comparison_returns is not None and comparison_name is not None:
        comparison_cumulative = (1 + comparison_returns).cumprod()
        comparison_running_max = comparison_cumulative.expanding().max()
        comparison_drawdown = (comparison_cumulative - comparison_running_max) / comparison_running_max * 100

        fig.add_trace(go.Scatter(
            x=comparison_drawdown.index,
            y=comparison_drawdown,
            name=comparison_name,
            fill='tozeroy',
            line=dict(color='#D4AF37', width=2),
            fillcolor='rgba(212, 175, 55, 0.3)',
            hovertemplate='%{y:.2f}%<extra></extra>'
        ))

    # Add strategy drawdown as area (drawn last, appears on top)
    fig.add_trace(go.Scatter(
        x=strategy_drawdown.index,
        y=strategy_drawdown,
        name=strategy_name,
        fill='tozeroy',
        line=dict(color='#1E3A5F', width=2),
        fillcolor='rgba(30, 58, 95, 0.3)',
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Drawdown Comparison", font=dict(size=18, weight='bold')),
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        yaxis=dict(side='right'),
        hovermode='x unified',
        height=450,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        margin=dict(b=100)
    )

    return fig

def create_monthly_returns_heatmap(returns, name):
    """Create monthly returns heatmap"""
    monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1) * 100

    monthly_returns_df = pd.DataFrame({
        'Year': monthly_returns.index.year,
        'Month': monthly_returns.index.month,
        'Return': monthly_returns.values
    })

    pivot = monthly_returns_df.pivot(index='Year', columns='Month', values='Return')

    fig = go.Figure(data=go.Heatmap(
        z=pivot.values,
        x=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
        y=pivot.index,
        colorscale='RdYlGn',
        zmid=0,
        text=np.round(pivot.values, 2),
        texttemplate='%{text:.1f}',
        textfont={"size": 10},
        colorbar=dict(title="Return (%)")
    ))

    fig.update_layout(
        title=f"Monthly Returns Heatmap - {name}",
        xaxis_title="Month",
        yaxis_title="Year",
        height=400,
        template='plotly_white'
    )

    return fig

def create_monthly_returns_table(returns):
    """Create monthly returns table with YTD column"""
    # Calculate monthly returns
    monthly_returns = returns.resample('M').apply(lambda x: (1 + x).prod() - 1) * 100

    # Create pivot table
    monthly_returns_df = pd.DataFrame({
        'Year': monthly_returns.index.year,
        'Month': monthly_returns.index.month,
        'Return': monthly_returns.values
    })

    pivot = monthly_returns_df.pivot(index='Year', columns='Month', values='Return')

    # Rename columns to month names
    month_names = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                   7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
    pivot.columns = [month_names.get(col, col) for col in pivot.columns]

    # Calculate YTD for each year
    ytd_returns = []
    for year in pivot.index:
        year_data = monthly_returns[monthly_returns.index.year == year]
        if len(year_data) > 0:
            # YTD is compound return: (1 + r1) * (1 + r2) * ... - 1
            ytd = ((1 + year_data / 100).prod() - 1) * 100
            ytd_returns.append(ytd)
        else:
            ytd_returns.append(np.nan)

    pivot['YTD'] = ytd_returns

    # Round to 2 decimal places
    pivot = pivot.round(2)

    # Sort by year descending (latest year first)
    pivot = pivot.sort_index(ascending=False)

    # Reset index to make Year a column
    pivot = pivot.reset_index()

    return pivot

def create_rolling_sharpe_chart(returns, benchmark_returns, strategy_name, benchmark_name, window=252, risk_free_rate=0.0249):
    """Create rolling Sharpe ratio chart"""
    TRADING_DAYS = 252

    rolling_sharpe = (returns.rolling(window).mean() * TRADING_DAYS - risk_free_rate) / \
                     (returns.rolling(window).std() * np.sqrt(TRADING_DAYS))
    bench_rolling_sharpe = (benchmark_returns.rolling(window).mean() * TRADING_DAYS - risk_free_rate) / \
                           (benchmark_returns.rolling(window).std() * np.sqrt(TRADING_DAYS))

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=rolling_sharpe.index,
        y=rolling_sharpe,
        name=strategy_name,
        line=dict(color='#1E3A5F', width=2),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=bench_rolling_sharpe.index,
        y=bench_rolling_sharpe,
        name=benchmark_name,
        line=dict(color='#94A3B8', width=2, dash='dash'),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Rolling Sharpe Ratio ({window} days)",
        xaxis_title="Date",
        yaxis_title="Sharpe Ratio",
        yaxis=dict(side='right'),
        hovermode='x unified',
        height=300,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

def create_log_returns_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name,
                             comparison_returns=None, comparison_name=None):
    """Create log-scaled cumulative returns chart"""
    strategy_cum = (1 + strategy_returns).cumprod()
    benchmark_cum = (1 + benchmark_returns).cumprod()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=strategy_cum.index,
        y=strategy_cum,
        name=strategy_name,
        line=dict(color='#1E3A5F', width=2),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=benchmark_cum.index,
        y=benchmark_cum,
        name=benchmark_name,
        line=dict(color='#94A3B8', width=2, dash='dash'),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))

    # Add comparison fund if provided
    if comparison_returns is not None and comparison_name is not None:
        comparison_cum = (1 + comparison_returns).cumprod()
        fig.add_trace(go.Scatter(
            x=comparison_cum.index,
            y=comparison_cum,
            name=comparison_name,
            line=dict(color='#D4AF37', width=2),
            hovertemplate='%{y:.2f}<extra></extra>'
        ))

    fig.update_layout(
        title=dict(text="Cumulative Returns (Log Scale)", font=dict(size=18, weight='bold')),
        xaxis_title="Date",
        yaxis_title="Growth of $1",
        yaxis=dict(type="log", side='right'),
        hovermode='x unified',
        height=450,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        margin=dict(b=100)
    )

    return fig

def create_rolling_returns_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name, window=252,
                                 comparison_returns=None, comparison_name=None):
    """Create rolling returns comparison chart"""
    TRADING_DAYS = 252

    # Calculate rolling returns (annualized)
    strategy_rolling = strategy_returns.rolling(window).apply(lambda x: (1 + x).prod() - 1) * (TRADING_DAYS / window) * 100
    benchmark_rolling = benchmark_returns.rolling(window).apply(lambda x: (1 + x).prod() - 1) * (TRADING_DAYS / window) * 100

    fig = go.Figure()

    # Add strategy rolling returns
    fig.add_trace(go.Scatter(
        x=strategy_rolling.index,
        y=strategy_rolling,
        name=strategy_name,
        line=dict(color='#1E3A5F', width=2),
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    # Add benchmark rolling returns
    fig.add_trace(go.Scatter(
        x=benchmark_rolling.index,
        y=benchmark_rolling,
        name=benchmark_name,
        line=dict(color='#94A3B8', width=2, dash='dash'),
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    # Add comparison fund rolling returns if provided
    if comparison_returns is not None and comparison_name is not None:
        comparison_rolling = comparison_returns.rolling(window).apply(lambda x: (1 + x).prod() - 1) * (TRADING_DAYS / window) * 100
        fig.add_trace(go.Scatter(
            x=comparison_rolling.index,
            y=comparison_rolling,
            name=comparison_name,
            line=dict(color='#D4AF37', width=2),
            hovertemplate='%{y:.2f}%<extra></extra>'
        ))

    # Determine period label
    period_label = f"{window} days"
    if window == 252:
        period_label = "1 Year"
    elif window == 756:
        period_label = "3 Years"
    elif window == 1260:
        period_label = "5 Years"

    fig.update_layout(
        title=dict(text=f"Rolling Returns ({period_label}, Annualized)", font=dict(size=18, weight='bold')),
        xaxis_title="Date",
        yaxis_title="Annualized Return (%)",
        yaxis=dict(side='right'),
        hovermode='x unified',
        height=450,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        margin=dict(b=100)
    )

    return fig

def create_rolling_analysis_subplot(strategy_returns, benchmark_returns, strategy_name, benchmark_name,
                                    window=252, ewm_span=126, use_ewm=False, period_label="1 Year",
                                    comparison_returns=None, comparison_name=None):
    """Create 2x2 subplot with rolling metrics: Returns, Volatility, Beta, Correlation

    Args:
        strategy_returns: Series with strategy daily returns
        benchmark_returns: Series with benchmark daily returns
        strategy_name: String name of strategy fund
        benchmark_name: String name of benchmark
        window: Rolling window size in trading days (for simple rolling)
        ewm_span: Span parameter for exponential weighted (for EWM method)
        use_ewm: Boolean, if True uses exponential weighted, else simple rolling
        period_label: String label for the period (e.g., "1 Year", "3 Years")
        comparison_returns: Optional Series with comparison fund returns
        comparison_name: Optional String name of comparison fund

    Returns:
        Plotly figure with 2x2 subplots
    """
    import numpy as np
    TRADING_DAYS = 252

    # Align returns for beta and correlation calculations
    aligned_strategy, aligned_benchmark = strategy_returns.align(benchmark_returns, join='inner')

    # Create 2x2 subplot
    fig = make_subplots(
        rows=2, cols=2,
        row_heights=[0.5, 0.5],
        horizontal_spacing=0.1,
        vertical_spacing=0.1,
        subplot_titles=(
            f"Rolling Returns ({period_label})",
            f"Rolling Volatility ({period_label})",
            f"Rolling Beta ({period_label})",
            f"Rolling Correlation ({period_label})"
        )
    )

    # === CHART 1: ROLLING RETURNS (Row 1, Col 1) ===
    if use_ewm:
        strategy_rolling_returns = aligned_strategy.ewm(span=ewm_span, min_periods=window).mean() * TRADING_DAYS * 100
        benchmark_rolling_returns = aligned_benchmark.ewm(span=ewm_span, min_periods=window).mean() * TRADING_DAYS * 100
    else:
        strategy_rolling_returns = aligned_strategy.rolling(window).apply(
            lambda x: (1 + x).prod() - 1
        ) * (TRADING_DAYS / window) * 100
        benchmark_rolling_returns = aligned_benchmark.rolling(window).apply(
            lambda x: (1 + x).prod() - 1
        ) * (TRADING_DAYS / window) * 100

    # Add strategy returns
    fig.add_trace(go.Scatter(
        x=strategy_rolling_returns.dropna().index,
        y=strategy_rolling_returns.dropna(),
        name=strategy_name,
        line=dict(color='#1E3A5F', width=2),
        hovertemplate='%{y:.2f}%<extra></extra>',
        showlegend=True
    ), row=1, col=1)

    # Add benchmark returns
    fig.add_trace(go.Scatter(
        x=benchmark_rolling_returns.dropna().index,
        y=benchmark_rolling_returns.dropna(),
        name=benchmark_name,
        line=dict(color='#94A3B8', width=2, dash='dash'),
        hovertemplate='%{y:.2f}%<extra></extra>',
        showlegend=True
    ), row=1, col=1)

    # Add comparison returns if provided
    if comparison_returns is not None and comparison_name is not None:
        aligned_comparison, _ = comparison_returns.align(benchmark_returns, join='inner')
        if use_ewm:
            comparison_rolling_returns = aligned_comparison.ewm(span=ewm_span, min_periods=window).mean() * TRADING_DAYS * 100
        else:
            comparison_rolling_returns = aligned_comparison.rolling(window).apply(
                lambda x: (1 + x).prod() - 1
            ) * (TRADING_DAYS / window) * 100

        fig.add_trace(go.Scatter(
            x=comparison_rolling_returns.dropna().index,
            y=comparison_rolling_returns.dropna(),
            name=comparison_name,
            line=dict(color='#D4AF37', width=2),
            hovertemplate='%{y:.2f}%<extra></extra>',
            showlegend=True
        ), row=1, col=1)

    fig.update_yaxes(title_text="Annualized Return (%)", row=1, col=1)

    # === CHART 2: ROLLING VOLATILITY (Row 1, Col 2) ===
    if use_ewm:
        strategy_rolling_vol = aligned_strategy.ewm(span=ewm_span, min_periods=window).std() * np.sqrt(TRADING_DAYS) * 100
        benchmark_rolling_vol = aligned_benchmark.ewm(span=ewm_span, min_periods=window).std() * np.sqrt(TRADING_DAYS) * 100
    else:
        strategy_rolling_vol = aligned_strategy.rolling(window).std() * np.sqrt(TRADING_DAYS) * 100
        benchmark_rolling_vol = aligned_benchmark.rolling(window).std() * np.sqrt(TRADING_DAYS) * 100

    # Add strategy volatility
    fig.add_trace(go.Scatter(
        x=strategy_rolling_vol.dropna().index,
        y=strategy_rolling_vol.dropna(),
        name=strategy_name,
        line=dict(color='#1E3A5F', width=2),
        hovertemplate='%{y:.2f}%<extra></extra>',
        showlegend=False
    ), row=1, col=2)

    # Add benchmark volatility
    fig.add_trace(go.Scatter(
        x=benchmark_rolling_vol.dropna().index,
        y=benchmark_rolling_vol.dropna(),
        name=benchmark_name,
        line=dict(color='#94A3B8', width=2, dash='dash'),
        hovertemplate='%{y:.2f}%<extra></extra>',
        showlegend=False
    ), row=1, col=2)

    # Add comparison volatility if provided
    if comparison_returns is not None and comparison_name is not None:
        if use_ewm:
            comparison_rolling_vol = aligned_comparison.ewm(span=ewm_span, min_periods=window).std() * np.sqrt(TRADING_DAYS) * 100
        else:
            comparison_rolling_vol = aligned_comparison.rolling(window).std() * np.sqrt(TRADING_DAYS) * 100

        fig.add_trace(go.Scatter(
            x=comparison_rolling_vol.dropna().index,
            y=comparison_rolling_vol.dropna(),
            name=comparison_name,
            line=dict(color='#D4AF37', width=2),
            hovertemplate='%{y:.2f}%<extra></extra>',
            showlegend=False
        ), row=1, col=2)

    fig.update_yaxes(title_text="Annualized Volatility (%)", row=1, col=2)

    # === CHART 3: ROLLING BETA (Row 2, Col 1) ===
    if use_ewm:
        strategy_rolling_cov = aligned_strategy.ewm(span=ewm_span, min_periods=window).cov(aligned_benchmark)
        benchmark_rolling_var = aligned_benchmark.ewm(span=ewm_span, min_periods=window).var()
        strategy_rolling_beta = strategy_rolling_cov / benchmark_rolling_var
    else:
        strategy_rolling_cov = aligned_strategy.rolling(window).cov(aligned_benchmark)
        benchmark_rolling_var = aligned_benchmark.rolling(window).var()
        strategy_rolling_beta = strategy_rolling_cov / benchmark_rolling_var

    # Add strategy beta
    fig.add_trace(go.Scatter(
        x=strategy_rolling_beta.dropna().index,
        y=strategy_rolling_beta.dropna(),
        name=strategy_name,
        line=dict(color='#1E3A5F', width=2),
        hovertemplate='%{y:.2f}<extra></extra>',
        showlegend=False
    ), row=2, col=1)

    # Add comparison beta if provided
    if comparison_returns is not None and comparison_name is not None:
        if use_ewm:
            comparison_rolling_cov = aligned_comparison.ewm(span=ewm_span, min_periods=window).cov(aligned_benchmark)
            comparison_rolling_beta = comparison_rolling_cov / benchmark_rolling_var
        else:
            comparison_rolling_cov = aligned_comparison.rolling(window).cov(aligned_benchmark)
            comparison_rolling_beta = comparison_rolling_cov / benchmark_rolling_var

        fig.add_trace(go.Scatter(
            x=comparison_rolling_beta.dropna().index,
            y=comparison_rolling_beta.dropna(),
            name=comparison_name,
            line=dict(color='#D4AF37', width=2),
            hovertemplate='%{y:.2f}<extra></extra>',
            showlegend=False
        ), row=2, col=1)

    # Add reference line at Beta = 1.0
    fig.add_hline(y=1.0, line_dash="dot", line_color="gray", opacity=0.5, row=2, col=1)

    fig.update_yaxes(title_text="Beta", row=2, col=1)

    # === CHART 4: ROLLING CORRELATION (Row 2, Col 2) ===
    if use_ewm:
        strategy_rolling_corr = aligned_strategy.ewm(span=ewm_span, min_periods=window).corr(aligned_benchmark)
    else:
        strategy_rolling_corr = aligned_strategy.rolling(window).corr(aligned_benchmark)

    # Add strategy correlation
    fig.add_trace(go.Scatter(
        x=strategy_rolling_corr.dropna().index,
        y=strategy_rolling_corr.dropna(),
        name=strategy_name,
        line=dict(color='#1E3A5F', width=2),
        hovertemplate='%{y:.3f}<extra></extra>',
        showlegend=False
    ), row=2, col=2)

    # Add comparison correlation if provided
    if comparison_returns is not None and comparison_name is not None:
        if use_ewm:
            comparison_rolling_corr = aligned_comparison.ewm(span=ewm_span, min_periods=window).corr(aligned_benchmark)
        else:
            comparison_rolling_corr = aligned_comparison.rolling(window).corr(aligned_benchmark)

        fig.add_trace(go.Scatter(
            x=comparison_rolling_corr.dropna().index,
            y=comparison_rolling_corr.dropna(),
            name=comparison_name,
            line=dict(color='#D4AF37', width=2),
            hovertemplate='%{y:.3f}<extra></extra>',
            showlegend=False
        ), row=2, col=2)

        # Add strategy vs comparison fund correlation
        if use_ewm:
            strategy_comp_corr = aligned_strategy.ewm(span=ewm_span, min_periods=window).corr(aligned_comparison)
        else:
            strategy_comp_corr = aligned_strategy.rolling(window).corr(aligned_comparison)

        fig.add_trace(go.Scatter(
            x=strategy_comp_corr.dropna().index,
            y=strategy_comp_corr.dropna(),
            name=f"{strategy_name} vs {comparison_name}",
            line=dict(color='#8b5cf6', width=2, dash='dot'),
            hovertemplate='%{y:.3f}<extra></extra>',
            showlegend=True
        ), row=2, col=2)

    # Add reference lines at -1, 0, 1
    fig.add_hline(y=1.0, line_dash="dot", line_color="gray", opacity=0.5, row=2, col=2)
    fig.add_hline(y=0.0, line_dash="dot", line_color="gray", opacity=0.5, row=2, col=2)
    fig.add_hline(y=-1.0, line_dash="dot", line_color="gray", opacity=0.5, row=2, col=2)

    fig.update_yaxes(title_text="Correlation", range=[-1, 1], row=2, col=2)

    # === OVERALL LAYOUT ===
    fig.update_layout(
        height=900,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="bottom", y=-0.12, xanchor="center", x=0.5),
        margin=dict(t=80, b=100, l=60, r=60)
    )

    # Update all y-axes to be on right side
    fig.update_yaxes(side='right')

    return fig

def create_annual_returns_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name,
                                comparison_returns=None, comparison_name=None):
    """Create annual returns bar chart with data labels"""

    # Calculate annual returns
    strategy_annual = strategy_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
    benchmark_annual = benchmark_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100

    # Align both series to ensure they have the same years
    strategy_annual, benchmark_annual = strategy_annual.align(benchmark_annual, join='outer', fill_value=0)

    # If comparison fund is provided, add it to alignment
    if comparison_returns is not None:
        comparison_annual = comparison_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
        strategy_annual, comparison_annual = strategy_annual.align(comparison_annual, join='outer', fill_value=0)
        benchmark_annual, comparison_annual = benchmark_annual.align(comparison_annual, join='outer', fill_value=0)

    # Extract years
    years = strategy_annual.index.year

    fig = go.Figure()

    # Add strategy bars with labels
    fig.add_trace(
        go.Bar(
            x=years,
            y=strategy_annual.values,
            name=strategy_name,
            marker=dict(color='rgba(30, 58, 95, 0.8)', line=dict(width=0)),
            text=[f"{v:.0f}%" for v in strategy_annual.values],
            textposition='outside',
            textfont=dict(size=14, color='#1F2937'),
            hovertemplate='%{y:.2f}%<extra></extra>'
        )
    )

    # Add benchmark bars with labels
    fig.add_trace(
        go.Bar(
            x=years,
            y=benchmark_annual.values,
            name=benchmark_name,
            marker=dict(color='rgba(148, 163, 184, 0.7)', line=dict(width=0)),
            text=[f"{v:.0f}%" for v in benchmark_annual.values],
            textposition='outside',
            textfont=dict(size=14, color='#1F2937'),
            hovertemplate='%{y:.2f}%<extra></extra>'
        )
    )

    # Add comparison fund bars if provided
    if comparison_returns is not None and comparison_name is not None:
        fig.add_trace(
            go.Bar(
                x=years,
                y=comparison_annual.values,
                name=comparison_name,
                marker=dict(color='rgba(212, 175, 55, 0.8)', line=dict(width=0)),
                text=[f"{v:.0f}%" for v in comparison_annual.values],
                textposition='outside',
                textfont=dict(size=14, color='#1F2937'),
                hovertemplate='%{y:.2f}%<extra></extra>'
            )
        )

    # Update layout
    fig.update_layout(
        title=dict(text="Annual Returns", font=dict(size=18, weight='bold')),
        xaxis_title="Year",
        yaxis_title="Return (%)",
        height=500,
        template='plotly_white',
        barmode='group',
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        hovermode='x unified',
        margin=dict(t=80, b=110, l=50, r=50)  # Extra top margin for labels, bottom for legend
    )

    return fig

def create_performance_overview_subplot(strategy_returns, benchmark_returns, strategy_name, benchmark_name,
                                        comparison_returns=None, comparison_name=None, log_scale=False,
                                        sip_table_df=None):
    """Create integrated performance overview with SIP, cumulative returns, drawdown, and annual returns

    Args:
        strategy_returns: Series with strategy daily returns
        benchmark_returns: Series with benchmark daily returns
        strategy_name: String name of strategy fund
        benchmark_name: String name of benchmark
        comparison_returns: Optional Series with comparison fund returns
        comparison_name: Optional String name of comparison fund
        log_scale: Boolean, if True uses log scale for cumulative returns subplot
        sip_table_df: Optional SIP progression table (from create_sip_progression_table)

    Returns:
        Plotly figure with 4-row subplot (if sip_table_df provided) or 3-row subplot
    """
    # Create subplot with 4 rows (if SIP data provided) or 3 rows
    if sip_table_df is not None:
        fig = make_subplots(
            rows=4, cols=1,
            row_heights=[0.23, 0.35, 0.24, 0.18],
            vertical_spacing=0.08,
            subplot_titles=("SIP Portfolio Growth (₹100/month)",
                           "Cumulative Returns" + (" (Log Scale)" if log_scale else ""),
                           "Drawdown Comparison",
                           "Annual Returns")
        )
    else:
        fig = make_subplots(
            rows=3, cols=1,
            row_heights=[0.4, 0.3, 0.3],
            vertical_spacing=0.08,
            subplot_titles=("Cumulative Returns" + (" (Log Scale)" if log_scale else ""),
                           "Drawdown Comparison",
                           "Annual Returns")
        )

    # === ROW 1: SIP PORTFOLIO GROWTH (if sip_table_df provided) ===
    if sip_table_df is not None:
        # Prepare SIP data (remove TOTAL and IRR rows)
        chart_df = sip_table_df.iloc[:-2].copy()
        chart_df['Date'] = pd.to_datetime(chart_df['Period'] + '-01')

        # Add Amount Invested (reference line)
        fig.add_trace(go.Scatter(
            x=chart_df['Date'],
            y=chart_df['Invested'],
            name='Amount Invested',
            line=dict(color='#9CA3AF', width=2, dash='dash'),
            hovertemplate='Invested: ₹%{y:,.2f}<extra></extra>',
            showlegend=True
        ), row=1, col=1)

        # Add Fund Value
        fig.add_trace(go.Scatter(
            x=chart_df['Date'],
            y=chart_df['Fund Value'],
            name=strategy_name,
            line=dict(color='#1E3A5F', width=2),
            hovertemplate=f'{strategy_name}: ₹%{{y:,.2f}}<extra></extra>',
            showlegend=False  # Already in row 2 legend
        ), row=1, col=1)

        # Add Benchmark Value
        fig.add_trace(go.Scatter(
            x=chart_df['Date'],
            y=chart_df['Benchmark Value'],
            name=benchmark_name,
            line=dict(color='#94A3B8', width=2, dash='dash'),
            hovertemplate=f'{benchmark_name}: ₹%{{y:,.2f}}<extra></extra>',
            showlegend=False  # Already in row 2 legend
        ), row=1, col=1)

        # Add Comparison Value (conditional)
        if comparison_returns is not None and comparison_name is not None:
            if 'Comp Value' in chart_df.columns:
                fig.add_trace(go.Scatter(
                    x=chart_df['Date'],
                    y=chart_df['Comp Value'],
                    name=comparison_name,
                    line=dict(color='#D4AF37', width=2),
                    hovertemplate=f'{comparison_name}: ₹%{{y:,.2f}}<extra></extra>',
                    showlegend=False  # Already in row 2 legend
                ), row=1, col=1)

        # Configure row 1 axes
        fig.update_yaxes(title_text="Amount (₹)", row=1, col=1)
        fig.update_yaxes(tickformat='₹,.0f', side='right', row=1, col=1)

        # Add IRR annotation to row 1
        irr_row = sip_table_df.iloc[-1]
        total_row = sip_table_df.iloc[-2]

        annotation_lines = ['<b>IRR % | Final Amount</b>']

        # Fund
        fund_irr = irr_row['Fund Value']
        fund_final = total_row['Fund Value']
        if pd.notna(fund_irr) and fund_irr != '':
            annotation_lines.append(
                f'<span style="color:#1E3A5F">{fund_irr:.1f}% | ₹{fund_final:,.0f}</span>'
            )

        # Benchmark
        benchmark_irr = irr_row['Benchmark Value']
        benchmark_final = total_row['Benchmark Value']
        if pd.notna(benchmark_irr) and benchmark_irr != '':
            annotation_lines.append(
                f'<span style="color:#94A3B8">{benchmark_irr:.1f}% | ₹{benchmark_final:,.0f}</span>'
            )

        # Comparison
        if 'Comp Value' in irr_row and comparison_name is not None:
            comp_irr = irr_row['Comp Value']
            comp_final = total_row['Comp Value']
            if pd.notna(comp_irr) and comp_irr != '':
                annotation_lines.append(
                    f'<span style="color:#D4AF37">{comp_irr:.1f}% | ₹{comp_final:,.0f}</span>'
                )

        # Add annotation
        fig.add_annotation(
            text='<br>'.join(annotation_lines),
            xref='x1',
            yref='paper',
            x=chart_df['Date'].min(),
            y=0.98,  # Position at top of figure (top of row 1)
            xanchor='left',
            yanchor='top',
            showarrow=False,
            font=dict(size=11),
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='#D1D5DB',
            borderwidth=1,
            borderpad=8,
            align='left'
        )

    # Determine row numbers based on whether SIP is included
    cumulative_row = 2 if sip_table_df is not None else 1
    drawdown_row = 3 if sip_table_df is not None else 2
    annual_row = 4 if sip_table_df is not None else 3

    # === CUMULATIVE RETURNS ===
    strategy_cum = (1 + strategy_returns).cumprod() * 100
    benchmark_cum = (1 + benchmark_returns).cumprod() * 100

    if log_scale:
        # Log scale: show growth of ₹100
        fig.add_trace(go.Scatter(
            x=strategy_cum.index,
            y=strategy_cum,
            name=strategy_name,
            line=dict(color='#1E3A5F', width=2),
            hovertemplate='₹%{y:.2f}<extra></extra>',
            showlegend=True
        ), row=cumulative_row, col=1)

        fig.add_trace(go.Scatter(
            x=benchmark_cum.index,
            y=benchmark_cum,
            name=benchmark_name,
            line=dict(color='#94A3B8', width=2, dash='dash'),
            hovertemplate='₹%{y:.2f}<extra></extra>',
            showlegend=True
        ), row=cumulative_row, col=1)

        if comparison_returns is not None and comparison_name is not None:
            comparison_cum = (1 + comparison_returns).cumprod() * 100
            fig.add_trace(go.Scatter(
                x=comparison_cum.index,
                y=comparison_cum,
                name=comparison_name,
                line=dict(color='#D4AF37', width=2),
                hovertemplate='₹%{y:.2f}<extra></extra>',
                showlegend=True
            ), row=cumulative_row, col=1)

        fig.update_yaxes(title_text="Growth of ₹100", type="log", row=cumulative_row, col=1)
    else:
        # Linear scale: show growth of ₹100
        fig.add_trace(go.Scatter(
            x=strategy_cum.index,
            y=strategy_cum,
            name=strategy_name,
            line=dict(color='#1E3A5F', width=2),
            hovertemplate='₹%{y:.2f}<extra></extra>',
            showlegend=True
        ), row=cumulative_row, col=1)

        fig.add_trace(go.Scatter(
            x=benchmark_cum.index,
            y=benchmark_cum,
            name=benchmark_name,
            line=dict(color='#94A3B8', width=2, dash='dash'),
            hovertemplate='₹%{y:.2f}<extra></extra>',
            showlegend=True
        ), row=cumulative_row, col=1)

        if comparison_returns is not None and comparison_name is not None:
            comparison_cum = (1 + comparison_returns).cumprod() * 100
            fig.add_trace(go.Scatter(
                x=comparison_cum.index,
                y=comparison_cum,
                name=comparison_name,
                line=dict(color='#D4AF37', width=2),
                hovertemplate='₹%{y:.2f}<extra></extra>',
                showlegend=True
            ), row=cumulative_row, col=1)

        fig.update_yaxes(title_text="Growth of ₹100", row=cumulative_row, col=1)

    # === DRAWDOWN ===
    # Calculate strategy drawdown
    strategy_cumulative = (1 + strategy_returns).cumprod()
    strategy_running_max = strategy_cumulative.expanding().max()
    strategy_drawdown = (strategy_cumulative - strategy_running_max) / strategy_running_max * 100

    # Calculate benchmark drawdown
    benchmark_cumulative = (1 + benchmark_returns).cumprod()
    benchmark_running_max = benchmark_cumulative.expanding().max()
    benchmark_drawdown = (benchmark_cumulative - benchmark_running_max) / benchmark_running_max * 100

    fig.add_trace(go.Scatter(
        x=strategy_drawdown.index,
        y=strategy_drawdown,
        name=strategy_name,
        fill='tozeroy',
        line=dict(color='#1E3A5F', width=2),
        fillcolor='rgba(30, 58, 95, 0.3)',
        hovertemplate='%{y:.2f}%<extra></extra>',
        showlegend=False
    ), row=drawdown_row, col=1)

    fig.add_trace(go.Scatter(
        x=benchmark_drawdown.index,
        y=benchmark_drawdown,
        name=benchmark_name,
        fill='tozeroy',
        line=dict(color='#94A3B8', width=2, dash='dash'),
        fillcolor='rgba(148, 163, 184, 0.2)',
        hovertemplate='%{y:.2f}%<extra></extra>',
        showlegend=False
    ), row=drawdown_row, col=1)

    if comparison_returns is not None and comparison_name is not None:
        comparison_cumulative = (1 + comparison_returns).cumprod()
        comparison_running_max = comparison_cumulative.expanding().max()
        comparison_drawdown = (comparison_cumulative - comparison_running_max) / comparison_running_max * 100

        fig.add_trace(go.Scatter(
            x=comparison_drawdown.index,
            y=comparison_drawdown,
            name=comparison_name,
            fill='tozeroy',
            line=dict(color='#D4AF37', width=2),
            fillcolor='rgba(212, 175, 55, 0.3)',
            hovertemplate='%{y:.2f}%<extra></extra>',
            showlegend=False
        ), row=drawdown_row, col=1)

    fig.update_yaxes(title_text="Drawdown (%)", row=drawdown_row, col=1)

    # === ANNUAL RETURNS ===
    # Calculate annual returns
    strategy_annual = strategy_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
    benchmark_annual = benchmark_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100

    # Align both series to ensure they have the same years
    strategy_annual, benchmark_annual = strategy_annual.align(benchmark_annual, join='outer', fill_value=0)

    # If comparison fund is provided, add it to alignment
    if comparison_returns is not None:
        comparison_annual = comparison_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
        strategy_annual, comparison_annual = strategy_annual.align(comparison_annual, join='outer', fill_value=0)
        benchmark_annual, comparison_annual = benchmark_annual.align(comparison_annual, join='outer', fill_value=0)

    # Extract years
    years = strategy_annual.index.year

    # Add strategy bars
    fig.add_trace(
        go.Bar(
            x=years,
            y=strategy_annual.values,
            name=strategy_name,
            marker=dict(color='rgba(30, 58, 95, 0.8)', line=dict(width=0)),
            text=[f"{v:.0f}%" for v in strategy_annual.values],
            textposition='outside',
            textfont=dict(size=11, color='#1F2937'),
            hovertemplate='%{y:.2f}%<extra></extra>',
            showlegend=False
        ), row=annual_row, col=1
    )

    # Add benchmark bars
    fig.add_trace(
        go.Bar(
            x=years,
            y=benchmark_annual.values,
            name=benchmark_name,
            marker=dict(color='rgba(148, 163, 184, 0.7)', line=dict(width=0)),
            text=[f"{v:.0f}%" for v in benchmark_annual.values],
            textposition='outside',
            textfont=dict(size=11, color='#1F2937'),
            hovertemplate='%{y:.2f}%<extra></extra>',
            showlegend=False
        ), row=annual_row, col=1
    )

    # Add comparison fund bars if provided
    if comparison_returns is not None and comparison_name is not None:
        fig.add_trace(
            go.Bar(
                x=years,
                y=comparison_annual.values,
                name=comparison_name,
                marker=dict(color='rgba(212, 175, 55, 0.8)', line=dict(width=0)),
                text=[f"{v:.0f}%" for v in comparison_annual.values],
                textposition='outside',
                textfont=dict(size=11, color='#1F2937'),
                hovertemplate='%{y:.2f}%<extra></extra>',
                showlegend=False
            ), row=annual_row, col=1
        )

    fig.update_xaxes(title_text="Year", row=annual_row, col=1)
    fig.update_yaxes(title_text="Return (%)", row=annual_row, col=1)

    # === OVERALL LAYOUT ===
    fig.update_layout(
        height=1800 if sip_table_df is not None else 1200,
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation="h", yanchor="top", y=1.06, xanchor="center", x=0.5),
        margin=dict(t=80, b=80, l=60, r=60),
        barmode='group'
    )

    # Update all y-axes to be on right side
    fig.update_yaxes(side='right')

    return fig

def create_category_equity_curves(returns_dict, benchmark_returns, benchmark_name, log_scale=False, selected_funds=None):
    """Create equity curves for multiple funds in a category with monthly resolution showing growth of ₹100

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark
        log_scale: Boolean, if True uses logarithmic y-axis
        selected_funds: List of fund names to highlight with color (others shown in grayscale)

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Color palette for funds
    colors = [
        '#1E3A5F', '#ef4444', '#D4AF37', '#8b5cf6', '#ec4899',
        '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6'
    ]

    def resample_to_monthly(returns):
        """Resample daily returns to monthly returns"""
        # Use 'ME' (Month End) frequency and calculate compound return for each month
        return returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)

    def calculate_cagr(cum_returns, start_date, end_dates):
        """Calculate CAGR for each point in the series"""
        cagrs = []
        for i, end_date in enumerate(end_dates):
            years = (end_date - start_date).days / 365.25
            if years > 0:
                cagr = ((cum_returns.iloc[i]) ** (1 / years) - 1) * 100
                cagrs.append(cagr)
            else:
                cagrs.append(0)
        return cagrs

    # Grayscale color for unselected funds
    grayscale_color = '#999999'

    # Add each fund's equity curve
    for idx, (fund_name, returns) in enumerate(returns_dict.items()):
        # Resample to monthly
        monthly_returns = resample_to_monthly(returns)
        # Calculate cumulative returns on monthly data
        cum_returns = (1 + monthly_returns).cumprod()

        # Determine styling based on selection
        if selected_funds is None:
            # No selection mode: use colors for all (backward compatibility)
            color = colors[idx % len(colors)]
            opacity = 0.7
            width = 1.5
        elif fund_name in selected_funds:
            # Selected: use color palette
            color = colors[idx % len(colors)]
            opacity = 0.8  # Slightly more opaque when selected
            width = 2.0    # Slightly thicker
        else:
            # Not selected: grayscale
            color = grayscale_color
            opacity = 0.3  # More transparent
            width = 1.0    # Thinner

        # Calculate growth of 100
        growth_values = cum_returns * 100

        # Calculate CAGR for each point
        start_date = cum_returns.index[0]
        cagrs = calculate_cagr(cum_returns, start_date, cum_returns.index)

        # Create custom hover text with both growth and CAGR
        customdata = list(zip(cagrs))

        fig.add_trace(go.Scatter(
            x=cum_returns.index,
            y=growth_values,
            name=fund_name,
            line=dict(color=color, width=width),
            customdata=customdata,
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: ₹%{y:.2f}<br>CAGR: %{customdata[0]:.2f}%<extra></extra>',
            opacity=opacity
        ))

    # Add benchmark (thicker, distinct line)
    monthly_benchmark = resample_to_monthly(benchmark_returns)
    benchmark_cum = (1 + monthly_benchmark).cumprod()
    benchmark_growth = benchmark_cum * 100

    # Calculate benchmark CAGR
    start_date = benchmark_cum.index[0]
    benchmark_cagrs = calculate_cagr(benchmark_cum, start_date, benchmark_cum.index)
    customdata_bench = list(zip(benchmark_cagrs))

    fig.add_trace(go.Scatter(
        x=benchmark_cum.index,
        y=benchmark_growth,
        name=f"🔷 {benchmark_name}",
        line=dict(color='#94A3B8', width=3, dash='dash'),
        customdata=customdata_bench,
        hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: ₹%{y:.2f}<br>CAGR: %{customdata[0]:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Category Equity Curves - Growth of ₹100", font=dict(size=18, weight='bold')),
        xaxis_title="Date",
        yaxis_title="Growth of ₹100",
        yaxis_side='right',
        yaxis_type="log" if log_scale else "linear",
        hovermode='closest',
        height=600,
        template='plotly_white',
        showlegend=False
    )

    return fig

def create_annual_returns_bubble_chart(returns_dict, benchmark_returns, benchmark_name, start_date, end_date):
    """Create vertical bubble chart showing annual returns with jitter and box plot overlay

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark
        start_date: Start date for analysis
        end_date: End date for analysis

    Returns:
        Plotly figure
    """
    # Calculate annual returns and volatility for each fund
    all_data = []

    # Process each fund
    for fund_name, returns in returns_dict.items():
        # Calculate annual returns
        annual_returns = returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100

        # Calculate annual volatility
        annual_volatility = returns.resample('YE').std() * np.sqrt(252) * 100

        for year in annual_returns.index:
            all_data.append({
                'Fund': fund_name,
                'Year': year.year,
                'Annual Return': annual_returns[year],
                'Annual Volatility': annual_volatility[year],
                'Type': 'Fund'
            })

    # Add benchmark data
    benchmark_annual_returns = benchmark_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
    benchmark_annual_volatility = benchmark_returns.resample('YE').std() * np.sqrt(252) * 100

    for year in benchmark_annual_returns.index:
        all_data.append({
            'Fund': f"🔷 {benchmark_name}",
            'Year': year.year,
            'Annual Return': benchmark_annual_returns[year],
            'Annual Volatility': benchmark_annual_volatility[year],
            'Type': 'Benchmark'
        })

    # Create DataFrame
    df = pd.DataFrame(all_data)

    # Add jitter to Year for better visibility of overlapping bubbles
    np.random.seed(42)  # For reproducibility
    df['Year_Jittered'] = df['Year'] + np.random.uniform(-0.15, 0.15, size=len(df))

    # Color palette
    colors = [
        '#1E3A5F', '#ef4444', '#D4AF37', '#8b5cf6', '#ec4899',
        '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6'
    ]

    fig = go.Figure()

    # First, add box plot for each year (showing distribution)
    years = sorted(df['Year'].unique())
    for year in years:
        year_data = df[df['Year'] == year]
        fig.add_trace(go.Box(
            x=year_data['Annual Return'],
            y=[year] * len(year_data),  # All at same Y position
            name=f'Distribution {year}',
            orientation='h',
            marker=dict(color='lightgray', opacity=0.3),
            line=dict(color='gray', width=1),
            fillcolor='lightgray',
            opacity=0.5,
            boxmean=False,
            showlegend=False,
            hoverinfo='skip',  # Don't show hover for box plot
            width=0.3  # Narrower box plot
        ))

    # Get unique funds (excluding benchmark)
    funds = [f for f in df['Fund'].unique() if not f.startswith('🔷')]

    # Plot each fund with jitter
    for idx, fund_name in enumerate(funds):
        fund_data = df[df['Fund'] == fund_name].copy()
        color = colors[idx % len(colors)]

        # Add year as text for hover
        fund_data['Year_Text'] = fund_data['Year'].astype(str)

        fig.add_trace(go.Scatter(
            x=fund_data['Annual Return'],
            y=fund_data['Year_Jittered'],  # Use jittered year
            mode='markers',
            name=fund_name,
            marker=dict(
                size=fund_data['Annual Volatility'],
                sizemode='diameter',
                sizeref=2,
                color=color,
                line=dict(width=1, color='white'),
                opacity=0.7
            ),
            customdata=fund_data[['Year', 'Annual Volatility']],
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Year: %{customdata[0]:.0f}<br>' +
                         'Return: %{x:.2f}%<br>' +
                         'Volatility: %{customdata[1]:.2f}%' +
                         '<extra></extra>'
        ))

    # Plot benchmark with distinct style (no jitter for benchmark)
    benchmark_data = df[df['Type'] == 'Benchmark'].copy()
    fig.add_trace(go.Scatter(
        x=benchmark_data['Annual Return'],
        y=benchmark_data['Year'],  # No jitter for benchmark
        mode='markers',
        name=f"🔷 {benchmark_name}",
        marker=dict(
            size=benchmark_data['Annual Volatility'],
            sizemode='diameter',
            sizeref=2,
            color='#94A3B8',
            line=dict(width=2, color='#9CA3AF'),
            opacity=0.9,
            symbol='diamond'
        ),
        customdata=benchmark_data[['Year', 'Annual Volatility']],
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Year: %{customdata[0]:.0f}<br>' +
                     'Return: %{x:.2f}%<br>' +
                     'Volatility: %{customdata[1]:.2f}%' +
                     '<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text="Annual Returns Distribution by Year (Bubble Size: Annual Volatility)",
            font=dict(size=18, weight='bold')
        ),
        xaxis_title="Annual Return (%)",
        yaxis_title="Year",
        height=max(500, len(years) * 100),  # Dynamic height based on number of years
        template='plotly_white',
        showlegend=False,
        hovermode='closest',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray'
        ),
        yaxis=dict(
            dtick=1,  # Show every year
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            autorange='reversed'  # Most recent year at top
        )
    )

    return fig

def create_annual_returns_subplots(returns_dict, benchmark_returns, benchmark_name, start_date, end_date):
    """Create bar chart subplots showing annual returns by fund for each year

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark
        start_date: Start date for analysis
        end_date: End date for analysis

    Returns:
        Plotly figure with subplots
    """
    from plotly.subplots import make_subplots

    # Get all years in the range
    all_years = list(range(start_date.year, end_date.year + 1))

    # Calculate annual returns for each fund
    fund_annual_returns = {}
    for fund_name, returns in returns_dict.items():
        annual_returns = returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
        fund_annual_returns[fund_name] = {year: None for year in all_years}
        for year_date in annual_returns.index:
            year = year_date.year
            if year in all_years:
                fund_annual_returns[fund_name][year] = annual_returns[year_date]

    # Calculate benchmark annual returns
    benchmark_annual = benchmark_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
    benchmark_by_year = {year: None for year in all_years}
    for year_date in benchmark_annual.index:
        year = year_date.year
        if year in all_years:
            benchmark_by_year[year] = benchmark_annual[year_date]

    # Create subplots - one per year (horizontal columns, newest to oldest)
    num_years = len(all_years)
    reversed_years = list(reversed(all_years))  # Newest year first

    fig = make_subplots(
        rows=1, cols=num_years,
        subplot_titles=[str(year) for year in reversed_years],
        shared_yaxes=True,
        horizontal_spacing=0.03  # Spacing between columns
    )

    # Get fund names
    fund_names = list(returns_dict.keys())

    # Create display names by stripping IDs (everything after "|")
    display_names = {}
    for fund_name in fund_names:
        if '|' in fund_name:
            display_name = fund_name.split('|')[0].strip()
        else:
            display_name = fund_name
        display_names[fund_name] = display_name

    # Sort fund names alphabetically by display name (reverse so A is at top)
    fund_names_sorted = sorted(fund_names, key=lambda x: display_names[x], reverse=True)

    # For each year, create a bar chart
    for col_idx, year in enumerate(reversed_years, start=1):
        # Get returns for this year for all funds (in sorted order)
        year_returns = []
        for fund_name in fund_names_sorted:
            ret = fund_annual_returns[fund_name].get(year)
            year_returns.append(ret if ret is not None else 0)

        # Add all funds as a single trace for this year
        display_names_list = [display_names[fn] for fn in fund_names_sorted]
        text_labels = [f"{ret:.1f}%" for ret in year_returns]

        fig.add_trace(
            go.Bar(
                y=display_names_list,  # All fund names on Y-axis
                x=year_returns,        # All returns on X-axis
                orientation='h',       # Horizontal orientation
                marker=dict(color='#3b82f6'),  # Single blue color for all bars
                showlegend=False,      # No legend needed
                text=text_labels,      # Data labels at end of bars
                textposition='outside',
                hovertemplate='%{y}<br>Return: %{x:.2f}%<extra></extra>',
                width=0.8              # Bar width (0-1, where 1 = full category width)
            ),
            row=1, col=col_idx
        )

        # Add benchmark as vertical line
        benchmark_ret = benchmark_by_year.get(year)
        if benchmark_ret is not None:
            fig.add_vline(
                x=benchmark_ret,
                line_dash="dash",
                line_color="red",
                line_width=2,
                annotation=dict(
                    text=f"<b>{benchmark_ret:.1f}%</b>",
                    xanchor="left",
                    x=benchmark_ret,
                    yanchor="top",
                    y=1,
                    xshift=5,  # Offset 5px to the right of the line
                    font=dict(size=12),
                    bgcolor="rgba(255, 255, 255, 0.9)",  # White background with slight transparency
                    bordercolor="red",
                    borderwidth=1,
                    borderpad=4
                ),
                row=1, col=col_idx
            )

    # Update layout
    fig.update_layout(
        title=dict(
            text="Annual Returns by Year - Fund Comparison (Newest to Oldest)",
            font=dict(size=18, weight='bold')
        ),
        height=max(400, len(fund_names_sorted) * 40),  # Dynamic height based on number of funds
        width=num_years * 400,  # Wide enough for horizontal scrolling
        template='plotly_white',
        showlegend=False,  # No legend needed
        margin=dict(l=200, r=50, t=100, b=50),  # More left margin for fund names
        bargap=0.15  # Gap between bars (15%)
    )

    # Update x-axis label for all columns (Return %)
    for col in range(1, num_years + 1):
        fig.update_xaxes(title_text="Return (%)", row=1, col=col)

    return fig

def create_annual_returns_table(returns_dict, benchmark_returns, benchmark_name, start_date, end_date):
    """Create sortable table showing annual returns by fund for each year

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark
        start_date: Start date for analysis
        end_date: End date for analysis

    Returns:
        Styled pandas DataFrame
    """
    import pandas as pd

    # Get all years in the range
    all_years = list(range(start_date.year, end_date.year + 1))
    reversed_years = list(reversed(all_years))  # Newest year first

    # Calculate number of years for CAGR
    num_years = (end_date - start_date).days / 365.25

    # Calculate annual returns for each fund
    fund_annual_returns = {}
    fund_cagr = {}

    for fund_name, returns in returns_dict.items():
        annual_returns = returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
        fund_annual_returns[fund_name] = {year: None for year in all_years}
        for year_date in annual_returns.index:
            year = year_date.year
            if year in all_years:
                fund_annual_returns[fund_name][year] = annual_returns[year_date]

        # Calculate CAGR over entire period
        cumulative_ret = (1 + returns).prod()
        cagr = (cumulative_ret ** (1 / num_years) - 1) * 100
        fund_cagr[fund_name] = cagr

    # Calculate benchmark annual returns and CAGR
    benchmark_annual = benchmark_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
    benchmark_by_year = {year: None for year in all_years}
    for year_date in benchmark_annual.index:
        year = year_date.year
        if year in all_years:
            benchmark_by_year[year] = benchmark_annual[year_date]

    benchmark_cumulative = (1 + benchmark_returns).prod()
    benchmark_cagr = (benchmark_cumulative ** (1 / num_years) - 1) * 100

    # Get fund names and create display names
    fund_names = list(returns_dict.keys())
    display_names = {}
    for fund_name in fund_names:
        if '|' in fund_name:
            display_name = fund_name.split('|')[0].strip()
        else:
            display_name = fund_name
        display_names[fund_name] = display_name

    # Sort fund names alphabetically by display name
    fund_names_sorted = sorted(fund_names, key=lambda x: display_names[x])

    # Build DataFrame
    data_rows = []

    # Add fund rows
    for fund_name in fund_names_sorted:
        # Calculate Beat Benchmark count
        beat_count = 0
        total_count = 0
        for year in all_years:
            fund_ret = fund_annual_returns[fund_name].get(year)
            bench_ret = benchmark_by_year.get(year)
            # Only count years where both have valid data
            if fund_ret is not None and bench_ret is not None:
                total_count += 1
                if fund_ret > bench_ret:
                    beat_count += 1

        beat_benchmark_str = f"{beat_count}/{total_count}" if total_count > 0 else "-"

        row = {'Fund Name': display_names[fund_name]}
        row['Beat Benchmark'] = beat_benchmark_str
        row['CAGR'] = fund_cagr[fund_name]

        for year in reversed_years:
            ret = fund_annual_returns[fund_name].get(year)
            row[str(year)] = ret if ret is not None else None

        data_rows.append(row)

    # Add benchmark row
    benchmark_row = {'Fund Name': f"🔷 {benchmark_name}"}
    benchmark_row['Beat Benchmark'] = '-'
    benchmark_row['CAGR'] = benchmark_cagr
    for year in reversed_years:
        bench_ret = benchmark_by_year.get(year)
        benchmark_row[str(year)] = bench_ret if bench_ret is not None else None
    data_rows.append(benchmark_row)

    df = pd.DataFrame(data_rows)

    # Define formatting and styling functions
    def format_value(val):
        """Format cell values as percentages"""
        if pd.isna(val):
            return '-'
        return f'{val:.2f}%'

    def highlight_vs_benchmark(s, benchmark_row):
        """Highlight cells based on comparison with benchmark"""
        # Get benchmark value for this column
        benchmark_val = benchmark_row[s.name]

        # Apply styling to each cell
        styles = []
        for idx, val in enumerate(s):
            # Check if this is the benchmark row
            if idx == len(s) - 1:  # Last row is benchmark
                styles.append('background-color: #dbeafe; font-weight: bold')
            elif pd.isna(val) or pd.isna(benchmark_val):
                styles.append('')
            elif val > benchmark_val:
                styles.append('background-color: #dcfce7')  # Light green
            elif val < benchmark_val:
                styles.append('background-color: #fee2e2')  # Light red
            else:
                styles.append('background-color: #fef9c3')  # Light yellow

        return styles

    # Get benchmark row for comparison
    benchmark_row_data = df.iloc[-1]

    # Create styled dataframe
    styled_df = df.style.format({
        'CAGR': format_value,
        **{str(year): format_value for year in reversed_years}
    })

    # Apply conditional formatting for each numeric column (CAGR and year columns)
    numeric_cols = ['CAGR'] + [str(year) for year in reversed_years]
    for col in numeric_cols:
        styled_df = styled_df.apply(
            highlight_vs_benchmark,
            subset=[col],
            benchmark_row=benchmark_row_data,
            axis=0
        )

    # Highlight fund name column for benchmark row
    def highlight_benchmark_name(s):
        return ['background-color: #dbeafe; font-weight: bold' if val.startswith('🔷') else ''
                for val in s]

    styled_df = styled_df.apply(highlight_benchmark_name, subset=['Fund Name'], axis=0)

    return styled_df

def create_correlation_heatmap(returns_dict, benchmark_returns, benchmark_name):
    """Create correlation heatmap showing correlations between all funds and benchmark

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark

    Returns:
        Plotly figure
    """
    import pandas as pd
    import plotly.graph_objects as go

    def resample_to_monthly(returns):
        """Resample daily returns to monthly returns"""
        return returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)

    # Create DataFrame with all returns (monthly)
    returns_data = {}

    # Add all funds
    for fund_name, returns in returns_dict.items():
        monthly_returns = resample_to_monthly(returns)
        # Create display name (remove code after |)
        if '|' in fund_name:
            display_name = fund_name.split('|')[0].strip()
        else:
            display_name = fund_name
        returns_data[display_name] = monthly_returns

    # Add benchmark
    benchmark_monthly = resample_to_monthly(benchmark_returns)
    returns_data[f"🔷 {benchmark_name}"] = benchmark_monthly

    # Create DataFrame and align dates
    returns_df = pd.DataFrame(returns_data)

    # Calculate correlation matrix
    corr_matrix = returns_df.corr()

    # Create custom 4-color scale for maximum distinction between correlation levels
    custom_colorscale = [
        [0.0, '#d73027'],   # Red (low correlation)
        [0.33, '#fc8d59'],  # Orange
        [0.67, '#fee08b'],  # Yellow
        [1.0, '#1a9850']    # Green (high correlation)
    ]

    # Create heatmap with custom colorscale for better distinction of high correlations
    fig = go.Figure(data=go.Heatmap(
        z=corr_matrix.values,
        x=corr_matrix.columns,
        y=corr_matrix.index,
        colorscale=custom_colorscale,
        text=corr_matrix.values,
        texttemplate='%{text:.2f}',
        textfont={"size": 10},
        colorbar=dict(
            title=dict(text="Correlation", side="right"),
            tickmode="auto",
            nticks=6
        ),
        hovertemplate='<b>%{x}</b> vs <b>%{y}</b><br>Correlation: %{z:.3f}<extra></extra>'
    ))

    # Calculate appropriate height based on number of funds
    num_funds = len(corr_matrix)
    height = max(500, min(900, num_funds * 40))

    fig.update_layout(
        title=dict(
            text="Monthly Returns Correlation Matrix",
            font=dict(size=16, weight='bold')
        ),
        xaxis=dict(
            title='',
            tickangle=-45,
            side='bottom'
        ),
        yaxis=dict(
            title='',
            autorange='reversed'  # Top to bottom matches left to right
        ),
        height=height,
        width=height,  # Square aspect ratio
        margin=dict(l=200, r=100, t=100, b=200),
        template='plotly_white'
    )

    return fig

def create_cagr_distribution(metrics_df, benchmark_cagr):
    """Create density curve showing CAGR distribution

    Args:
        metrics_df: DataFrame with fund metrics (must have 'CAGR' column)
        benchmark_cagr: Benchmark CAGR value (as decimal, e.g., 0.15 for 15%)

    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    from scipy import stats

    # Convert CAGR from decimal to percentage
    cagr_values = metrics_df['CAGR'].values * 100
    benchmark_cagr_pct = benchmark_cagr * 100
    median_cagr = np.median(cagr_values)

    # Create KDE (density curve)
    cagr_array = np.array(cagr_values)
    kde = stats.gaussian_kde(cagr_array)
    x_range = np.linspace(cagr_array.min() - 2, cagr_array.max() + 2, 200)
    density = kde(x_range)

    fig = go.Figure()

    # Add density curve
    fig.add_trace(go.Scatter(
        x=x_range,
        y=density,
        mode='lines',
        fill='tozeroy',
        line=dict(color='#3b82f6', width=2),
        fillcolor='rgba(59, 130, 246, 0.2)',
        name='Distribution',
        hovertemplate='CAGR: %{x:.1f}%<extra></extra>'
    ))

    # Add median line
    fig.add_vline(
        x=median_cagr,
        line_dash="dash",
        line_color="#D4AF37",
        line_width=2,
        annotation=dict(
            text=f"Median: {median_cagr:.1f}%",
            textangle=0,
            font=dict(size=9, color='#D4AF37'),
            yanchor='top'
        )
    )

    # Add benchmark line
    fig.add_vline(
        x=benchmark_cagr_pct,
        line_dash="dot",
        line_color="#ef4444",
        line_width=2,
        annotation=dict(
            text=f"Benchmark: {benchmark_cagr_pct:.1f}%",
            textangle=0,
            font=dict(size=9, color='#ef4444'),
            yanchor='bottom'
        )
    )

    fig.update_layout(
        title=dict(text="CAGR Distribution", font=dict(size=13, weight='bold', color='#334155')),
        height=140,
        margin=dict(l=15, r=15, t=35, b=35),
        template='plotly_white',
        showlegend=False,
        xaxis=dict(
            showticklabels=True,
            title='',
            showgrid=False
        ),
        yaxis=dict(
            showticklabels=False,
            title='',
            showgrid=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_annual_returns_distribution(returns_dict, benchmark_returns, start_date, end_date):
    """Create density curve of annual returns distribution

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        start_date: Start date for analysis
        end_date: End date for analysis

    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    from scipy import stats

    # Get all years in the range
    all_years = list(range(start_date.year, end_date.year + 1))

    # Collect all annual returns from all funds
    all_annual_returns = []

    for fund_name, returns in returns_dict.items():
        annual_returns = returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
        for year_date in annual_returns.index:
            year = year_date.year
            if year in all_years:
                ret = annual_returns[year_date]
                if not pd.isna(ret):
                    all_annual_returns.append(ret)

    # Add benchmark annual returns
    benchmark_annual = benchmark_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
    benchmark_annual_values = []
    for year_date in benchmark_annual.index:
        year = year_date.year
        if year in all_years:
            ret = benchmark_annual[year_date]
            if not pd.isna(ret):
                all_annual_returns.append(ret)
                benchmark_annual_values.append(ret)

    # Calculate statistics
    median_return = np.median(all_annual_returns)
    benchmark_median = np.median(benchmark_annual_values) if benchmark_annual_values else median_return

    # Create KDE (density curve)
    all_annual_returns_array = np.array(all_annual_returns)
    kde = stats.gaussian_kde(all_annual_returns_array)
    x_range = np.linspace(all_annual_returns_array.min() - 5, all_annual_returns_array.max() + 5, 200)
    density = kde(x_range)

    fig = go.Figure()

    # Add density curve
    fig.add_trace(go.Scatter(
        x=x_range,
        y=density,
        mode='lines',
        fill='tozeroy',
        line=dict(color='#3b82f6', width=2),
        fillcolor='rgba(59, 130, 246, 0.2)',
        name='Distribution',
        hovertemplate='Return: %{x:.1f}%<extra></extra>'
    ))

    # Add median line
    fig.add_vline(
        x=median_return,
        line_dash="dash",
        line_color="#D4AF37",
        line_width=2,
        annotation=dict(
            text=f"Median: {median_return:.1f}%",
            textangle=0,
            font=dict(size=10, color='#D4AF37'),
            yanchor='top'
        )
    )

    # Add benchmark line
    fig.add_vline(
        x=benchmark_median,
        line_dash="dot",
        line_color="#ef4444",
        line_width=2,
        annotation=dict(
            text=f"Benchmark: {benchmark_median:.1f}%",
            textangle=0,
            font=dict(size=10, color='#ef4444'),
            yanchor='bottom'
        )
    )

    fig.update_layout(
        title=dict(text="Annual Returns Distribution", font=dict(size=13, weight='bold', color='#334155')),
        height=140,
        margin=dict(l=15, r=15, t=35, b=35),
        template='plotly_white',
        showlegend=False,
        xaxis=dict(
            showticklabels=True,
            title='',
            showgrid=False
        ),
        yaxis=dict(
            showticklabels=False,
            title='',
            showgrid=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_volatility_distribution(returns_dict, benchmark_returns, start_date, end_date, risk_free_rate=0.0249):
    """Create density curve of annual volatility distribution

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        start_date: Start date for analysis
        end_date: End date for analysis
        risk_free_rate: Risk-free rate for calculations

    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    from scipy import stats

    TRADING_DAYS = 252

    # Get all years in the range
    all_years = list(range(start_date.year, end_date.year + 1))

    # Collect all annual volatilities from all funds
    all_volatilities = []

    for fund_name, returns in returns_dict.items():
        for year in all_years:
            # Get returns for this year
            year_returns = returns[returns.index.year == year]
            if len(year_returns) > 20:  # At least 20 trading days
                annual_vol = year_returns.std() * np.sqrt(TRADING_DAYS) * 100
                if not pd.isna(annual_vol):
                    all_volatilities.append(annual_vol)

    # Calculate benchmark annual volatilities
    benchmark_volatilities = []
    for year in all_years:
        year_returns = benchmark_returns[benchmark_returns.index.year == year]
        if len(year_returns) > 20:
            annual_vol = year_returns.std() * np.sqrt(TRADING_DAYS) * 100
            if not pd.isna(annual_vol):
                all_volatilities.append(annual_vol)
                benchmark_volatilities.append(annual_vol)

    if not all_volatilities:
        # Return empty figure if no data
        return go.Figure()

    # Calculate statistics
    median_vol = np.median(all_volatilities)
    benchmark_median_vol = np.median(benchmark_volatilities) if benchmark_volatilities else median_vol

    # Create KDE (density curve)
    all_vols_array = np.array(all_volatilities)
    kde = stats.gaussian_kde(all_vols_array)
    x_range = np.linspace(max(0, all_vols_array.min() - 2), all_vols_array.max() + 2, 200)
    density = kde(x_range)

    fig = go.Figure()

    # Add density curve
    fig.add_trace(go.Scatter(
        x=x_range,
        y=density,
        mode='lines',
        fill='tozeroy',
        line=dict(color='#8b5cf6', width=2),
        fillcolor='rgba(139, 92, 246, 0.2)',
        name='Distribution',
        hovertemplate='Volatility: %{x:.1f}%<extra></extra>'
    ))

    # Add median line
    fig.add_vline(
        x=median_vol,
        line_dash="dash",
        line_color="#D4AF37",
        line_width=2,
        annotation=dict(
            text=f"Median: {median_vol:.1f}%",
            textangle=0,
            font=dict(size=9, color='#D4AF37'),
            yanchor='top'
        )
    )

    # Add benchmark line
    fig.add_vline(
        x=benchmark_median_vol,
        line_dash="dot",
        line_color="#ef4444",
        line_width=2,
        annotation=dict(
            text=f"Benchmark: {benchmark_median_vol:.1f}%",
            textangle=0,
            font=dict(size=9, color='#ef4444'),
            yanchor='bottom'
        )
    )

    fig.update_layout(
        title=dict(text="Volatility Distribution", font=dict(size=13, weight='bold', color='#334155')),
        height=140,
        margin=dict(l=15, r=15, t=35, b=35),
        template='plotly_white',
        showlegend=False,
        xaxis=dict(
            showticklabels=True,
            title='',
            showgrid=False
        ),
        yaxis=dict(
            showticklabels=False,
            title='',
            showgrid=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_sharpe_distribution(returns_dict, benchmark_returns, start_date, end_date, risk_free_rate=0.0249):
    """Create density curve of annual Sharpe ratio distribution

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        start_date: Start date for analysis
        end_date: End date for analysis
        risk_free_rate: Risk-free rate for calculations

    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    from scipy import stats

    TRADING_DAYS = 252

    # Get all years in the range
    all_years = list(range(start_date.year, end_date.year + 1))

    # Collect all annual Sharpe ratios from all funds
    all_sharpes = []

    for fund_name, returns in returns_dict.items():
        for year in all_years:
            # Get returns for this year
            year_returns = returns[returns.index.year == year]
            if len(year_returns) > 20:  # At least 20 trading days
                annual_return = year_returns.mean() * TRADING_DAYS
                annual_vol = year_returns.std() * np.sqrt(TRADING_DAYS)
                if annual_vol > 0 and not pd.isna(annual_return):
                    sharpe = (annual_return - risk_free_rate) / annual_vol
                    all_sharpes.append(sharpe)

    # Calculate benchmark annual Sharpe ratios
    benchmark_sharpes = []
    for year in all_years:
        year_returns = benchmark_returns[benchmark_returns.index.year == year]
        if len(year_returns) > 20:
            annual_return = year_returns.mean() * TRADING_DAYS
            annual_vol = year_returns.std() * np.sqrt(TRADING_DAYS)
            if annual_vol > 0 and not pd.isna(annual_return):
                sharpe = (annual_return - risk_free_rate) / annual_vol
                all_sharpes.append(sharpe)
                benchmark_sharpes.append(sharpe)

    if not all_sharpes:
        # Return empty figure if no data
        return go.Figure()

    # Calculate statistics
    median_sharpe = np.median(all_sharpes)
    benchmark_median_sharpe = np.median(benchmark_sharpes) if benchmark_sharpes else median_sharpe

    # Create KDE (density curve)
    all_sharpes_array = np.array(all_sharpes)
    kde = stats.gaussian_kde(all_sharpes_array)
    x_range = np.linspace(all_sharpes_array.min() - 0.5, all_sharpes_array.max() + 0.5, 200)
    density = kde(x_range)

    fig = go.Figure()

    # Add density curve
    fig.add_trace(go.Scatter(
        x=x_range,
        y=density,
        mode='lines',
        fill='tozeroy',
        line=dict(color='#1E3A5F', width=2),
        fillcolor='rgba(245, 158, 11, 0.2)',
        name='Distribution',
        hovertemplate='Sharpe: %{x:.2f}<extra></extra>'
    ))

    # Add median line
    fig.add_vline(
        x=median_sharpe,
        line_dash="dash",
        line_color="#D4AF37",
        line_width=2,
        annotation=dict(
            text=f"Median: {median_sharpe:.2f}",
            textangle=0,
            font=dict(size=9, color='#D4AF37'),
            yanchor='top'
        )
    )

    # Add benchmark line
    fig.add_vline(
        x=benchmark_median_sharpe,
        line_dash="dot",
        line_color="#ef4444",
        line_width=2,
        annotation=dict(
            text=f"Benchmark: {benchmark_median_sharpe:.2f}",
            textangle=0,
            font=dict(size=9, color='#ef4444'),
            yanchor='bottom'
        )
    )

    fig.update_layout(
        title=dict(text="Sharpe Ratio Distribution", font=dict(size=13, weight='bold', color='#334155')),
        height=140,
        margin=dict(l=15, r=15, t=35, b=35),
        template='plotly_white',
        showlegend=False,
        xaxis=dict(
            showticklabels=True,
            title='',
            showgrid=False
        ),
        yaxis=dict(
            showticklabels=False,
            title='',
            showgrid=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_max_drawdown_distribution(returns_dict, benchmark_returns):
    """Create density curve showing max drawdown distribution

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns

    Returns:
        Plotly figure
    """
    import plotly.graph_objects as go
    from scipy import stats

    # Calculate max drawdown for each fund
    max_drawdowns = []
    for fund_name, returns in returns_dict.items():
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_dd = drawdown.min() * 100  # Convert to percentage
        max_drawdowns.append(max_dd)

    # Calculate benchmark max drawdown and find the year it occurred
    bench_cumulative = (1 + benchmark_returns).cumprod()
    bench_running_max = bench_cumulative.expanding().max()
    bench_drawdown = (bench_cumulative - bench_running_max) / bench_running_max
    bench_max_dd = bench_drawdown.min() * 100
    bench_max_dd_date = bench_drawdown.idxmin()
    bench_max_dd_year = bench_max_dd_date.year if hasattr(bench_max_dd_date, 'year') else 'N/A'

    max_drawdowns.append(bench_max_dd)
    median_dd = np.median(max_drawdowns)

    # Create KDE (density curve)
    dd_array = np.array(max_drawdowns)
    kde = stats.gaussian_kde(dd_array)
    x_range = np.linspace(dd_array.min() - 2, dd_array.max() + 2, 200)
    density = kde(x_range)

    fig = go.Figure()

    # Add density curve
    fig.add_trace(go.Scatter(
        x=x_range,
        y=density,
        mode='lines',
        fill='tozeroy',
        line=dict(color='#ef4444', width=2),
        fillcolor='rgba(239, 68, 68, 0.2)',
        name='Distribution',
        hovertemplate='Max DD: %{x:.1f}%<extra></extra>'
    ))

    # Add median line
    fig.add_vline(
        x=median_dd,
        line_dash="dash",
        line_color="#D4AF37",
        line_width=2,
        annotation=dict(
            text=f"Median: {median_dd:.1f}%",
            textangle=0,
            font=dict(size=9, color='#D4AF37'),
            yanchor='top'
        )
    )

    # Add benchmark line with year annotation
    fig.add_vline(
        x=bench_max_dd,
        line_dash="dot",
        line_color="#ef4444",
        line_width=2,
        annotation=dict(
            text=f"Benchmark: {bench_max_dd:.1f}% ({bench_max_dd_year})",
            textangle=0,
            font=dict(size=9, color='#ef4444'),
            yanchor='bottom'
        )
    )

    fig.update_layout(
        title=dict(text="Max Drawdown Distribution", font=dict(size=13, weight='bold', color='#334155')),
        height=140,
        margin=dict(l=15, r=15, t=35, b=35),
        template='plotly_white',
        showlegend=False,
        xaxis=dict(
            showticklabels=True,
            title='',
            showgrid=False
        ),
        yaxis=dict(
            showticklabels=False,
            title='',
            showgrid=False
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig

def create_bubble_scatter_chart(metrics_df, x_metric, y_metric, size_metric, fund_name_col='Fund',
                                 benchmark_x=None, benchmark_y=None):
    """Create bubble scatter chart with customizable metrics

    Args:
        metrics_df: DataFrame with fund metrics (including fund name column)
        x_metric: Column name for X-axis
        y_metric: Column name for Y-axis
        size_metric: Column name for bubble size
        fund_name_col: Name of column containing fund names
        benchmark_x: Benchmark value for X-axis (adds vertical reference line)
        benchmark_y: Benchmark value for Y-axis (adds horizontal reference line)

    Returns:
        Plotly figure
    """
    # Prepare data
    df = metrics_df.copy()

    # Handle percentage metrics - convert to numeric if needed
    for col in [x_metric, y_metric, size_metric]:
        if df[col].dtype == 'object':
            # Remove % signs and convert
            df[col] = pd.to_numeric(df[col].astype(str).str.rstrip('%'), errors='coerce')

    # Remove rows with NaN in key metrics
    df = df.dropna(subset=[x_metric, y_metric, size_metric])

    # Normalize size metric for bubble sizing (scale 5-50)
    size_values = df[size_metric].values
    if size_values.max() != size_values.min():
        normalized_sizes = 5 + 45 * (size_values - size_values.min()) / (size_values.max() - size_values.min())
    else:
        normalized_sizes = [25] * len(size_values)

    # Create color scale based on fund names
    unique_funds = df[fund_name_col].unique()
    color_palette = [
        '#1E3A5F', '#ef4444', '#D4AF37', '#8b5cf6', '#ec4899',
        '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6'
    ]
    color_map = {fund: color_palette[i % len(color_palette)] for i, fund in enumerate(unique_funds)}
    colors = df[fund_name_col].map(color_map)

    # Create hover text with all metrics
    hover_texts = []
    for _, row in df.iterrows():
        text = f"<b>{row[fund_name_col]}</b><br>"
        text += f"{x_metric}: {row[x_metric]:.2f}<br>"
        text += f"{y_metric}: {row[y_metric]:.2f}<br>"
        text += f"{size_metric}: {row[size_metric]:.2f}"
        hover_texts.append(text)

    fig = go.Figure()

    # Add scatter points
    fig.add_trace(go.Scatter(
        x=df[x_metric],
        y=df[y_metric],
        mode='markers',
        marker=dict(
            size=normalized_sizes,
            color=colors,
            line=dict(width=1, color='white'),
            opacity=0.7
        ),
        text=hover_texts,
        hovertemplate='%{text}<extra></extra>',
        showlegend=False
    ))

    # Add fund name annotations for clarity (optional, for top performers)
    if len(df) <= 15:  # Only annotate if not too many funds
        for _, row in df.iterrows():
            fig.add_annotation(
                x=row[x_metric],
                y=row[y_metric],
                text=row[fund_name_col][:20],  # Truncate long names
                showarrow=False,
                font=dict(size=8),
                opacity=0.6,
                yshift=10
            )

    # Add benchmark reference lines if provided
    if benchmark_x is not None:
        # Vertical line for X-axis benchmark
        fig.add_vline(
            x=benchmark_x,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text="Benchmark",
            annotation_position="top"
        )

    if benchmark_y is not None:
        # Horizontal line for Y-axis benchmark
        fig.add_hline(
            y=benchmark_y,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text="Benchmark",
            annotation_position="right"
        )

    fig.update_layout(
        title=dict(
            text=f"Fund Comparison: {x_metric} vs {y_metric} (Size: {size_metric})",
            font=dict(size=18, weight='bold')
        ),
        xaxis_title=x_metric,
        yaxis_title=y_metric,
        height=600,
        template='plotly_white',
        hovermode='closest',
        xaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray'),
        yaxis=dict(showgrid=True, gridwidth=1, gridcolor='lightgray')
    )

    return fig

def create_performance_ranking_grid(returns_dict, benchmark_returns, benchmark_name,
                                     start_date, end_date, risk_free_rate=0.0249,
                                     ranking_mode='annual'):
    """Create performance ranking grid showing fund rankings by year

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark
        start_date: Start date for analysis (can be date or Timestamp)
        end_date: End date for analysis (can be date or Timestamp)
        risk_free_rate: Risk-free rate for Sharpe calculation
        ranking_mode: 'annual' (rank by year) or 'cumulative' (rank by cumulative performance)

    Returns:
        Plotly figure
    """
    import pandas as pd
    import numpy as np
    import plotly.graph_objects as go
    from src.metrics import calculate_sharpe_ratio, calculate_max_drawdown, calculate_cagr

    # Convert dates to Timestamps to ensure compatibility
    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    # Get all unique years in the date range (including incomplete years like current year)
    years = list(range(start_date.year, end_date.year + 1))

    # Create display names by stripping IDs (everything after "|")
    display_names = {}
    for fund_name in returns_dict.keys():
        if '|' in fund_name:
            display_name = fund_name.split('|')[0].strip()
        else:
            display_name = fund_name
        display_names[fund_name] = display_name

    # Calculate metrics for each fund for each year
    fund_year_data = []

    for fund_name, returns in returns_dict.items():
        for year in years:
            year_start = pd.Timestamp(f"{year}-01-01")
            year_end = pd.Timestamp(f"{year}-12-31")

            if ranking_mode == 'annual':
                # Annual mode: metrics for just this year
                year_returns = returns[(returns.index >= year_start) & (returns.index <= year_end)]
            else:
                # Cumulative mode: metrics from start_date to end of this year
                year_returns = returns[(returns.index >= start_date) & (returns.index <= year_end)]

            if len(year_returns) > 20:  # Need minimum data points
                # Calculate annual CAGR
                total_return = (1 + year_returns).prod() - 1
                if ranking_mode == 'annual':
                    years_period = len(year_returns) / 252
                else:
                    years_period = (year_end - pd.Timestamp(start_date)).days / 365.25

                if years_period > 0:
                    cagr = ((1 + total_return) ** (1 / years_period) - 1) * 100
                else:
                    continue

                # Calculate other metrics
                volatility = year_returns.std() * np.sqrt(252) * 100
                sharpe = calculate_sharpe_ratio(year_returns, risk_free_rate)
                max_dd = calculate_max_drawdown(year_returns) * 100

                # Calculate annual return (total return for the period, not annualized)
                annual_return = total_return * 100

                fund_year_data.append({
                    'Fund': fund_name,
                    'Year': year,
                    'CAGR': cagr,
                    'Annual Return': annual_return,
                    'Sharpe': sharpe,
                    'Volatility': volatility,
                    'Max DD': max_dd
                })

    # Add benchmark data
    benchmark_full_name = f"🔷 {benchmark_name}"
    display_names[benchmark_full_name] = benchmark_name  # Add benchmark to display_names

    for year in years:
        year_start = pd.Timestamp(f"{year}-01-01")
        year_end = pd.Timestamp(f"{year}-12-31")

        if ranking_mode == 'annual':
            year_returns = benchmark_returns[(benchmark_returns.index >= year_start) & (benchmark_returns.index <= year_end)]
        else:
            year_returns = benchmark_returns[(benchmark_returns.index >= start_date) & (benchmark_returns.index <= year_end)]

        if len(year_returns) > 20:
            total_return = (1 + year_returns).prod() - 1
            if ranking_mode == 'annual':
                years_period = len(year_returns) / 252
            else:
                years_period = (year_end - pd.Timestamp(start_date)).days / 365.25

            if years_period > 0:
                cagr = ((1 + total_return) ** (1 / years_period) - 1) * 100
                volatility = year_returns.std() * np.sqrt(252) * 100
                sharpe = calculate_sharpe_ratio(year_returns, risk_free_rate)
                max_dd = calculate_max_drawdown(year_returns) * 100

                # Calculate annual return (total return for the period, not annualized)
                annual_return = total_return * 100

                fund_year_data.append({
                    'Fund': benchmark_full_name,
                    'Year': year,
                    'CAGR': cagr,
                    'Annual Return': annual_return,
                    'Sharpe': sharpe,
                    'Volatility': volatility,
                    'Max DD': max_dd
                })

    df = pd.DataFrame(fund_year_data)

    if df.empty:
        # Return empty figure with message
        fig = go.Figure()
        fig.add_annotation(
            text="Insufficient data for ranking grid",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(size=16)
        )
        return fig

    # Rank funds by CAGR for each year (break ties by fund name for consistency)
    df['Rank'] = df.groupby('Year')['CAGR'].rank(ascending=False, method='first').astype(int)

    # Calculate average rank for each fund across all years
    avg_ranks = df.groupby('Fund')['Rank'].mean()

    # Sort funds by average rank (best performers first)
    fund_order = avg_ranks.sort_values().index.tolist()

    # Create pivot for heatmap (Fund x Year -> CAGR for coloring)
    pivot_cagr = df.pivot(index='Fund', columns='Year', values='CAGR')

    # Reorder rows by average rank (best performers at top)
    pivot_cagr = pivot_cagr.reindex(fund_order)

    # Create annotations with rank and metrics for each fund
    annotations = []

    for fund_name in pivot_cagr.index:
        for year in pivot_cagr.columns:
            # Get fund data for this fund and year
            fund_data = df[(df['Fund'] == fund_name) & (df['Year'] == year)]

            if not fund_data.empty:
                row = fund_data.iloc[0]

                # Check if this is a benchmark
                is_benchmark = fund_name.startswith('🔷')

                # Create multi-line annotation (showing Rank first, then metrics)
                text = f"<b>Rank: {row['Rank']:.0f}</b><br>" \
                       f"Ann Ret: {row['Annual Return']:.1f}%<br>" \
                       f"CAGR: {row['CAGR']:.1f}%<br>" \
                       f"SR: {row['Sharpe']:.2f} | DD: {row['Max DD']:.1f}%<br>" \
                       f"Vol: {row['Volatility']:.1f}%"

                # Emphasize benchmark with different styling
                if is_benchmark:
                    annotations.append(
                        dict(
                            x=year,
                            y=fund_name,
                            text=text,
                            showarrow=False,
                            font=dict(size=9, color='#1e40af', family='Arial Black'),  # Bold blue font
                            bgcolor='#fef3c7',  # Light yellow background
                            bordercolor='#1E3A5F',  # Orange border
                            borderwidth=2,
                            borderpad=4,
                            xref='x',
                            yref='y'
                        )
                    )
                else:
                    annotations.append(
                        dict(
                            x=year,
                            y=fund_name,
                            text=text,
                            showarrow=False,
                            font=dict(size=9, color='black'),
                            xref='x',
                            yref='y'
                        )
                    )

    # Create heatmap with transparent color scale and borders
    fig = go.Figure(data=go.Heatmap(
        z=pivot_cagr.values,
        x=pivot_cagr.columns,
        y=pivot_cagr.index,
        colorscale=[
            [0, 'rgba(220, 38, 38, 0.4)'],      # Red for low CAGR (40% opacity)
            [0.5, 'rgba(234, 179, 8, 0.35)'],   # Yellow for medium (35% opacity)
            [1, 'rgba(34, 197, 94, 0.5)']       # Green for high CAGR (50% opacity)
        ],
        zmid=0,  # Center colorscale at 0
        text=pivot_cagr.values,
        hovertemplate='Year: %{x}<br>Fund: %{y}<br>CAGR: %{z:.2f}%<extra></extra>',
        colorbar=dict(
            title=dict(text="CAGR (%)", side="right"),
            tickmode="linear",
            tick0=pivot_cagr.min().min(),
            dtick=(pivot_cagr.max().max() - pivot_cagr.min().min()) / 5
        ),
        xgap=1,  # Horizontal gap between cells (reduced for more cell space)
        ygap=1   # Vertical gap between cells (reduced for more cell space)
    ))

    # Add annotations
    fig.update_layout(annotations=annotations)

    # Update layout
    mode_text = "Annual Performance" if ranking_mode == 'annual' else "Cumulative Performance from Start"

    # Function to wrap long text labels
    def wrap_label(text, width=40):
        """Wrap text at specified character width"""
        if len(text) <= width:
            return text
        words = text.split()
        lines = []
        current_line = []
        current_length = 0

        for word in words:
            if current_length + len(word) + 1 <= width:
                current_line.append(word)
                current_length += len(word) + 1
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_length = len(word)

        if current_line:
            lines.append(' '.join(current_line))

        return '<br>'.join(lines)

    # Create clean Y-axis labels with wrapping (fund names without IDs)
    yaxis_labels = [wrap_label(display_names[fn]) for fn in pivot_cagr.index]

    fig.update_layout(
        title=dict(
            text=f"Performance Ranking Grid - {mode_text} (Sorted by Avg Rank)",
            font=dict(size=18, weight='bold')
        ),
        xaxis_title="Year",
        yaxis_title="Fund Name",
        height=max(600, len(pivot_cagr.index) * 80),  # Dynamic height based on number of funds (larger cells)
        margin=dict(l=250, r=50, t=100, b=50),  # Increased left margin for wrapped labels
        template='plotly_white',
        xaxis=dict(
            side='top',
            dtick=1,
            showgrid=True,
            gridwidth=2,
            gridcolor='white'
        ),
        yaxis=dict(
            autorange='reversed',  # Best performers (lowest avg rank) at top
            tickmode='array',
            tickvals=list(range(len(pivot_cagr.index))),
            ticktext=yaxis_labels,
            showgrid=True,
            gridwidth=2,
            gridcolor='white'
        )
    )

    return fig

def create_rolling_metric_chart(returns_dict, benchmark_returns, benchmark_name,
                                  metric_type, window, risk_free_rate=0.0249, window_label=None, selected_funds=None):
    """Create rolling metric chart for multiple funds with monthly resolution

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark
        metric_type: "Return", "Volatility", "Sharpe", or "Drawdown"
        window: Rolling window size in days (will be converted to months)
        risk_free_rate: Risk-free rate for Sharpe calculation
        window_label: Optional custom label for window (e.g., "1 Year", "3 Years")
        selected_funds: List of fund names to highlight with color (others shown in grayscale)

    Returns:
        Plotly figure
    """
    MONTHS_PER_YEAR = 12
    fig = go.Figure()

    # Convert window from days to months (approximate: 21 trading days per month)
    window_months = int(window / 21)

    # Color palette
    colors = [
        '#1E3A5F', '#ef4444', '#D4AF37', '#8b5cf6', '#ec4899',
        '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6'
    ]

    # Grayscale color for unselected funds
    grayscale_color = '#999999'

    def resample_to_monthly(returns):
        """Resample daily returns to monthly returns"""
        # Use 'ME' (Month End) frequency and calculate compound return for each month
        return returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)

    def calculate_rolling_metric(returns, metric_type, window_months):
        """Calculate rolling metric based on type using monthly data"""
        if metric_type == "Return":
            # Annualized rolling return
            return returns.rolling(window_months).apply(lambda x: (1 + x).prod() - 1) * (MONTHS_PER_YEAR / window_months) * 100
        elif metric_type == "Volatility":
            # Annualized rolling volatility
            return returns.rolling(window_months).std() * np.sqrt(MONTHS_PER_YEAR) * 100
        elif metric_type == "Sharpe":
            # Rolling Sharpe ratio
            rolling_mean = returns.rolling(window_months).mean() * MONTHS_PER_YEAR
            rolling_std = returns.rolling(window_months).std() * np.sqrt(MONTHS_PER_YEAR)
            return (rolling_mean - risk_free_rate) / rolling_std
        elif metric_type == "Drawdown":
            # Rolling max drawdown
            rolling_dd = []
            for i in range(len(returns)):
                if i < window_months:
                    rolling_dd.append(np.nan)
                else:
                    window_returns = returns.iloc[i-window_months:i]
                    cum_returns = (1 + window_returns).cumprod()
                    running_max = cum_returns.expanding().max()
                    dd = ((cum_returns - running_max) / running_max * 100).min()
                    rolling_dd.append(dd)
            return pd.Series(rolling_dd, index=returns.index)
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")

    # Plot each fund
    for idx, (fund_name, returns) in enumerate(returns_dict.items()):
        # Resample to monthly
        monthly_returns = resample_to_monthly(returns)
        metric_values = calculate_rolling_metric(monthly_returns, metric_type, window_months)

        # Drop NaN values to avoid showing initial period with insufficient data
        metric_values = metric_values.dropna()

        # Determine styling based on selection
        if selected_funds is None:
            # No selection mode: use colors for all (backward compatibility)
            color = colors[idx % len(colors)]
            opacity = 0.7
            width = 1.5
        elif fund_name in selected_funds:
            # Selected: use color palette
            color = colors[idx % len(colors)]
            opacity = 0.8  # Slightly more opaque when selected
            width = 2.0    # Slightly thicker
        else:
            # Not selected: grayscale
            color = grayscale_color
            opacity = 0.3  # More transparent
            width = 1.0    # Thinner

        fig.add_trace(go.Scatter(
            x=metric_values.index,
            y=metric_values,
            name=fund_name,
            line=dict(color=color, width=width),
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>',
            opacity=opacity
        ))

    # Add benchmark
    monthly_benchmark = resample_to_monthly(benchmark_returns)
    benchmark_metric = calculate_rolling_metric(monthly_benchmark, metric_type, window_months)

    # Drop NaN values for benchmark as well
    benchmark_metric = benchmark_metric.dropna()

    fig.add_trace(go.Scatter(
        x=benchmark_metric.index,
        y=benchmark_metric,
        name=f"🔷 {benchmark_name}",
        line=dict(color='#94A3B8', width=3, dash='dash'),
        hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>'
    ))

    # Determine Y-axis label and title
    y_labels = {
        "Return": "Annualized Return (%)",
        "Volatility": "Annualized Volatility (%)",
        "Sharpe": "Sharpe Ratio",
        "Drawdown": "Max Drawdown (%)"
    }

    # Determine window label
    if window_label:
        period_text = window_label
    else:
        # Default labels based on common windows
        if window == 252:
            period_text = "1 Year"
        elif window == 756:
            period_text = "3 Years"
        elif window == 1260:
            period_text = "5 Years"
        else:
            period_text = f"{window} days"

    fig.update_layout(
        title=dict(
            text=f"Rolling {metric_type} ({period_text})",
            font=dict(size=18, weight='bold')
        ),
        xaxis_title="Date",
        yaxis_title=y_labels.get(metric_type, metric_type),
        yaxis=dict(side='right'),
        hovermode='closest',
        height=500,
        template='plotly_white',
        showlegend=False
    )

    return fig


def create_distribution_chart(data_df, value_column, category_column, 
                              title, xlabel, order_by='median', 
                              add_zero_line=True, decimal_places=2):
    """
    Create an interactive distribution chart with KDE curves for each category.
    
    Parameters:
    -----------
    data_df : pandas.DataFrame
        The dataframe containing the data
    value_column : str
        Column name containing the values to plot
    category_column : str
        Column name containing the categories
    title : str
        Main title for the chart
    xlabel : str
        Label for x-axis
    order_by : str, default='median'
        How to order categories: 'median', 'mean', or provide a list of categories
    add_zero_line : bool, default=True
        Whether to add a vertical line at x=0
    decimal_places : int, default=2
        Number of decimal places for statistics
        
    Returns:
    --------
    plotly.graph_objects.Figure
        The interactive Plotly figure
    """
    
    # Get category order
    if isinstance(order_by, list):
        category_order = order_by
    elif order_by == 'median':
        category_order = data_df.groupby(category_column)[value_column].median().sort_values(ascending=False).index
    elif order_by == 'mean':
        category_order = data_df.groupby(category_column)[value_column].mean().sort_values(ascending=False).index
    else:
        category_order = data_df[category_column].unique()
    
    # Create subplots
    fig = make_subplots(
        rows=len(category_order), 
        cols=1,
        subplot_titles=[f'<b>{cat}</b>' for cat in category_order],
        vertical_spacing=0.01,
        shared_xaxes=True
    )
    
    # Create a chart for each category
    for idx, category in enumerate(category_order):
        cat_data = data_df[data_df[category_column] == category][value_column].dropna()
        
        if len(cat_data) < 2:
            continue
        
        # Calculate statistics
        mean_val = cat_data.mean()
        median_val = cat_data.median()
        std_val = cat_data.std()
        count = len(cat_data)
        min_val = cat_data.min()
        max_val = cat_data.max()
        
        # Calculate KDE
        try:
            kde = stats.gaussian_kde(cat_data)
            x_range = np.linspace(cat_data.min() - abs(cat_data.min())*0.1, 
                                 cat_data.max() + abs(cat_data.max())*0.1, 300)
            kde_values = kde(x_range)
        except:
            # Fallback if KDE fails (e.g., all same values)
            x_range = np.linspace(cat_data.min(), cat_data.max(), 100)
            kde_values = np.zeros_like(x_range)
        
        # Add KDE curve
        fig.add_trace(
            go.Scatter(
                x=x_range,
                y=kde_values,
                name=category,
                mode='lines',
                line=dict(color='steelblue', width=3),
                fill='tozeroy',
                fillcolor='rgba(70, 130, 180, 0.3)',
                showlegend=False,
                hovertemplate=f'{xlabel}: %{{x:.{decimal_places}f}}<br>Density: %{{y:.4f}}<extra></extra>'
            ),
            row=idx+1, 
            col=1
        )
        
        # Add mean line
        fig.add_vline(
            x=mean_val, 
            line=dict(color='red', dash='dash', width=2),
            row=idx+1, 
            col=1
        )
        
        # Add median line
        fig.add_vline(
            x=median_val, 
            line=dict(color='green', dash='dash', width=2),
            row=idx+1, 
            col=1
        )
        
        # Add zero line if requested
        if add_zero_line:
            fig.add_vline(
                x=0, 
                line=dict(color='black', width=1),
                opacity=0.3,
                row=idx+1, 
                col=1
            )
        
        # Add annotation box with statistics
        annotation_text = (
            f'<b>Statistics (n={count})</b><br>'
            f'Mean: {mean_val:.{decimal_places}f}<br>'
            f'Median: {median_val:.{decimal_places}f}<br>'
            f'Std Dev: {std_val:.{decimal_places}f}<br>'
            f'Range: [{min_val:.{decimal_places}f}, {max_val:.{decimal_places}f}]'
        )
        
        xref_str = f'x{idx+1} domain' if idx > 0 else 'x domain'
        yref_str = f'y{idx+1} domain' if idx > 0 else 'y domain'
        
        fig.add_annotation(
            text=annotation_text,
            xref=xref_str,
            yref=yref_str,
            x=0.98,
            y=0.98,
            xanchor='right',
            yanchor='top',
            showarrow=False,
            bgcolor='rgba(255, 255, 255, 0.9)',
            bordercolor='black',
            borderwidth=1,
            font=dict(size=9),
            align='left'
        )
        
        # Update axes
        fig.update_xaxes(
            title_text=xlabel if idx == len(category_order)-1 else '',
            row=idx+1, 
            col=1,
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=0.5
        )
        
        fig.update_yaxes(
            title_text='Density',
            row=idx+1, 
            col=1,
            showgrid=True,
            gridcolor='lightgray',
            gridwidth=0.5,
            range=[0, kde_values.max() * 1.1] if kde_values.max() > 0 else [0, 1]
        )
    
    # Update overall layout
    fig.update_layout(
        title=dict(
            text=f'<b>{title}</b><br><sub>Ordered by {order_by.capitalize()}</sub>',
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        height=len(category_order) * 300,
        showlegend=False,
        template='plotly_white',
        hovermode='x unified'
    )
    
    return fig


def create_return_distribution_chart(equity_df, order_by='median'):
    """
    Convenience function specifically for return distributions.
    
    Parameters:
    -----------
    equity_df : pandas.DataFrame
        Dataframe with columns: scheme_category_level2, log_return (or pct_return)
    order_by : str or list
        How to order categories
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    # Convert log returns to percentage if needed
    if 'pct_return' not in equity_df.columns and 'log_return' in equity_df.columns:
        equity_df = equity_df.copy()
        equity_df['pct_return'] = (np.exp(equity_df['log_return']) - 1) * 100
    
    return create_distribution_chart(
        data_df=equity_df,
        value_column='pct_return',
        category_column='scheme_category_level2',
        title='Annual Return Distributions by Equity Scheme Category',
        xlabel='Annual Return (%)',
        order_by=order_by,
        add_zero_line=True,
        decimal_places=1
    )


def create_return_box_plot_chart(equity_df, order_by='median'):
    """
    Create vertical box plots showing annual return distributions by equity scheme category.

    Parameters:
    -----------
    equity_df : pandas.DataFrame
        Dataframe with columns: scheme_category_level2, log_return
    order_by : str or list, default='median'
        How to order categories: 'median', 'mean', or provide list of categories

    Returns:
    --------
    tuple
        (plotly.graph_objects.Figure, list):
        - Figure: Interactive Plotly box plot figure
        - category_order: List of category names in display order
    """
    # Convert log returns to percentage if needed
    if 'pct_return' not in equity_df.columns and 'log_return' in equity_df.columns:
        equity_df = equity_df.copy()
        equity_df['pct_return'] = (np.exp(equity_df['log_return']) - 1) * 100

    # Calculate statistics for ordering
    category_stats = equity_df.groupby('scheme_category_level2')['pct_return'].agg([
        ('median', 'median'),
        ('mean', 'mean'),
        ('count', 'count')
    ]).reset_index()

    # Determine category order
    if isinstance(order_by, list):
        category_order = order_by
    elif order_by == 'median':
        category_order = category_stats.sort_values('median', ascending=False)['scheme_category_level2'].tolist()
    elif order_by == 'mean':
        category_order = category_stats.sort_values('mean', ascending=False)['scheme_category_level2'].tolist()
    else:
        category_order = category_stats['scheme_category_level2'].tolist()

    # Create figure
    fig = go.Figure()

    # Add box plot for each category
    for category in category_order:
        category_data = equity_df[equity_df['scheme_category_level2'] == category]
        n_funds = len(category_data)

        fig.add_trace(go.Box(
            y=category_data['pct_return'],
            x=[category] * len(category_data),
            name=category,
            marker=dict(
                color='#64748b',
                opacity=0.6,
                outliercolor='#ef4444',
                line=dict(width=0)
            ),
            line=dict(color='#334155', width=1.5),
            fillcolor='rgba(100, 116, 139, 0.25)',
            boxmean=True,  # Show mean as dashed line
            boxpoints='outliers',  # Show outliers only
            showlegend=False,
            hovertemplate=(
                '<b>%{fullData.name}</b><br>' +
                'Return: %{y:.0f}%<br>' +
                f'N: {n_funds}<br>' +
                '<extra></extra>'
            )
        ))

    # Add zero reference line
    fig.add_hline(
        y=0,
        line=dict(color='#d1d5db', width=1),
        opacity=0.8
    )

    # Update layout
    fig.update_layout(
        title=dict(
            text='<b>Annual Return Distributions by Equity Scheme Category</b><br>' +
                 '<sub>Ordered by Median Return</sub>',
            font=dict(size=18),
            x=0.5,
            xanchor='center'
        ),
        xaxis_title='Scheme Category',
        yaxis_title='Annual Return (%)',
        height=700,
        template='plotly_white',
        hovermode='closest',
        showlegend=False,
        xaxis=dict(
            showgrid=False,
            categoryorder='array',
            categoryarray=category_order,  # Explicit ordering
            tickangle=-45
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='#e5e7eb',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='#9ca3af'
        ),
        margin=dict(l=80, r=50, t=100, b=150)  # Extra bottom margin for angled labels
    )

    return fig, category_order


def create_metric_distribution_chart(metrics_df, metric_name, order_by='median'):
    """
    Convenience function for creating metric distribution charts.
    
    Parameters:
    -----------
    metrics_df : pandas.DataFrame
        Dataframe with columns: category, and metric columns
    metric_name : str
        One of: 'annual_volatility', 'sharpe_ratio', 'max_drawdown'
    order_by : str or list
        How to order categories
        
    Returns:
    --------
    plotly.graph_objects.Figure
    """
    
    metric_configs = {
        'annual_volatility': {
            'title': 'Annual Volatility Distribution by Equity Scheme Category',
            'xlabel': 'Annual Volatility (%)',
            'add_zero_line': False,
            'decimal_places': 2
        },
        'sharpe_ratio': {
            'title': 'Sharpe Ratio Distribution by Equity Scheme Category',
            'xlabel': 'Sharpe Ratio (Risk-free rate: 6%)',
            'add_zero_line': True,
            'decimal_places': 2
        },
        'max_drawdown': {
            'title': 'Maximum Drawdown Distribution by Equity Scheme Category',
            'xlabel': 'Maximum Drawdown (%)',
            'add_zero_line': True,
            'decimal_places': 2
        }
    }
    
    if metric_name not in metric_configs:
        raise ValueError(f"metric_name must be one of {list(metric_configs.keys())}")
    
    config = metric_configs[metric_name]
    
    return create_distribution_chart(
        data_df=metrics_df,
        value_column=metric_name,
        category_column='category',
        title=config['title'],
        xlabel=config['xlabel'],
        order_by=order_by,
        add_zero_line=config['add_zero_line'],
        decimal_places=config['decimal_places']
    )


def create_monthly_returns_scatter(strategy_monthly_returns, benchmark_monthly_returns,
                                   strategy_name, benchmark_name,
                                   comparison_monthly_returns=None, comparison_name=None):
    """Create scatter plot of monthly returns: fund vs benchmark with trendlines

    Shows relationship between benchmark and fund monthly returns with:
    - Scatter points for each month
    - Linear trendline (beta relationship)
    - Optional comparison fund overlay

    Args:
        strategy_monthly_returns: pd.Series with monthly fund returns (decimal format)
        benchmark_monthly_returns: pd.Series with monthly benchmark returns (decimal format)
        strategy_name: str, name of strategy fund
        benchmark_name: str, name of benchmark
        comparison_monthly_returns: pd.Series, optional comparison fund monthly returns
        comparison_name: str, optional name of comparison fund

    Returns:
        plotly.graph_objects.Figure
    """
    import plotly.graph_objects as go
    import numpy as np

    # Align series to matching dates
    aligned_fund, aligned_bench = strategy_monthly_returns.align(
        benchmark_monthly_returns, join='inner'
    )

    # Convert to percentage for display
    bench_pct = aligned_bench.values * 100
    fund_pct = aligned_fund.values * 100
    dates = aligned_fund.index

    # Create figure
    fig = go.Figure()

    # Add main fund scatter points
    fig.add_trace(go.Scatter(
        x=bench_pct,
        y=fund_pct,
        mode='markers',
        marker=dict(
            size=8,
            color='#1E3A5F',  # Orange for main fund
            line=dict(width=1, color='white'),
            opacity=0.7
        ),
        text=[f"Date: {d.strftime('%b %Y')}<br>Benchmark: {b:.2f}%<br>{strategy_name}: {f:.2f}%"
              for d, b, f in zip(dates, bench_pct, fund_pct)],
        hovertemplate='%{text}<extra></extra>',
        name=strategy_name,
        showlegend=True
    ))

    # Add main fund trendline
    if len(fund_pct) > 1:
        z = np.polyfit(bench_pct, fund_pct, 1)
        p = np.poly1d(z)
        trendline_x = np.linspace(bench_pct.min(), bench_pct.max(), 100)
        trendline_y = p(trendline_x)

        fig.add_trace(go.Scatter(
            x=trendline_x,
            y=trendline_y,
            mode='lines',
            name=f'{strategy_name} Trendline',
            line=dict(color='#1E3A5F', width=2, dash='dash'),
            showlegend=False,  # Hide from legend (same color as dots)
            hoverinfo='skip'
        ))

    # Calculate initial min/max for Y=X reference line
    min_val = min(bench_pct.min(), fund_pct.min())
    max_val = max(bench_pct.max(), fund_pct.max())

    # Add comparison fund if provided
    if comparison_monthly_returns is not None and comparison_name is not None:
        aligned_comp, aligned_bench_comp = comparison_monthly_returns.align(
            benchmark_monthly_returns, join='inner'
        )

        comp_pct = aligned_comp.values * 100
        bench_comp_pct = aligned_bench_comp.values * 100
        dates_comp = aligned_comp.index

        # Comparison scatter points
        fig.add_trace(go.Scatter(
            x=bench_comp_pct,
            y=comp_pct,
            mode='markers',
            marker=dict(
                size=8,
                color='#D4AF37',  # Green for comparison fund
                line=dict(width=1, color='white'),
                opacity=0.7
            ),
            text=[f"Date: {d.strftime('%b %Y')}<br>Benchmark: {b:.2f}%<br>{comparison_name}: {c:.2f}%"
                  for d, b, c in zip(dates_comp, bench_comp_pct, comp_pct)],
            hovertemplate='%{text}<extra></extra>',
            name=comparison_name,
            showlegend=True
        ))

        # Comparison trendline
        if len(comp_pct) > 1:
            z_comp = np.polyfit(bench_comp_pct, comp_pct, 1)
            p_comp = np.poly1d(z_comp)
            trendline_x_comp = np.linspace(bench_comp_pct.min(), bench_comp_pct.max(), 100)
            trendline_y_comp = p_comp(trendline_x_comp)

            fig.add_trace(go.Scatter(
                x=trendline_x_comp,
                y=trendline_y_comp,
                mode='lines',
                name=f'{comparison_name} Trendline',
                line=dict(color='#D4AF37', width=2, dash='dash'),
                showlegend=False,  # Hide from legend (same color as dots)
                hoverinfo='skip'
            ))

        # Update Y=X reference line to include comparison fund range
        min_val = min(min_val, comp_pct.min())
        max_val = max(max_val, comp_pct.max())

    # Add Y=X reference line (after calculating final min/max)
    fig.add_trace(go.Scatter(
        x=[min_val, max_val],
        y=[min_val, max_val],
        mode='lines',
        name='Y=X Reference',
        line=dict(color='gray', width=1, dash='dot'),
        showlegend=True,
        hoverinfo='skip'
    ))

    # Update layout
    fig.update_layout(
        title=dict(
            text="Monthly Returns: Fund vs Benchmark",
            font=dict(size=16, weight='bold')
        ),
        xaxis_title=f"{benchmark_name} Monthly Returns (%)",
        yaxis_title="Fund Monthly Returns (%)",
        height=500,
        template='plotly_white',
        hovermode='closest',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='black'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.25,
            xanchor="center",
            x=0.5,
            bgcolor="rgba(255,255,255,0.8)"
        )
    )

    return fig


def create_comparison_metrics_table(strategy_metrics, benchmark_name,
                                    comparison_metrics=None, comparison_name=None):
    """Create table showing R², Correlation, Beta for fund vs benchmark

    Args:
        strategy_metrics: dict with strategy fund metrics (includes R², Correlation, Beta)
        benchmark_name: str, name of benchmark
        comparison_metrics: dict, optional comparison fund metrics
        comparison_name: str, optional comparison fund name

    Returns:
        pd.DataFrame formatted for display
    """
    import pandas as pd

    # Metrics to display
    metric_keys = ['R²', 'Correlation', 'Beta']

    data = []
    for metric in metric_keys:
        row = {
            'Metric': metric,
            'Main Fund': f"{strategy_metrics.get(metric, 0):.4f}"
        }

        if comparison_metrics is not None:
            row['Comp Fund'] = f"{comparison_metrics.get(metric, 0):.4f}"

        data.append(row)

    df = pd.DataFrame(data)
    return df