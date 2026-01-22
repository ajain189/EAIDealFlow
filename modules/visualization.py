import plotly.graph_objects as go
import pandas as pd
import numpy as np

def create_market_chart(
    peers_df: pd.DataFrame,
    target_name: str,
    target_revenue: float,
    target_margin: float,
    show_confidence_band: bool = True
) -> go.Figure:
    """
    Create interactive scatter plot with:
    - Grey dots: peer companies (semi-transparent)
    - Cyan dot: target company (larger, draggable)
    - Shaded IQR confidence band (25th-75th percentile)
    """
    fig = go.Figure()

    # Calculate IQR confidence band if enough data
    if show_confidence_band and len(peers_df) >= 4:
        margin_25 = peers_df['ebitda_margin'].quantile(0.25)
        margin_75 = peers_df['ebitda_margin'].quantile(0.75)
        rev_min = peers_df['revenue'].min()
        rev_max = peers_df['revenue'].max()

        # Add shaded confidence band
        fig.add_trace(go.Scatter(
            x=[rev_min, rev_max, rev_max, rev_min],
            y=[margin_25, margin_25, margin_75, margin_75],
            fill='toself',
            fillcolor='rgba(99, 102, 241, 0.1)',
            line=dict(color='rgba(99, 102, 241, 0.3)', width=1),
            name='IQR Range (25th-75th)',
            hoverinfo='skip'
        ))

    # Peers (ghost dots)
    if not peers_df.empty:
        fig.add_trace(go.Scatter(
            x=peers_df['revenue'],
            y=peers_df['ebitda_margin'],
            mode='markers',
            marker=dict(
                size=10,
                color='rgba(156, 163, 175, 0.4)',
                line=dict(width=1, color='rgba(255, 255, 255, 0.2)')
            ),
            name='Market Peers',
            hovertemplate=(
                '<b>Comparable Deal</b><br>'
                'Revenue: $%{x:,.0f}<br>'
                'EBITDA Margin: %{y:.1f}%<br>'
                '<extra></extra>'
            )
        ))

    # Target (cyan orb) - larger and highlighted
    fig.add_trace(go.Scatter(
        x=[target_revenue],
        y=[target_margin],
        mode='markers+text',
        marker=dict(
            size=20,
            color='#06b6d4',
            line=dict(width=3, color='white'),
            symbol='circle'
        ),
        text=[target_name],
        textposition='top center',
        textfont=dict(color='#06b6d4', size=12),
        name=target_name,
        hovertemplate=(
            f'<b>{target_name}</b><br>'
            'Revenue: $%{x:,.0f}<br>'
            'Est. Margin: %{y:.1f}%<br>'
            '<extra></extra>'
        )
    ))

    # Layout with dark theme
    peer_count = len(peers_df)
    fig.update_layout(
        title=dict(
            text=f'Market Position Analysis<br><sub>Based on {peer_count} comparable transactions</sub>',
            font=dict(size=16, color='white')
        ),
        template='plotly_dark',
        paper_bgcolor='#0E1117',
        plot_bgcolor='rgba(30, 35, 50, 0.5)',
        font=dict(family='Inter, sans-serif', color='white'),
        xaxis=dict(
            title='Revenue ($)',
            tickformat='$,.0f',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showgrid=True
        ),
        yaxis=dict(
            title='EBITDA Margin (%)',
            ticksuffix='%',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showgrid=True
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(0,0,0,0)'
        ),
        hovermode='closest',
        dragmode='pan'  # Enable panning by default
    )

    # Enable zoom and pan
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    return fig

def calculate_valuation_range(peers_df: pd.DataFrame, target_revenue: float) -> tuple:
    """
    Calculate valuation range using Multiple × Revenue.
    Returns (low_val, high_val, median_val).
    """
    if peers_df.empty or 'multiple' not in peers_df.columns:
        return (0, 0, 0)

    multiples = peers_df['multiple'].dropna()
    if len(multiples) == 0:
        return (0, 0, 0)

    low_multiple = multiples.quantile(0.25)
    high_multiple = multiples.quantile(0.75)
    median_multiple = multiples.median()

    return (
        target_revenue * low_multiple,
        target_revenue * high_multiple,
        target_revenue * median_multiple
    )

def get_chart_config() -> dict:
    """Return Plotly chart configuration for optimal display."""
    return {
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'market_position',
            'height': 800,
            'width': 1200,
            'scale': 2
        }
    }
