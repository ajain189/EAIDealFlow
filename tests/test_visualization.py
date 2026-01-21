"""
Tests for visualization module.
Tests chart rendering with confidence bands and valuation calculations.
"""

import pandas as pd
import numpy as np
import plotly.graph_objects as go

from modules.visualization import (
    create_market_chart,
    calculate_valuation_range,
    get_chart_config,
    create_simple_chart_for_pdf
)


def create_sample_peers_df(num_peers=10):
    """Create a sample peers DataFrame for testing."""
    np.random.seed(42)
    return pd.DataFrame({
        'revenue': np.random.uniform(1_000_000, 10_000_000, num_peers),
        'ebitda_margin': np.random.uniform(5, 25, num_peers),
        'multiple': np.random.uniform(1.0, 3.0, num_peers)
    })


class TestCreateMarketChart:
    """Tests for create_market_chart function."""

    def test_returns_plotly_figure(self):
        """Test that function returns a Plotly Figure object."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)
        assert isinstance(fig, go.Figure)

    def test_chart_contains_target_company(self):
        """Test that target company is plotted on chart."""
        peers_df = create_sample_peers_df()
        target_name = "Test Company"
        target_revenue = 5_000_000
        target_margin = 15.0

        fig = create_market_chart(
            peers_df, target_name, target_revenue, target_margin
        )

        # Find target trace
        target_trace = None
        for trace in fig.data:
            if trace.name == target_name:
                target_trace = trace
                break

        assert target_trace is not None
        assert target_trace.x[0] == target_revenue
        assert target_trace.y[0] == target_margin

    def test_chart_contains_peer_companies(self):
        """Test that peer companies are plotted."""
        peers_df = create_sample_peers_df(num_peers=5)
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        # Find peers trace
        peers_trace = None
        for trace in fig.data:
            if trace.name == 'Market Peers':
                peers_trace = trace
                break

        assert peers_trace is not None
        assert len(peers_trace.x) == 5

    def test_chart_has_dark_theme(self):
        """Test that chart uses dark theme."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        # Check for dark theme characteristics
        assert fig.layout.paper_bgcolor == '#0E1117'
        assert fig.layout.font.color == 'white'


