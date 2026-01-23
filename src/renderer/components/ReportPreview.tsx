import React, { useState } from 'react';
import { GlassCard, Button, Badge } from './ui';
import { CompanyResearch } from '../types';
import { colors, typography, spacing, borderRadius, gradients } from '../styles/theme';

interface ReportPreviewProps {
  company: CompanyResearch;
  onDownload: () => void;
  onOpenPDF?: () => void;
  pdfPath?: string | null;
}

export const ReportPreview: React.FC<ReportPreviewProps> = ({
  company,
  onDownload,
  onOpenPDF,
  pdfPath,
}) => {
  const [expandedServices, setExpandedServices] = useState(false);
  const displayedServices = expandedServices ? company.services : company.services.slice(0, 3);

  return (
    <GlassCard variant="elevated" padding="lg">
      <div style={headerStyles}>
        <div>
          <div style={nameRowStyles}>
            <h2 style={titleStyles}>{company.name}</h2>
            {company.location && company.location !== 'Unknown' && (
              <span style={locationStyles}>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                {company.location}
              </span>
            )}
          </div>
          <div style={metaRowStyles}>
            <Badge variant="primary">{company.industry}</Badge>
            {company.yearFounded && company.yearFounded !== 'Unknown' && (
              <Badge variant="secondary">Est. {company.yearFounded}</Badge>
            )}
            {company.employeeCount && company.employeeCount !== 'Unknown' && (
              <Badge variant="secondary">{company.employeeCount} employees</Badge>
            )}
          </div>
        </div>
        <div style={actionsStyles}>
          {pdfPath && onOpenPDF && (
            <Button variant="secondary" size="sm" onClick={onOpenPDF}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '6px' }}>
                <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" />
                <path d="M14 2v6h6" />
                <path d="M12 18v-6" />
                <path d="M9 15l3 3 3-3" />
              </svg>
              Open
            </Button>
          )}
          <Button variant="secondary" size="sm" onClick={onDownload}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '6px' }}>
              <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
              <path d="M7 10l5 5 5-5" />
              <path d="M12 15V3" />
            </svg>
            Download
          </Button>
        </div>
      </div>

      <p style={descriptionStyles}>{company.description}</p>

      {/* Services Section */}
      <div style={sectionStyles}>
        <h3 style={sectionTitleStyles}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '8px', opacity: 0.6 }}>
            <path d="M22 11.08V12a10 10 0 11-5.93-9.14" />
            <path d="M22 4L12 14.01l-3-3" />
          </svg>
          Services & Offerings
        </h3>
        <div style={servicesGridStyles}>
          {displayedServices.map((service, index) => (
            <div key={index} style={serviceItemStyles}>
              <div style={serviceBulletStyles} />
              <span style={serviceTextStyles}>{service}</span>
            </div>
          ))}
        </div>
        {company.services.length > 3 && (
          <button
            style={showMoreButtonStyles}
            onClick={() => setExpandedServices(!expandedServices)}
          >
            {expandedServices ? 'Show less' : `Show ${company.services.length - 3} more`}
          </button>
        )}
      </div>

      {/* Competitive Position Highlight */}
      <div style={highlightBoxStyles}>
        <div style={highlightHeaderStyles}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={colors.primary} strokeWidth="2">
            <path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z" />
          </svg>
          <span style={highlightLabelStyles}>Competitive Position</span>
        </div>
        <div style={highlightTextStyles}>{company.competitiveAdvantage}</div>
      </div>

      {/* Key Metrics */}
      {company.keyMetrics && company.keyMetrics.length > 0 && company.keyMetrics[0] && (
        <div style={sectionStyles}>
          <h3 style={sectionTitleStyles}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '8px', opacity: 0.6 }}>
              <path d="M12 20V10" />
              <path d="M18 20V4" />
              <path d="M6 20v-4" />
            </svg>
            Key Highlights
          </h3>
          {company.keyMetrics.filter(m => m).map((metric, index) => (
            <div key={index} style={metricItemStyles}>
              <div style={metricIconStyles}>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke={colors.emerald} strokeWidth="3">
                  <path d="M20 6L9 17l-5-5" />
                </svg>
              </div>
              <span style={metricTextStyles}>{metric}</span>
            </div>
          ))}
        </div>
      )}

      {/* Ownership Info */}
      {company.ownershipHints && company.ownershipHints !== 'Not publicly available' && (
        <div style={ownershipBoxStyles}>
          <div style={ownershipLabelStyles}>
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ marginRight: '6px' }}>
              <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" />
              <circle cx="12" cy="7" r="4" />
            </svg>
            Leadership
          </div>
          <div style={ownershipTextStyles}>{company.ownershipHints}</div>
        </div>
      )}
    </GlassCard>
  );
};

