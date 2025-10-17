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
    """Create equity curves for multiple funds in a category with monthly resolution

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

    def resample_to_monthly(returns):
        """Resample daily returns to monthly returns"""
        # Use 'ME' (Month End) frequency and calculate compound return for each month
        return returns.resample('ME').apply(lambda x: (1 + x).prod() - 1)

    # Add each fund's equity curve
    for idx, (fund_name, returns) in enumerate(returns_dict.items()):
        # Resample to monthly
        monthly_returns = resample_to_monthly(returns)
        # Calculate cumulative returns on monthly data
        cum_returns = (1 + monthly_returns).cumprod()
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
    monthly_benchmark = resample_to_monthly(benchmark_returns)
    benchmark_cum = (1 + monthly_benchmark).cumprod()
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
        '#f59e0b', '#ef4444', '#10b981', '#8b5cf6', '#ec4899',
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
            color='#000000',
            line=dict(width=2, color='red'),
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

def create_performance_ranking_grid(returns_dict, benchmark_returns, benchmark_name,
                                     start_date, end_date, risk_free_rate=0.0249,
                                     ranking_mode='annual', max_funds=20):
    """Create performance ranking grid showing fund rankings by year

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark
        start_date: Start date for analysis (can be date or Timestamp)
        end_date: End date for analysis (can be date or Timestamp)
        risk_free_rate: Risk-free rate for Sharpe calculation
        ranking_mode: 'annual' (rank by year) or 'cumulative' (rank by cumulative performance)
        max_funds: Maximum number of funds to display (top N)

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

    # Get all unique years in the date range
    years = pd.date_range(start=start_date, end=end_date, freq='YE').year.unique()

    if len(years) == 0:
        # Handle single year case
        years = [pd.Timestamp(end_date).year]

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

                fund_year_data.append({
                    'Fund': fund_name,
                    'Year': year,
                    'CAGR': cagr,
                    'Sharpe': sharpe,
                    'Volatility': volatility,
                    'Max DD': max_dd
                })

    # Add benchmark data
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

                fund_year_data.append({
                    'Fund': f"🔷 {benchmark_name}",
                    'Year': year,
                    'CAGR': cagr,
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

    # Limit to top N funds (based on average rank)
    top_funds = df.groupby('Fund')['Rank'].mean().nsmallest(max_funds).index
    df = df[df['Fund'].isin(top_funds)]

    # Get unique ranks that appear in the filtered data
    unique_ranks = sorted(df['Rank'].unique())

    # Create a mapping for consecutive rank display
    rank_mapping = {old_rank: new_rank for new_rank, old_rank in enumerate(unique_ranks, start=1)}
    df['Display_Rank'] = df['Rank'].map(rank_mapping)

    # Create pivot for heatmap (Display_Rank x Year -> CAGR for coloring)
    pivot_cagr = df.pivot(index='Display_Rank', columns='Year', values='CAGR')

    # Sort by rank
    pivot_cagr = pivot_cagr.sort_index()

    # Create annotations with fund name and metrics
    annotations = []

    for display_rank in pivot_cagr.index:
        for year in pivot_cagr.columns:
            # Get fund data for this display rank and year
            fund_data = df[(df['Display_Rank'] == display_rank) & (df['Year'] == year)]

            if not fund_data.empty:
                row = fund_data.iloc[0]
                fund_name = row['Fund']

                # Truncate long fund names
                display_name = fund_name.split(' - ')[0] if ' - ' in fund_name else fund_name
                if len(display_name) > 20:
                    display_name = display_name[:17] + '...'

                # Create multi-line annotation
                text = f"<b>{display_name}</b><br>" \
                       f"CAGR: {row['CAGR']:.1f}%<br>" \
                       f"SR: {row['Sharpe']:.2f} | DD: {row['Max DD']:.1f}%<br>" \
                       f"Vol: {row['Volatility']:.1f}%"

                annotations.append(
                    dict(
                        x=year,
                        y=display_rank,
                        text=text,
                        showarrow=False,
                        font=dict(size=9, color='white' if abs(row['CAGR']) > 10 else 'black'),
                        xref='x',
                        yref='y'
                    )
                )

    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=pivot_cagr.values,
        x=pivot_cagr.columns,
        y=pivot_cagr.index,
        colorscale=[
            [0, '#ef4444'],      # Red for low CAGR
            [0.5, '#fbbf24'],    # Yellow for medium
            [1, '#10b981']       # Green for high CAGR
        ],
        zmid=0,  # Center colorscale at 0
        text=pivot_cagr.values,
        hovertemplate='Year: %{x}<br>Rank: %{y}<br>CAGR: %{z:.2f}%<extra></extra>',
        colorbar=dict(
            title=dict(text="CAGR (%)", side="right"),
            tickmode="linear",
            tick0=pivot_cagr.min().min(),
            dtick=(pivot_cagr.max().max() - pivot_cagr.min().min()) / 5
        )
    ))

    # Add annotations
    fig.update_layout(annotations=annotations)

    # Update layout
    mode_text = "Annual Performance" if ranking_mode == 'annual' else "Cumulative Performance from Start"

    fig.update_layout(
        title=dict(
            text=f"Performance Ranking Grid - {mode_text}",
            font=dict(size=18, weight='bold')
        ),
        xaxis_title="Year",
        yaxis_title="Rank (1 = Best)",
        height=max(400, len(pivot_cagr.index) * 80),  # Dynamic height based on number of funds
        template='plotly_white',
        xaxis=dict(
            side='top',
            dtick=1,
            showgrid=True,
            gridwidth=2,
            gridcolor='white'
        ),
        yaxis=dict(
            autorange='reversed',  # Rank 1 at top
            dtick=1,
            showgrid=True,
            gridwidth=2,
            gridcolor='white'
        )
    )

    return fig

def create_rolling_metric_chart(returns_dict, benchmark_returns, benchmark_name,
                                  metric_type, window, risk_free_rate=0.0249, window_label=None):
    """Create rolling metric chart for multiple funds with monthly resolution

    Args:
        returns_dict: Dictionary {fund_name: returns_series}
        benchmark_returns: Series with benchmark returns
        benchmark_name: String name of benchmark
        metric_type: "Return", "Volatility", "Sharpe", or "Drawdown"
        window: Rolling window size in days (will be converted to months)
        risk_free_rate: Risk-free rate for Sharpe calculation
        window_label: Optional custom label for window (e.g., "1 Year", "3 Years")

    Returns:
        Plotly figure
    """
    MONTHS_PER_YEAR = 12
    fig = go.Figure()

    # Convert window from days to months (approximate: 21 trading days per month)
    window_months = int(window / 21)

    # Color palette
    colors = [
        '#f59e0b', '#ef4444', '#10b981', '#8b5cf6', '#ec4899',
        '#06b6d4', '#f97316', '#84cc16', '#6366f1', '#14b8a6'
    ]

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
    monthly_benchmark = resample_to_monthly(benchmark_returns)
    benchmark_metric = calculate_rolling_metric(monthly_benchmark, metric_type, window_months)

    # Drop NaN values for benchmark as well
    benchmark_metric = benchmark_metric.dropna()

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