class TestConfidenceBand:
    """Tests for confidence band (IQR shaded region) rendering."""

    def test_confidence_band_shown_by_default(self):
        """Test that confidence band is shown when sufficient data exists."""
        peers_df = create_sample_peers_df(num_peers=10)
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        # Find IQR trace
        iqr_trace = None
        for trace in fig.data:
            if 'IQR' in trace.name:
                iqr_trace = trace
                break

        assert iqr_trace is not None
        assert iqr_trace.fill == 'toself'

    def test_confidence_band_uses_correct_percentiles(self):
        """Test that confidence band uses 25th and 75th percentiles."""
        # Create predictable data
        peers_df = pd.DataFrame({
            'revenue': [1_000_000, 2_000_000, 3_000_000, 4_000_000, 5_000_000],
            'ebitda_margin': [10.0, 12.0, 15.0, 18.0, 20.0],
            'multiple': [1.5, 1.6, 1.7, 1.8, 1.9]
        })

        fig = create_market_chart(peers_df, "Test Company", 3_000_000, 15.0)

        # Find IQR trace
        iqr_trace = None
        for trace in fig.data:
            if 'IQR' in trace.name:
                iqr_trace = trace
                break

        expected_margin_25 = peers_df['ebitda_margin'].quantile(0.25)
        expected_margin_75 = peers_df['ebitda_margin'].quantile(0.75)

        # The y values should contain the percentile boundaries
        y_values = list(iqr_trace.y)
        assert expected_margin_25 in y_values
        assert expected_margin_75 in y_values

    def test_confidence_band_spans_revenue_range(self):
        """Test that confidence band spans the full revenue range."""
        peers_df = pd.DataFrame({
            'revenue': [1_000_000, 5_000_000, 10_000_000],
            'ebitda_margin': [10.0, 15.0, 20.0],
            'multiple': [1.5, 1.7, 1.9]
        })
        # Need at least 4 points for confidence band
        peers_df = pd.concat([peers_df, peers_df], ignore_index=True)

        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        iqr_trace = None
        for trace in fig.data:
            if 'IQR' in trace.name:
                iqr_trace = trace
                break

        x_values = list(iqr_trace.x)
        assert min(x_values) == peers_df['revenue'].min()
        assert max(x_values) == peers_df['revenue'].max()

    def test_confidence_band_not_shown_when_disabled(self):
        """Test that confidence band can be disabled."""
        peers_df = create_sample_peers_df(num_peers=10)
        fig = create_market_chart(
            peers_df, "Test Company", 5_000_000, 15.0,
            show_confidence_band=False
        )

        iqr_trace = None
        for trace in fig.data:
            if 'IQR' in trace.name:
                iqr_trace = trace
                break

        assert iqr_trace is None

    def test_confidence_band_not_shown_with_insufficient_data(self):
        """Test that confidence band is not shown with fewer than 4 peers."""
        peers_df = pd.DataFrame({
            'revenue': [1_000_000, 2_000_000, 3_000_000],
            'ebitda_margin': [10.0, 15.0, 20.0],
            'multiple': [1.5, 1.7, 1.9]
        })

        fig = create_market_chart(peers_df, "Test Company", 2_000_000, 15.0)

        iqr_trace = None
        for trace in fig.data:
            if 'IQR' in trace.name:
                iqr_trace = trace
                break

        assert iqr_trace is None

    def test_confidence_band_with_empty_peers(self):
        """Test chart renders without error when peers DataFrame is empty."""
        cols = ['revenue', 'ebitda_margin', 'multiple']
        peers_df = pd.DataFrame(columns=cols)
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        # Should still render target company
        assert len(fig.data) >= 1

        iqr_trace = None
        for trace in fig.data:
            if 'IQR' in trace.name:
                iqr_trace = trace
                break

        assert iqr_trace is None

    def test_confidence_band_styling(self):
        """Test that confidence band has correct styling."""
        peers_df = create_sample_peers_df(num_peers=10)
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        iqr_trace = None
        for trace in fig.data:
            if 'IQR' in trace.name:
                iqr_trace = trace
                break

        # Check fill color has expected purple tone with transparency
        assert 'rgba' in iqr_trace.fillcolor
        assert '99, 102, 241' in iqr_trace.fillcolor  # Indigo/blurple color

    def test_confidence_band_appears_in_legend(self):
        """Test that confidence band appears in legend."""
        peers_df = create_sample_peers_df(num_peers=10)
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        iqr_trace = None
        for trace in fig.data:
            if 'IQR' in trace.name:
                iqr_trace = trace
                break

        assert iqr_trace.showlegend is True

    def test_confidence_band_with_nan_values(self):
        """Test confidence band handles NaN values in data."""
        peers_df = pd.DataFrame({
            'revenue': [1e6, 2e6, np.nan, 4e6, 5e6, 6e6],
            'ebitda_margin': [10.0, np.nan, 15.0, 18.0, 20.0, 22.0],
            'multiple': [1.5, 1.6, 1.7, np.nan, 1.9, 2.0]
        })

        # Should not raise an error
        fig = create_market_chart(peers_df, "Test Company", 3_000_000, 15.0)
        assert isinstance(fig, go.Figure)


class TestCalculateValuationRange:
    """Tests for calculate_valuation_range function."""

    def test_returns_tuple_of_three(self):
        """Test that function returns tuple of (low, high, median)."""
        peers_df = create_sample_peers_df()
        result = calculate_valuation_range(peers_df, 5_000_000)

        assert isinstance(result, tuple)
        assert len(result) == 3

    def test_valuation_uses_multiples(self):
        """Test that valuation is calculated using multiples."""
        peers_df = pd.DataFrame({
            'multiple': [1.0, 2.0, 3.0, 4.0, 5.0]
        })
        target_revenue = 1_000_000

        result = calculate_valuation_range(peers_df, target_revenue)
        low_val, high_val, median_val = result

        # 25th percentile of [1,2,3,4,5] = 2.0
        # 75th percentile of [1,2,3,4,5] = 4.0
        # Median = 3.0
        assert low_val == target_revenue * 2.0
        assert high_val == target_revenue * 4.0
        assert median_val == target_revenue * 3.0

    def test_empty_dataframe_returns_zeros(self):
        """Test that empty DataFrame returns (0, 0, 0)."""
        peers_df = pd.DataFrame()
        result = calculate_valuation_range(peers_df, 5_000_000)
        assert result == (0, 0, 0)

    def test_missing_multiple_column_returns_zeros(self):
        """Test that missing 'multiple' column returns (0, 0, 0)."""
        peers_df = pd.DataFrame({
            'revenue': [1_000_000, 2_000_000],
            'ebitda_margin': [10.0, 15.0]
        })
        result = calculate_valuation_range(peers_df, 5_000_000)
        assert result == (0, 0, 0)

    def test_all_nan_multiples_returns_zeros(self):
        """Test that all NaN multiples return (0, 0, 0)."""
        peers_df = pd.DataFrame({
            'multiple': [np.nan, np.nan, np.nan]
        })
        result = calculate_valuation_range(peers_df, 5_000_000)
        assert result == (0, 0, 0)

    def test_valuation_scales_with_revenue(self):
        """Test that valuation scales linearly with target revenue."""
        peers_df = pd.DataFrame({
            'multiple': [2.0, 2.0, 2.0, 2.0, 2.0]
        })

        low1, high1, median1 = calculate_valuation_range(peers_df, 1_000_000)
        low2, high2, median2 = calculate_valuation_range(peers_df, 2_000_000)

        assert low2 == low1 * 2
        assert high2 == high1 * 2
        assert median2 == median1 * 2