// Styles
const headerStyles: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'flex-start',
  marginBottom: spacing.lg,
  gap: spacing.lg,
};

const nameRowStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.md,
  marginBottom: spacing.sm,
  flexWrap: 'wrap',
};

const titleStyles: React.CSSProperties = {
  fontSize: typography.sizes.xl,
  fontWeight: typography.weights.bold,
  color: colors.textPrimary,
  margin: 0,
  letterSpacing: '-0.3px',
};

const locationStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: '4px',
  fontSize: typography.sizes.sm,
  color: colors.textMuted,
};

const metaRowStyles: React.CSSProperties = {
  display: 'flex',
  gap: spacing.sm,
  alignItems: 'center',
  flexWrap: 'wrap',
};

const actionsStyles: React.CSSProperties = {
  display: 'flex',
  gap: spacing.sm,
  flexShrink: 0,
};

const descriptionStyles: React.CSSProperties = {
  fontSize: typography.sizes.base,
  color: colors.textSecondary,
  lineHeight: typography.lineHeights.relaxed,
  marginBottom: spacing.xl,
  paddingBottom: spacing.lg,
  borderBottom: `1px solid ${colors.glassBorder}`,
};

const sectionStyles: React.CSSProperties = {
  marginBottom: spacing.lg,
};

const sectionTitleStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  fontSize: typography.sizes.xs,
  fontWeight: typography.weights.semibold,
  color: colors.textSecondary,
  marginBottom: spacing.md,
  textTransform: 'uppercase',
  letterSpacing: '0.8px',
};

const servicesGridStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: spacing.xs,
};

const serviceItemStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  gap: spacing.md,
  padding: `${spacing.sm} 0`,
};

const serviceBulletStyles: React.CSSProperties = {
  width: 6,
  height: 6,
  borderRadius: '50%',
  background: gradients.primary,
  marginTop: 7,
  flexShrink: 0,
};

const serviceTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  color: colors.textSecondary,
  lineHeight: 1.5,
};

const showMoreButtonStyles: React.CSSProperties = {
  marginTop: spacing.sm,
  padding: `${spacing.xs} ${spacing.md}`,
  fontSize: typography.sizes.xs,
  color: colors.primary,
  background: 'transparent',
  border: 'none',
  cursor: 'pointer',
  fontWeight: typography.weights.medium,
};

const highlightBoxStyles: React.CSSProperties = {
  background: gradients.primarySubtle,
  borderLeft: `3px solid ${colors.primary}`,
  padding: spacing.lg,
  borderRadius: `0 ${borderRadius.md} ${borderRadius.md} 0`,
  marginBottom: spacing.lg,
};

const highlightHeaderStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.sm,
  marginBottom: spacing.sm,
};

const highlightLabelStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  fontWeight: typography.weights.semibold,
  color: colors.primary,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const highlightTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.base,
  color: colors.textPrimary,
  fontWeight: typography.weights.medium,
  lineHeight: 1.5,
};

const metricItemStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  gap: spacing.md,
  padding: `${spacing.sm} 0`,
};

const metricIconStyles: React.CSSProperties = {
  width: 18,
  height: 18,
  borderRadius: '50%',
  background: 'rgba(16, 185, 129, 0.15)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: 0,
  marginTop: 2,
};

const metricTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  color: colors.textSecondary,
  lineHeight: 1.5,
};

const ownershipBoxStyles: React.CSSProperties = {
  background: colors.glass,
  border: `1px solid ${colors.glassBorder}`,
  borderRadius: borderRadius.md,
  padding: spacing.md,
  marginTop: spacing.lg,
};

const ownershipLabelStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  marginBottom: spacing.xs,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
};

const ownershipTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  color: colors.textSecondary,
};
