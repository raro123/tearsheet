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

def create_category_equity_curves(returns_dict, benchmark_returns, benchmark_name):
    """Create equity curves for multiple funds in a category

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark

    Returns:
        Plotly figure
    """
    fig = go.Figure()

    # Color palette for funds
    colors = [
        '#f59e0b', '#ef4444', '#10b981', '#8b5cf6', '#ec4899',
        '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6'
    ]

    # Add each fund's equity curve
    for idx, (fund_name, returns) in enumerate(returns_dict.items()):
        cum_returns = (1 + returns).cumprod()
        color = colors[idx % len(colors)]

        fig.add_trace(go.Scatter(
            x=cum_returns.index,
            y=(cum_returns - 1) * 100,
            name=fund_name,
            line=dict(color=color, width=1.5),
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>',
            opacity=0.7
        ))

    # Add benchmark (thicker, distinct line)
    benchmark_cum = (1 + benchmark_returns).cumprod()
    fig.add_trace(go.Scatter(
        x=benchmark_cum.index,
        y=(benchmark_cum - 1) * 100,
        name=f"🔷 {benchmark_name}",
        line=dict(color='#000000', width=3, dash='dash'),
        hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Return: %{y:.2f}%<extra></extra>'
    ))

    fig.update_layout(
        title=dict(text="Category Equity Curves - Cumulative Returns", font=dict(size=18, weight='bold')),
        xaxis_title="Date",
        yaxis_title="Cumulative Return (%)",
        hovermode='closest',
        height=600,
        template='plotly_white',
        showlegend=False
    )

    return fig

def create_annual_returns_bubble_chart(returns_dict, benchmark_returns, benchmark_name, start_date, end_date):
    """Create bubble chart showing annual returns over time with volatility as bubble size

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

    # Color palette
    colors = [
        '#f59e0b', '#ef4444', '#10b981', '#8b5cf6', '#ec4899',
        '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6'
    ]

    fig = go.Figure()

    # Get unique funds (excluding benchmark)
    funds = [f for f in df['Fund'].unique() if not f.startswith('🔷')]

    # Plot each fund
    for idx, fund_name in enumerate(funds):
        fund_data = df[df['Fund'] == fund_name]
        color = colors[idx % len(colors)]

        fig.add_trace(go.Scatter(
            x=fund_data['Year'],
            y=fund_data['Annual Return'],
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
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         'Year: %{x}<br>' +
                         'Return: %{y:.2f}%<br>' +
                         'Volatility: %{marker.size:.2f}%' +
                         '<extra></extra>'
        ))

    # Plot benchmark with distinct style
    benchmark_data = df[df['Type'] == 'Benchmark']
    fig.add_trace(go.Scatter(
        x=benchmark_data['Year'],
        y=benchmark_data['Annual Return'],
        mode='markers',
        name=f"🔷 {benchmark_name}",
        marker=dict(
            size=benchmark_data['Annual Volatility'],
            sizemode='diameter',
            sizeref=2,
            color='#000000',
            line=dict(width=2, color='red'),
            opacity=0.9,
            symbol='diamond'
        ),
        hovertemplate='<b>%{fullData.name}</b><br>' +
                     'Year: %{x}<br>' +
                     'Return: %{y:.2f}%<br>' +
                     'Volatility: %{marker.size:.2f}%' +
                     '<extra></extra>'
    ))

    fig.update_layout(
        title=dict(
            text="Annual Returns by Year (Bubble Size: Annual Volatility)",
            font=dict(size=18, weight='bold')
        ),
        xaxis_title="Year",
        yaxis_title="Annual Return (%)",
        height=600,
        template='plotly_white',
        showlegend=False,
        hovermode='closest',
        xaxis=dict(
            dtick=1,  # Show every year
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray',
            zeroline=True,
            zerolinewidth=2,
            zerolinecolor='gray'
        )
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
        '#f59e0b', '#ef4444', '#10b981', '#8b5cf6', '#ec4899',
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

def create_rolling_metric_chart(returns_dict, benchmark_returns, benchmark_name,
                                  metric_type, window, risk_free_rate=0.0249, window_label=None):
    """Create rolling metric chart for multiple funds

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark
        metric_type: "Return", "Volatility", "Sharpe", or "Drawdown"
        window: Rolling window size in days
        risk_free_rate: Risk-free rate for Sharpe calculation
        window_label: Optional custom label for window (e.g., "1 Year", "3 Years")

    Returns:
        Plotly figure
    """
    TRADING_DAYS = 252
    fig = go.Figure()

    # Color palette
    colors = [
        '#f59e0b', '#ef4444', '#10b981', '#8b5cf6', '#ec4899',
        '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6'
    ]

    def calculate_rolling_metric(returns, metric_type, window):
        """Calculate rolling metric based on type"""
        if metric_type == "Return":
            # Annualized rolling return
            return returns.rolling(window).apply(lambda x: (1 + x).prod() - 1) * (TRADING_DAYS / window) * 100
        elif metric_type == "Volatility":
            # Annualized rolling volatility
            return returns.rolling(window).std() * np.sqrt(TRADING_DAYS) * 100
        elif metric_type == "Sharpe":
            # Rolling Sharpe ratio
            rolling_mean = returns.rolling(window).mean() * TRADING_DAYS
            rolling_std = returns.rolling(window).std() * np.sqrt(TRADING_DAYS)
            return (rolling_mean - risk_free_rate) / rolling_std
        elif metric_type == "Drawdown":
            # Rolling max drawdown
            rolling_dd = []
            for i in range(len(returns)):
                if i < window:
                    rolling_dd.append(np.nan)
                else:
                    window_returns = returns.iloc[i-window:i]
                    cum_returns = (1 + window_returns).cumprod()
                    running_max = cum_returns.expanding().max()
                    dd = ((cum_returns - running_max) / running_max * 100).min()
                    rolling_dd.append(dd)
            return pd.Series(rolling_dd, index=returns.index)
        else:
            raise ValueError(f"Unknown metric type: {metric_type}")

    # Plot each fund
    for idx, (fund_name, returns) in enumerate(returns_dict.items()):
        metric_values = calculate_rolling_metric(returns, metric_type, window)
        color = colors[idx % len(colors)]

        fig.add_trace(go.Scatter(
            x=metric_values.index,
            y=metric_values,
            name=fund_name,
            line=dict(color=color, width=1.5),
            hovertemplate='<b>%{fullData.name}</b><br>Date: %{x}<br>Value: %{y:.2f}<extra></extra>',
            opacity=0.7
        ))

    # Add benchmark
    benchmark_metric = calculate_rolling_metric(benchmark_returns, metric_type, window)
    fig.add_trace(go.Scatter(
        x=benchmark_metric.index,
        y=benchmark_metric,
        name=f"🔷 {benchmark_name}",
        line=dict(color='#000000', width=3, dash='dash'),
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
        hovermode='closest',
        height=500,
        template='plotly_white',
        showlegend=False
    )

    return fig