class TestGetChartConfig:
    """Tests for get_chart_config function."""

    def test_returns_dict(self):
        """Test that function returns a dictionary."""
        config = get_chart_config()
        assert isinstance(config, dict)

    def test_mode_bar_enabled(self):
        """Test that mode bar is displayed."""
        config = get_chart_config()
        assert config['displayModeBar'] is True

    def test_logo_disabled(self):
        """Test that Plotly logo is disabled."""
        config = get_chart_config()
        assert config['displaylogo'] is False

    def test_lasso_removed(self):
        """Test that lasso selection is removed."""
        config = get_chart_config()
        assert 'lasso2d' in config['modeBarButtonsToRemove']

    def test_select_removed(self):
        """Test that box selection is removed."""
        config = get_chart_config()
        assert 'select2d' in config['modeBarButtonsToRemove']

    def test_image_export_options(self):
        """Test that image export is configured."""
        config = get_chart_config()
        assert 'toImageButtonOptions' in config
        assert config['toImageButtonOptions']['format'] == 'png'


class TestCreateSimpleChartForPdf:
    """Tests for create_simple_chart_for_pdf function."""

    def test_returns_plotly_figure(self):
        """Test that function returns a Plotly Figure."""
        peers_df = create_sample_peers_df()
        fig = create_simple_chart_for_pdf(
            peers_df, "Test Company", 5_000_000, 15.0
        )
        assert isinstance(fig, go.Figure)

    def test_uses_white_background(self):
        """Test that PDF chart uses white background for print."""
        peers_df = create_sample_peers_df()
        fig = create_simple_chart_for_pdf(
            peers_df, "Test Company", 5_000_000, 15.0
        )
        assert fig.layout.paper_bgcolor == 'white'

    def test_uses_light_plot_background(self):
        """Test that PDF chart uses light plot background."""
        peers_df = create_sample_peers_df()
        fig = create_simple_chart_for_pdf(
            peers_df, "Test Company", 5_000_000, 15.0
        )
        assert fig.layout.plot_bgcolor == '#f8fafc'

    def test_uses_dark_text(self):
        """Test that PDF chart uses dark text for readability."""
        peers_df = create_sample_peers_df()
        fig = create_simple_chart_for_pdf(
            peers_df, "Test Company", 5_000_000, 15.0
        )
        assert fig.layout.font.color == '#1f2937'

    def test_contains_same_data_as_web_chart(self):
        """Test that PDF chart contains same traces as web chart."""
        peers_df = create_sample_peers_df(num_peers=5)

        web_fig = create_market_chart(
            peers_df, "Test Company", 5_000_000, 15.0
        )
        pdf_fig = create_simple_chart_for_pdf(
            peers_df, "Test Company", 5_000_000, 15.0
        )

        # Same number of traces
        assert len(web_fig.data) == len(pdf_fig.data)

        # Same trace names
        web_names = {trace.name for trace in web_fig.data}
        pdf_names = {trace.name for trace in pdf_fig.data}
        assert web_names == pdf_names


