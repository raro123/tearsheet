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
        title="Cumulative Returns vs Benchmark",
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)",
        hovermode='x unified',
        height=400,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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

    # Add strategy drawdown
    fig.add_trace(go.Scatter(
        x=strategy_drawdown.index,
        y=strategy_drawdown,
        name=strategy_name,
        line=dict(color='#f59e0b', width=2),
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    # Add benchmark drawdown
    fig.add_trace(go.Scatter(
        x=benchmark_drawdown.index,
        y=benchmark_drawdown,
        name=benchmark_name,
        line=dict(color='#3b82f6', width=2),
        hovertemplate='%{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title="Drawdown Comparison",
        xaxis_title="Date",
        yaxis_title="Drawdown (%)",
        hovermode='x unified',
        height=400,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
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
        title="Cumulative Returns (Log Scale)",
        xaxis_title="Date",
        yaxis_title="Growth of $1",
        yaxis_type="log",
        hovermode='x unified',
        height=350,
        template='plotly_white',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )

    return fig

def create_annual_returns_chart(strategy_returns, benchmark_returns, strategy_name, benchmark_name):
    """Create annual returns bar chart with difference subplot"""
    from plotly.subplots import make_subplots

    # Calculate annual returns
    strategy_annual = strategy_returns.resample('Y').apply(lambda x: (1 + x).prod() - 1) * 100
    benchmark_annual = benchmark_returns.resample('Y').apply(lambda x: (1 + x).prod() - 1) * 100

    # Calculate difference
    difference = strategy_annual - benchmark_annual

    # Extract years
    years = strategy_annual.index.year

    # Create subplot with 2 rows
    fig = make_subplots(
        rows=2, cols=1,
        row_heights=[0.7, 0.3],
        vertical_spacing=0.1,
        subplot_titles=("Annual Returns", "Excess Return (Fund - Benchmark)")
    )

    # Add strategy bars
    fig.add_trace(
        go.Bar(
            x=years,
            y=strategy_annual.values,
            name=strategy_name,
            marker_color='#f59e0b',
            hovertemplate='%{y:.2f}%<extra></extra>'
        ),
        row=1, col=1
    )

    # Add benchmark bars
    fig.add_trace(
        go.Bar(
            x=years,
            y=benchmark_annual.values,
            name=benchmark_name,
            marker_color='#3b82f6',
            hovertemplate='%{y:.2f}%<extra></extra>'
        ),
        row=1, col=1
    )

    # Add difference bars (color based on positive/negative)
    colors = ['#10b981' if d > 0 else '#ef4444' for d in difference.values]
    fig.add_trace(
        go.Bar(
            x=years,
            y=difference.values,
            name='Excess Return',
            marker_color=colors,
            hovertemplate='%{y:.2f}%<extra></extra>',
            showlegend=False
        ),
        row=2, col=1
    )

    # Update layout
    fig.update_xaxes(title_text="Year", row=2, col=1)
    fig.update_yaxes(title_text="Return (%)", row=1, col=1)
    fig.update_yaxes(title_text="Difference (%)", row=2, col=1)

    fig.update_layout(
        height=600,
        template='plotly_white',
        barmode='group',
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        hovermode='x unified'
    )

    return fig