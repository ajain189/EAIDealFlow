import React from 'react';
import { GlassCard, Input, Button } from './ui';
import { colors, typography, spacing, borderRadius, gradients } from '../styles/theme';

interface CompanyInputProps {
  companyName: string;
  websiteUrl: string;
  onCompanyNameChange: (value: string) => void;
  onWebsiteUrlChange: (value: string) => void;
  onSubmit: () => void;
  loading: boolean;
  error?: string | null;
}

export const CompanyInput: React.FC<CompanyInputProps> = ({
  companyName,
  websiteUrl,
  onCompanyNameChange,
  onWebsiteUrlChange,
  onSubmit,
  loading,
  error,
}) => {
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && companyName && websiteUrl && !loading) {
      onSubmit();
    }
  };

  return (
    <GlassCard variant="elevated" padding="lg">
      <div style={headerStyles}>
        <div style={iconContainerStyles}>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={colors.primary} strokeWidth="2">
            <circle cx="11" cy="11" r="8" />
            <path d="M21 21l-4.35-4.35" />
          </svg>
        </div>
        <div>
          <h2 style={titleStyles}>Research Company</h2>
          <p style={subtitleStyles}>Enter a company to analyze</p>
        </div>
      </div>

      <div style={formStyles} onKeyDown={handleKeyPress}>
        <Input
          label="Company Name"
          placeholder="e.g., Acme HVAC Services"
          value={companyName}
          onChange={onCompanyNameChange}
          disabled={loading}
        />
        <Input
          label="Website URL"
          placeholder="e.g., www.acmehvac.com"
          value={websiteUrl}
          onChange={onWebsiteUrlChange}
          type="url"
          disabled={loading}
        />

        {error && (
          <div style={errorStyles}>
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={colors.red} strokeWidth="2" style={{ flexShrink: 0 }}>
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
            <span>{error}</span>
          </div>
        )}

        <Button
          onClick={onSubmit}
          disabled={!companyName.trim() || !websiteUrl.trim()}
          loading={loading}
          fullWidth
        >
          {loading ? 'Researching...' : 'Generate Report'}
        </Button>

        <div style={hintStyles}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" style={{ opacity: 0.6 }}>
            <circle cx="12" cy="12" r="10" />
            <path d="M12 16v-4" />
            <path d="M12 8h.01" />
          </svg>
          <span>AI will research the company website and generate a comprehensive analysis</span>
        </div>
      </div>
    </GlassCard>
  );
};

// Styles
const headerStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  gap: spacing.md,
  marginBottom: spacing.xl,
};

const iconContainerStyles: React.CSSProperties = {
  width: 40,
  height: 40,
  borderRadius: borderRadius.md,
  background: gradients.primarySubtle,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  flexShrink: 0,
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

const formStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: spacing.lg,
};

const errorStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'flex-start',
  gap: spacing.sm,
  fontSize: typography.sizes.sm,
  color: colors.red,
  padding: spacing.md,
  background: 'rgba(239, 68, 68, 0.08)',
  borderRadius: borderRadius.md,
  border: '1px solid rgba(239, 68, 68, 0.15)',
};

const hintStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.sm,
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  paddingTop: spacing.sm,
};
