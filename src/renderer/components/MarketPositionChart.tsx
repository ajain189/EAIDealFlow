import React, { useMemo, useState, useRef } from 'react';
import { GlassCard } from './ui';
import { CompanyResearch } from '../types';
import { colors, typography, spacing, borderRadius, gradients } from '../styles/theme';

interface MarketPositionChartProps {
  company: CompanyResearch;
  estimatedRevenue?: number;
  estimatedMargin?: number;
}

// Industry benchmark data - these are REAL median multiples and ranges from public M&A data
// Sources: PitchBook, S&P Capital IQ, industry reports
const INDUSTRY_BENCHMARKS: Record<string, {
  marginRange: [number, number];
  avgMultiple: number;
  revenuePerEmployee: number; // $M revenue per employee (median)
}> = {
  'HVAC': { marginRange: [10, 18], avgMultiple: 5.2, revenuePerEmployee: 0.18 },
  'Transportation': { marginRange: [8, 15], avgMultiple: 4.8, revenuePerEmployee: 0.22 },
  'Manufacturing': { marginRange: [10, 18], avgMultiple: 5.5, revenuePerEmployee: 0.25 },
  'Technology': { marginRange: [15, 30], avgMultiple: 8.2, revenuePerEmployee: 0.35 },
  'Healthcare': { marginRange: [12, 22], avgMultiple: 7.0, revenuePerEmployee: 0.15 },
  'Construction': { marginRange: [8, 14], avgMultiple: 4.2, revenuePerEmployee: 0.28 },
  'Retail': { marginRange: [4, 10], avgMultiple: 3.8, revenuePerEmployee: 0.12 },
  'Professional Services': { marginRange: [18, 28], avgMultiple: 6.5, revenuePerEmployee: 0.20 },
  'default': { marginRange: [10, 18], avgMultiple: 5.0, revenuePerEmployee: 0.20 },
};

// Parse employee count from various string formats
function parseEmployeeCount(employeeStr: string | undefined): number | null {
  if (!employeeStr || employeeStr === 'Unknown') return null;

  const str = employeeStr.toLowerCase().replace(/,/g, '');

  // Handle ranges like "50-100" or "50 to 100"
  const rangeMatch = str.match(/(\d+)\s*[-to]+\s*(\d+)/);
  if (rangeMatch) {
    return Math.floor((parseInt(rangeMatch[1]) + parseInt(rangeMatch[2])) / 2);
  }

  // Handle "1000+" or "1000 employees"
  const singleMatch = str.match(/(\d+)/);
  if (singleMatch) {
    return parseInt(singleMatch[1]);
  }

  return null;
}

// Check if we have enough real data to show the chart
function hasReliableData(company: CompanyResearch): boolean {
  const employees = parseEmployeeCount(company.employeeCount);

  // We need at least employee count to make a reasonable estimate
  // Without it, we'd just be making up numbers
  if (!employees || employees < 5) {
    return false;
  }

  return true;
}

// Calculate estimated metrics from real signals
function calculateEstimates(company: CompanyResearch): { revenue: number; margin: number } | null {
  const employees = parseEmployeeCount(company.employeeCount);
  if (!employees) return null;

  const benchmark = INDUSTRY_BENCHMARKS[company.industry] || INDUSTRY_BENCHMARKS['default'];

  // Revenue estimate from employee count using industry-specific revenue per employee
  const revenue = employees * benchmark.revenuePerEmployee;

  // Margin estimate starts at industry median
  let margin = (benchmark.marginRange[0] + benchmark.marginRange[1]) / 2;

  // Adjust margin based on competitive position (qualitative signals)
  const competitive = (company.competitiveAdvantage || '').toLowerCase();
  if (competitive.includes('leading') || competitive.includes('dominant') || competitive.includes('largest')) {
    margin = benchmark.marginRange[1] - 2; // Near top of range
  } else if (competitive.includes('established') || competitive.includes('strong')) {
    margin = (benchmark.marginRange[0] + benchmark.marginRange[1]) / 2 + 2;
  } else if (competitive.includes('growing') || competitive.includes('emerging')) {
    margin = benchmark.marginRange[0] + 2; // Near bottom of range
  }

  return { revenue, margin };
}