class TestChartInteractivity:
    """Tests for chart interactivity features."""

    def test_drag_mode_is_pan(self):
        """Test that default drag mode is pan."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)
        assert fig.layout.dragmode == 'pan'

    def test_hover_mode_is_closest(self):
        """Test that hover mode is closest point."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)
        assert fig.layout.hovermode == 'closest'

    def test_axes_are_zoomable(self):
        """Test that axes allow zoom/pan (not fixed range)."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)
        # fixedrange should be False for zooming
        assert fig.layout.xaxis.fixedrange is False
        assert fig.layout.yaxis.fixedrange is False


class TestChartLabeling:
    """Tests for chart labels and formatting."""

    def test_x_axis_shows_currency(self):
        """Test that x-axis formats revenue as currency."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)
        assert '$' in fig.layout.xaxis.tickformat

    def test_y_axis_shows_percentage(self):
        """Test that y-axis shows percentage suffix."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)
        assert fig.layout.yaxis.ticksuffix == '%'

    def test_title_includes_peer_count(self):
        """Test that title includes peer count."""
        peers_df = create_sample_peers_df(num_peers=7)
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)
        assert '7' in fig.layout.title.text

    def test_legend_is_horizontal_at_top(self):
        """Test that legend is horizontal and at top."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)
        assert fig.layout.legend.orientation == 'h'
        assert fig.layout.legend.y > 1.0  # Above the plot


