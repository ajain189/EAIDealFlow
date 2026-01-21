"""
Visualization module for EAI DealFlow Terminal.
Creates interactive Plotly scatter charts with IQR confidence bands.
"""

import plotly.graph_objects as go
import pandas as pd
from typing import Tuple


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
    - Cyan dot: target company (larger, highlighted)
    - Shaded IQR confidence band (25th-75th percentile)

    Args:
        peers_df: DataFrame of peer companies with 'revenue' and 'ebitda_margin' columns
        target_name: Name of the target company
        target_revenue: Target company revenue
        target_margin: Target company estimated EBITDA margin
        show_confidence_band: Whether to show the IQR shaded region

    Returns:
        Plotly Figure object
    """
    fig = go.Figure()

    # Calculate IQR confidence band if enough data
    if show_confidence_band and not peers_df.empty and len(peers_df) >= 4:
        margins = peers_df['ebitda_margin'].dropna()
        revenues = peers_df['revenue'].dropna()

        if len(margins) >= 4 and len(revenues) >= 2:
            margin_25 = margins.quantile(0.25)
            margin_75 = margins.quantile(0.75)
            rev_min = revenues.min()
            rev_max = revenues.max()

            # Add shaded confidence band
            fig.add_trace(go.Scatter(
                x=[rev_min, rev_max, rev_max, rev_min],
                y=[margin_25, margin_25, margin_75, margin_75],
                fill='toself',
                fillcolor='rgba(99, 102, 241, 0.1)',
                line=dict(color='rgba(99, 102, 241, 0.3)', width=1),
                name='IQR Range (25th-75th)',
                hoverinfo='skip',
                showlegend=True
            ))

    # Peers (ghost dots)
    if not peers_df.empty and 'revenue' in peers_df.columns and 'ebitda_margin' in peers_df.columns:
        peer_data = peers_df.dropna(subset=['revenue', 'ebitda_margin'])

        if not peer_data.empty:
            # Create hover text with available info
            hover_texts = []
            for _, row in peer_data.iterrows():
                text = "<b>Comparable Deal</b><br>"
                text += f"Revenue: ${row['revenue']:,.0f}<br>"
                text += f"EBITDA Margin: {row['ebitda_margin']:.1f}%"
                if 'multiple' in row and pd.notna(row['multiple']):
                    text += f"<br>Multiple: {row['multiple']:.2f}x"
                hover_texts.append(text)

            fig.add_trace(go.Scatter(
                x=peer_data['revenue'],
                y=peer_data['ebitda_margin'],
                mode='markers',
                marker=dict(
                    size=10,
                    color='rgba(156, 163, 175, 0.5)',
                    line=dict(width=1, color='rgba(255, 255, 255, 0.3)')
                ),
                name='Market Peers',
                hovertext=hover_texts,
                hoverinfo='text'
            ))

    # Target (cyan orb) - larger and highlighted
    fig.add_trace(go.Scatter(
        x=[target_revenue],
        y=[target_margin],
        mode='markers+text',
        marker=dict(
            size=22,
            color='#06b6d4',
            line=dict(width=3, color='white'),
            symbol='circle'
        ),
        text=[target_name],
        textposition='top center',
        textfont=dict(color='#06b6d4', size=12, family='Inter'),
        name=target_name,
        hovertemplate=(
            f'<b>{target_name}</b><br>'
            'Revenue: $%{x:,.0f}<br>'
            'Est. Margin: %{y:.1f}%<br>'
            '<extra></extra>'
        )
    ))

    # Layout with dark theme
    peer_count = len(peers_df) if not peers_df.empty else 0
    subtitle = f'Based on {peer_count} comparable transactions'
    fig.update_layout(
        title=dict(
            text=f'Market Position Analysis<br><sub style="color:#9ca3af">{subtitle}</sub>',
            font=dict(size=18, color='white', family='Inter'),
            x=0.5,
            xanchor='center'
        ),
        template='plotly_dark',
        paper_bgcolor='#0E1117',
        plot_bgcolor='rgba(30, 35, 50, 0.5)',
        font=dict(family='Inter, sans-serif', color='white'),
        xaxis=dict(
            title=dict(text='Revenue ($)', font=dict(size=12)),
            tickformat='$,.0f',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showgrid=True,
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text='EBITDA Margin (%)', font=dict(size=12)),
            ticksuffix='%',
            gridcolor='rgba(255, 255, 255, 0.1)',
            showgrid=True,
            zeroline=False
        ),
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1,
            bgcolor='rgba(0,0,0,0)',
            font=dict(size=10)
        ),
        hovermode='closest',
        dragmode='pan',
        margin=dict(l=60, r=40, t=80, b=60)
    )

    # Enable zoom and pan
    fig.update_xaxes(fixedrange=False)
    fig.update_yaxes(fixedrange=False)

    return fig


def calculate_valuation_range(peers_df: pd.DataFrame, target_revenue: float) -> Tuple[float, float, float]:
    """
    Calculate valuation range using Multiple × Revenue.

    Args:
        peers_df: DataFrame with 'multiple' column
        target_revenue: Target company revenue

    Returns:
        Tuple of (low_val, high_val, median_val)
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