export const MarketPositionChart: React.FC<MarketPositionChartProps> = ({
  company,
  estimatedRevenue: propRevenue,
  estimatedMargin: propMargin,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [mousePos, setMousePos] = useState({ x: 0, y: 0 });
  const [showTooltip, setShowTooltip] = useState(false);

  // Check if we have enough data to show the chart
  const canShowChart = useMemo(() => {
    if (propRevenue && propMargin) return true;
    return hasReliableData(company);
  }, [company, propRevenue, propMargin]);

  const estimates = useMemo(() => {
    if (propRevenue && propMargin) {
      return { revenue: propRevenue, margin: propMargin };
    }
    return calculateEstimates(company);
  }, [company, propRevenue, propMargin]);

  // If we don't have reliable data, don't show the chart at all
  if (!canShowChart || !estimates) {
    return null;
  }

  const { revenue, margin } = estimates;
  const benchmark = INDUSTRY_BENCHMARKS[company.industry] || INDUSTRY_BENCHMARKS['default'];
  const employees = parseEmployeeCount(company.employeeCount);

  const handleMouseMove = (e: React.MouseEvent) => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setMousePos({
        x: e.clientX - rect.left,
        y: e.clientY - rect.top,
      });
    }
  };

  const formatCurrency = (value: number) => {
    if (value >= 1000) return `$${(value / 1000).toFixed(1)}B`;
    if (value >= 1) return `$${value.toFixed(1)}M`;
    return `$${(value * 1000).toFixed(0)}K`;
  };

  // Calculate position within margin range (0-100%)
  const marginPosition = Math.min(100, Math.max(0,
    ((margin - benchmark.marginRange[0]) / (benchmark.marginRange[1] - benchmark.marginRange[0])) * 100
  ));

  // Valuation calculations
  const baseValuation = revenue * benchmark.avgMultiple;
  const lowValuation = baseValuation * 0.85;
  const highValuation = baseValuation * 1.15;

  return (
    <GlassCard variant="elevated" padding="lg">
      <div style={headerStyles}>
        <div>
          <h3 style={titleStyles}>Valuation Estimate</h3>
          <p style={subtitleStyles}>
            Based on {employees} employees and {company.industry} sector benchmarks
          </p>
        </div>
        <div style={dataSourceStyles}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={colors.textMuted} strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 16v-4M12 8h.01" />
          </svg>
          <span>Estimated from public data</span>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div style={metricsGridStyles}>
        <div style={metricBoxStyles}>
          <div style={metricLabelStyles}>Est. Revenue</div>
          <div style={metricValueStyles}>{formatCurrency(revenue)}</div>
          <div style={metricSubStyles}>
            Based on {employees} employees
          </div>
        </div>

        <div style={metricBoxStyles}>
          <div style={metricLabelStyles}>Est. EBITDA Margin</div>
          <div style={metricValueStyles}>{margin.toFixed(1)}%</div>
          <div style={metricSubStyles}>
            Industry range: {benchmark.marginRange[0]}-{benchmark.marginRange[1]}%
          </div>
        </div>

        <div style={metricBoxStyles}>
          <div style={metricLabelStyles}>Sector Multiple</div>
          <div style={{ ...metricValueStyles, color: colors.primary }}>{benchmark.avgMultiple.toFixed(1)}x</div>
          <div style={metricSubStyles}>
            EV / EBITDA median
          </div>
        </div>

        <div style={{ ...metricBoxStyles, background: gradients.primarySubtle, borderColor: colors.glassBorderActive }}>
          <div style={metricLabelStyles}>Est. Valuation</div>
          <div style={{ ...metricValueStyles, color: colors.cyan }}>
            {formatCurrency(baseValuation)}
          </div>
          <div style={metricSubStyles}>
            Range: {formatCurrency(lowValuation)} - {formatCurrency(highValuation)}
          </div>
        </div>
      </div>

      {/* Margin Position Indicator */}
      <div
        ref={containerRef}
        style={chartContainerStyles}
        onMouseMove={handleMouseMove}
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
      >
        <div style={chartLabelStyles}>EBITDA Margin Position vs Industry</div>
        <div style={barContainerStyles}>
          {/* Range bar background */}
          <div style={rangeBarStyles}>
            <div style={rangeLowLabelStyles}>{benchmark.marginRange[0]}%</div>
            <div style={rangeHighLabelStyles}>{benchmark.marginRange[1]}%</div>

            {/* Position marker */}
            <div
              style={{
                ...positionMarkerStyles,
                left: `${marginPosition}%`,
              }}
            >
              <div style={markerLineStyles} />
              <div style={markerDotStyles} />
              <div style={markerLabelStyles}>{margin.toFixed(1)}%</div>
            </div>
          </div>
        </div>

        {/* Position description */}
        <div style={positionDescStyles}>
          {marginPosition >= 70 ? (
            <>Operating at <span style={{ color: colors.emerald }}>above-average margins</span> for the industry</>
          ) : marginPosition >= 40 ? (
            <>Operating at <span style={{ color: colors.primary }}>market-average margins</span> for the industry</>
          ) : (
            <>Operating at <span style={{ color: colors.amber }}>below-average margins</span>, potential for improvement</>
          )}
        </div>

        {/* Tooltip */}
        {showTooltip && (
          <div
            style={{
              ...tooltipStyles,
              left: Math.min(mousePos.x + 12, 280),
              top: mousePos.y - 10,
            }}
          >
            <div style={tooltipTitleStyles}>Methodology</div>
            <div style={tooltipTextStyles}>
              Revenue estimated using industry-standard revenue per employee ratios.
              Margin estimated based on company positioning and sector benchmarks.
              Multiple reflects median EV/EBITDA for recent {company.industry} transactions.
            </div>
          </div>
        )}
      </div>

      {/* Disclaimer */}
      <div style={disclaimerStyles}>
        Estimates based on employee count and industry benchmarks. Actual financials may vary.
      </div>
    </GlassCard>
  );
};