class TestTargetMarkerStyling:
    """Tests for target company marker styling."""

    def test_target_marker_is_cyan(self):
        """Test that target company marker is cyan colored."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        target_trace = None
        for trace in fig.data:
            if trace.name == "Test Company":
                target_trace = trace
                break

        assert target_trace.marker.color == '#06b6d4'

    def test_target_marker_is_larger_than_peers(self):
        """Test that target marker is larger than peer markers."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        target_trace = None
        peers_trace = None
        for trace in fig.data:
            if trace.name == "Test Company":
                target_trace = trace
            elif trace.name == "Market Peers":
                peers_trace = trace

        assert target_trace.marker.size > peers_trace.marker.size

    def test_target_has_label(self):
        """Test that target company has text label."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        target_trace = None
        for trace in fig.data:
            if trace.name == "Test Company":
                target_trace = trace
                break

        assert 'markers+text' in target_trace.mode
        assert target_trace.text[0] == "Test Company"


class TestPeerHoverInfo:
    """Tests for peer company hover information."""

    def test_peers_have_hover_text(self):
        """Test that peer points have hover information."""
        peers_df = create_sample_peers_df()
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        peers_trace = None
        for trace in fig.data:
            if trace.name == "Market Peers":
                peers_trace = trace
                break

        assert peers_trace.hovertext is not None
        assert len(peers_trace.hovertext) > 0

    def test_hover_includes_revenue(self):
        """Test that hover text includes revenue."""
        peers_df = create_sample_peers_df(num_peers=1)
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        peers_trace = None
        for trace in fig.data:
            if trace.name == "Market Peers":
                peers_trace = trace
                break

        assert 'Revenue' in peers_trace.hovertext[0]

    def test_hover_includes_margin(self):
        """Test that hover text includes EBITDA margin."""
        peers_df = create_sample_peers_df(num_peers=1)
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        peers_trace = None
        for trace in fig.data:
            if trace.name == "Market Peers":
                peers_trace = trace
                break

        assert 'EBITDA Margin' in peers_trace.hovertext[0]

    def test_hover_includes_multiple_when_available(self):
        """Test that hover text includes multiple when present."""
        peers_df = pd.DataFrame({
            'revenue': [3_000_000],
            'ebitda_margin': [15.0],
            'multiple': [2.5]
        })
        fig = create_market_chart(peers_df, "Test Company", 5_000_000, 15.0)

        peers_trace = None
        for trace in fig.data:
            if trace.name == "Market Peers":
                peers_trace = trace
                break

        assert 'Multiple' in peers_trace.hovertext[0]
        assert '2.50x' in peers_trace.hovertext[0]


class TestRealTimeMarginUpdates:
    """Tests for real-time margin slider chart updates.

    These tests verify that the chart correctly responds to margin changes,
    which is the underlying behavior that enables real-time slider updates.
    """

    def test_chart_updates_target_position_on_margin_change(self):
        """Test that target marker position updates when margin changes."""
        peers_df = create_sample_peers_df()
        target_name = "Test Company"
        target_revenue = 5_000_000

        # Create chart with initial margin
        fig1 = create_market_chart(peers_df, target_name, target_revenue, 10.0)
        # Create chart with updated margin
        fig2 = create_market_chart(peers_df, target_name, target_revenue, 25.0)

        # Find target trace in both figures
        target_y1 = None
        target_y2 = None
        for trace in fig1.data:
            if trace.name == target_name:
                target_y1 = trace.y[0]
                break
        for trace in fig2.data:
            if trace.name == target_name:
                target_y2 = trace.y[0]
                break

        assert target_y1 == 10.0
        assert target_y2 == 25.0
        assert target_y1 != target_y2

    def test_chart_preserves_peers_on_margin_change(self):
        """Test that peer data remains unchanged when margin slider moves."""
        peers_df = create_sample_peers_df(num_peers=5)
        target_name = "Test Company"
        target_revenue = 5_000_000

        # Create charts with different margins
        fig1 = create_market_chart(peers_df, target_name, target_revenue, 10.0)
        fig2 = create_market_chart(peers_df, target_name, target_revenue, 30.0)

        # Find peer traces
        peers1 = None
        peers2 = None
        for trace in fig1.data:
            if trace.name == 'Market Peers':
                peers1 = trace
                break
        for trace in fig2.data:
            if trace.name == 'Market Peers':
                peers2 = trace
                break

        # Peer data should be identical
        assert list(peers1.x) == list(peers2.x)
        assert list(peers1.y) == list(peers2.y)

    def test_chart_preserves_confidence_band_on_margin_change(self):
        """Test that IQR confidence band remains unchanged on margin change."""
        peers_df = create_sample_peers_df(num_peers=10)
        target_name = "Test Company"
        target_revenue = 5_000_000

        fig1 = create_market_chart(peers_df, target_name, target_revenue, 5.0)
        fig2 = create_market_chart(peers_df, target_name, target_revenue, 45.0)

        # Find IQR traces
        iqr1 = None
        iqr2 = None
        for trace in fig1.data:
            if 'IQR' in trace.name:
                iqr1 = trace
                break
        for trace in fig2.data:
            if 'IQR' in trace.name:
                iqr2 = trace
                break

        # IQR band should be identical regardless of target margin
        assert list(iqr1.x) == list(iqr2.x)
        assert list(iqr1.y) == list(iqr2.y)

    def test_margin_slider_range_boundaries(self):
        """Test chart handles margin at slider boundaries (0% and 50%)."""
        peers_df = create_sample_peers_df()
        target_name = "Test Company"
        target_revenue = 5_000_000

        # Test minimum margin (0%)
        fig_min = create_market_chart(peers_df, target_name, target_revenue, 0.0)
        target_min = None
        for trace in fig_min.data:
            if trace.name == target_name:
                target_min = trace
                break
        assert target_min.y[0] == 0.0

        # Test maximum margin (50%)
        fig_max = create_market_chart(peers_df, target_name, target_revenue, 50.0)
        target_max = None
        for trace in fig_max.data:
            if trace.name == target_name:
                target_max = trace
                break
        assert target_max.y[0] == 50.0

    def test_incremental_margin_updates(self):
        """Test chart handles small incremental margin changes (slider step)."""
        peers_df = create_sample_peers_df()
        target_name = "Test Company"
        target_revenue = 5_000_000

        # Simulate slider moving in 0.5% steps
        margins = [15.0, 15.5, 16.0, 16.5, 17.0]
        previous_y = None

        for margin in margins:
            fig = create_market_chart(peers_df, target_name, target_revenue, margin)
            for trace in fig.data:
                if trace.name == target_name:
                    current_y = trace.y[0]
                    assert current_y == margin
                    if previous_y is not None:
                        assert current_y - previous_y == 0.5
                    previous_y = current_y
                    break

    def test_chart_structure_consistent_across_margin_changes(self):
        """Test that chart structure remains consistent across margin changes."""
        peers_df = create_sample_peers_df(num_peers=8)
        target_name = "Test Company"
        target_revenue = 5_000_000

        # Create multiple charts with different margins
        margins = [5.0, 15.0, 25.0, 35.0, 45.0]
        trace_counts = []
        trace_names_sets = []

        for margin in margins:
            fig = create_market_chart(peers_df, target_name, target_revenue, margin)
            trace_counts.append(len(fig.data))
            trace_names_sets.append({trace.name for trace in fig.data})

        # All charts should have same structure
        assert all(count == trace_counts[0] for count in trace_counts)
        assert all(names == trace_names_sets[0] for names in trace_names_sets)