def calculate_valuation_range_detailed(
    peers_df: pd.DataFrame,
    target_revenue: float,
    target_ebitda: float = None
) -> dict:
    """
    Calculate detailed valuation range with multiple metrics.

    Provides a comprehensive valuation breakdown including:
    - Min, 25th percentile, median, 75th percentile, and max valuations
    - The multiples used for each calculation
    - Statistics about the peer group used

    Args:
        peers_df: DataFrame with 'multiple' column (and optionally 'ebitda_margin')
        target_revenue: Target company revenue
        target_ebitda: Optional target EBITDA (if None, calculated from margin if available)

    Returns:
        Dictionary containing:
        - 'valuations': dict with min, p25, median, p75, max valuations
        - 'multiples': dict with min, p25, median, p75, max multiples
        - 'peer_count': number of peers with valid multiple data
        - 'method': valuation method used ('ev_revenue_multiple')
        - 'confidence': 'high', 'medium', or 'low' based on peer count
    """
    result = {
        'valuations': {
            'min': 0,
            'p25': 0,
            'median': 0,
            'p75': 0,
            'max': 0
        },
        'multiples': {
            'min': 0,
            'p25': 0,
            'median': 0,
            'p75': 0,
            'max': 0
        },
        'peer_count': 0,
        'method': 'ev_revenue_multiple',
        'confidence': 'low'
    }

    if peers_df.empty or 'multiple' not in peers_df.columns:
        return result

    multiples = peers_df['multiple'].dropna()
    if len(multiples) == 0:
        return result

    peer_count = len(multiples)
    result['peer_count'] = peer_count

    # Calculate confidence level based on peer count
    if peer_count >= 10:
        result['confidence'] = 'high'
    elif peer_count >= 5:
        result['confidence'] = 'medium'
    else:
        result['confidence'] = 'low'

    # Calculate multiple statistics
    result['multiples'] = {
        'min': float(multiples.min()),
        'p25': float(multiples.quantile(0.25)),
        'median': float(multiples.median()),
        'p75': float(multiples.quantile(0.75)),
        'max': float(multiples.max())
    }

    # Calculate valuations using Multiple × Revenue
    result['valuations'] = {
        'min': target_revenue * result['multiples']['min'],
        'p25': target_revenue * result['multiples']['p25'],
        'median': target_revenue * result['multiples']['median'],
        'p75': target_revenue * result['multiples']['p75'],
        'max': target_revenue * result['multiples']['max']
    }

    return result


def get_valuation_summary(detailed_result: dict) -> str:
    """
    Generate a human-readable summary of the valuation range.

    Args:
        detailed_result: Result from calculate_valuation_range_detailed()

    Returns:
        Formatted string summary of the valuation
    """
    if detailed_result['peer_count'] == 0:
        return "Insufficient peer data for valuation"

    vals = detailed_result['valuations']
    mults = detailed_result['multiples']
    conf = detailed_result['confidence']

    confidence_text = {
        'high': 'High confidence',
        'medium': 'Moderate confidence',
        'low': 'Low confidence'
    }.get(conf, 'Unknown confidence')

    summary = (
        f"Valuation Range: ${vals['p25']:,.0f} - ${vals['p75']:,.0f}\n"
        f"Median Valuation: ${vals['median']:,.0f}\n"
        f"Multiple Range: {mults['p25']:.2f}x - {mults['p75']:.2f}x (median: {mults['median']:.2f}x)\n"
        f"Based on {detailed_result['peer_count']} comparable transactions\n"
        f"{confidence_text} ({detailed_result['peer_count']} peers)"
    )

    return summary


def get_chart_config() -> dict:
    """Get Plotly chart display configuration."""
    return {
        'displayModeBar': True,
        'modeBarButtonsToRemove': ['lasso2d', 'select2d'],
        'displaylogo': False,
        'toImageButtonOptions': {
            'format': 'png',
            'filename': 'market_position_chart',
            'height': 600,
            'width': 900,
            'scale': 2
        }
    }


def create_simple_chart_for_pdf(
    peers_df: pd.DataFrame,
    target_name: str,
    target_revenue: float,
    target_margin: float
) -> go.Figure:
    """
    Create a simpler version of the chart optimized for PDF export.
    Uses white background for better print quality.
    """
    fig = create_market_chart(peers_df, target_name, target_revenue, target_margin)

    # Adjust for PDF - lighter theme
    fig.update_layout(
        paper_bgcolor='white',
        plot_bgcolor='#f8fafc',
        font=dict(color='#1f2937'),
        title=dict(font=dict(color='#1f2937')),
        xaxis=dict(
            gridcolor='rgba(0, 0, 0, 0.1)',
            title=dict(font=dict(color='#1f2937')),
            tickfont=dict(color='#1f2937')
        ),
        yaxis=dict(
            gridcolor='rgba(0, 0, 0, 0.1)',
            title=dict(font=dict(color='#1f2937')),
            tickfont=dict(color='#1f2937')
        )
    )

    return fig