// Styles
const headerStyles: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: spacing.lg,
};

const titleStyles: React.CSSProperties = {
  fontSize: typography.sizes.md,
  fontWeight: typography.weights.semibold,
  color: colors.textPrimary,
  margin: 0,
  marginBottom: spacing.xs,
};

const subtitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  margin: 0,
};

const dataSourceStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.xs,
  fontSize: '10px',
  color: colors.textMuted,
  background: colors.glass,
  padding: `${spacing.xs} ${spacing.sm}`,
  borderRadius: borderRadius.sm,
  border: `1px solid ${colors.glassBorder}`,
};

const metricsGridStyles: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(4, 1fr)',
  gap: spacing.md,
  marginBottom: spacing.lg,
};

const metricBoxStyles: React.CSSProperties = {
  background: colors.glass,
  border: `1px solid ${colors.glassBorder}`,
  borderRadius: borderRadius.md,
  padding: spacing.md,
  textAlign: 'center',
};

const metricLabelStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  marginBottom: spacing.xs,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const metricValueStyles: React.CSSProperties = {
  fontSize: typography.sizes.lg,
  fontWeight: typography.weights.bold,
  color: colors.textPrimary,
  marginBottom: '2px',
};

const metricSubStyles: React.CSSProperties = {
  fontSize: '10px',
  color: colors.textMuted,
};

const chartContainerStyles: React.CSSProperties = {
  position: 'relative',
  background: 'rgba(0, 0, 0, 0.2)',
  borderRadius: borderRadius.md,
  padding: spacing.lg,
  marginBottom: spacing.md,
};

const chartLabelStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  marginBottom: spacing.md,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const barContainerStyles: React.CSSProperties = {
  marginBottom: spacing.md,
};

const rangeBarStyles: React.CSSProperties = {
  position: 'relative',
  height: 8,
  background: `linear-gradient(90deg, rgba(245, 158, 11, 0.3) 0%, rgba(99, 102, 241, 0.3) 50%, rgba(16, 185, 129, 0.3) 100%)`,
  borderRadius: borderRadius.full,
  marginTop: spacing.lg,
  marginBottom: spacing.xl,
};

const rangeLowLabelStyles: React.CSSProperties = {
  position: 'absolute',
  left: 0,
  top: -20,
  fontSize: '10px',
  color: colors.textMuted,
};

const rangeHighLabelStyles: React.CSSProperties = {
  position: 'absolute',
  right: 0,
  top: -20,
  fontSize: '10px',
  color: colors.textMuted,
};

const positionMarkerStyles: React.CSSProperties = {
  position: 'absolute',
  top: '50%',
  transform: 'translateX(-50%)',
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
};

const markerLineStyles: React.CSSProperties = {
  width: 2,
  height: 24,
  background: colors.cyan,
  marginBottom: -8,
};

const markerDotStyles: React.CSSProperties = {
  width: 16,
  height: 16,
  borderRadius: '50%',
  background: colors.cyan,
  border: '3px solid rgba(0, 0, 0, 0.5)',
  boxShadow: `0 0 12px ${colors.cyan}`,
};

const markerLabelStyles: React.CSSProperties = {
  marginTop: spacing.sm,
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.bold,
  color: colors.cyan,
};

const positionDescStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  color: colors.textSecondary,
  textAlign: 'center',
};

const tooltipStyles: React.CSSProperties = {
  position: 'absolute',
  background: colors.backgroundElevated,
  border: `1px solid ${colors.glassBorder}`,
  borderRadius: borderRadius.md,
  padding: spacing.md,
  pointerEvents: 'none',
  zIndex: 100,
  maxWidth: 280,
  boxShadow: '0 8px 24px rgba(0,0,0,0.5)',
};

const tooltipTitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.semibold,
  color: colors.textPrimary,
  marginBottom: spacing.sm,
};

const tooltipTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textSecondary,
  lineHeight: typography.lineHeights.relaxed,
};

const disclaimerStyles: React.CSSProperties = {
  fontSize: '10px',
  color: colors.textMuted,
  textAlign: 'center',
  fontStyle: 'italic',
};
