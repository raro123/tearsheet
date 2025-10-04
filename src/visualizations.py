import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_cumulative_returns_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name):
    """Create cumulative returns comparison chart"""
    strategy_cum = (1 + strategy_returns).cumprod()
    benchmark_cum = (1 + benchmark_returns).cumprod()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=strategy_cum.index,
        y=(strategy_cum - 1) * 100,
        name=strategy_name,
        line=dict(color='#f59e0b', width=2),
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=benchmark_cum.index,
        y=(benchmark_cum - 1) * 100,
        name=benchmark_name,
        line=dict(color='#3b82f6', width=2),
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Cumulative Returns vs Benchmark", font=dict(size=18, weight='bold')),
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)",
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
        hovermode='x unified',
        height=300,
        template='plotly_white'
    )

    return fig

def create_drawdown_comparison_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name):
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

    # Add strategy drawdown as area
    fig.add_trace(go.Scatter(
        x=strategy_drawdown.index,
        y=strategy_drawdown,
        name=strategy_name,
        fill='tozeroy',
        line=dict(color='#f59e0b', width=2),
        fillcolor='rgba(245, 158, 11, 0.3)',
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    # Add benchmark drawdown as area
    fig.add_trace(go.Scatter(
        x=benchmark_drawdown.index,
        y=benchmark_drawdown,
        name=benchmark_name,
        fill='tozeroy',
        line=dict(color='#3b82f6', width=2),
        fillcolor='rgba(59, 130, 246, 0.3)',
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Drawdown Comparison", font=dict(size=18, weight='bold')),
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
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
        line=dict(color='#f59e0b', width=2),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=bench_rolling_sharpe.index,
        y=bench_rolling_sharpe,
        name=benchmark_name,
        line=dict(color='#3b82f6', width=2),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=f"Rolling Sharpe Ratio ({window} days)",
        xaxis_title="Date",
        yaxis_title="Sharpe Ratio",
        hovermode='x unified',
        height=300,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

def create_log_returns_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name):
    """Create log-scaled cumulative returns chart"""
    strategy_cum = (1 + strategy_returns).cumprod()
    benchmark_cum = (1 + benchmark_returns).cumprod()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=strategy_cum.index,
        y=strategy_cum,
        name=strategy_name,
        line=dict(color='#f59e0b', width=2),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))
    fig.add_trace(go.Scatter(
        x=benchmark_cum.index,
        y=benchmark_cum,
        name=benchmark_name,
        line=dict(color='#3b82f6', width=2),
        hovertemplate='%{y:.2f}<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Cumulative Returns (Log Scale)", font=dict(size=18, weight='bold')),
        xaxis_title="Date",
        yaxis_title="Growth of $1",
        yaxis_type="log",
        hovermode='x unified',
        height=450,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        margin=dict(b=100)
    )

    return fig

def create_rolling_returns_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name, window=252):
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
        line=dict(color='#f59e0b', width=2),
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    # Add benchmark rolling returns
    fig.add_trace(go.Scatter(
        x=benchmark_rolling.index,
        y=benchmark_rolling,
        name=benchmark_name,
        line=dict(color='#3b82f6', width=2),
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
        hovermode='x unified',
        height=450,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="top", y=-0.2, xanchor="center", x=0.5),
        margin=dict(b=100)
    )

    return fig

def create_annual_returns_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name):
    """Create annual returns bar chart with data labels"""

    # Calculate annual returns
    strategy_annual = strategy_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100
    benchmark_annual = benchmark_returns.resample('YE').apply(lambda x: (1 + x).prod() - 1) * 100

    # Align both series to ensure they have the same years
    strategy_annual, benchmark_annual = strategy_annual.align(benchmark_annual, join='outer', fill_value=0)

    # Extract years
    years = strategy_annual.index.year

    fig = go.Figure()

    # Add strategy bars with labels
    fig.add_trace(
        go.Bar(
            x=years,
            y=strategy_annual.values,
            name=strategy_name,
            marker_color='#f59e0b',
            text=[f"{v:.1f}%" for v in strategy_annual.values],
            textposition='outside',
            hovertemplate='%{y:.2f}%<extra></extra>'
        )
    )

    # Add benchmark bars with labels
    fig.add_trace(
        go.Bar(
            x=years,
            y=benchmark_annual.values,
            name=benchmark_name,
            marker_color='#3b82f6',
            text=[f"{v:.1f}%" for v in benchmark_annual.values],
            textposition='outside',
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