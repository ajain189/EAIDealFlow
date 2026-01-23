import React, { useState } from 'react';
import { GlassCard, Button } from './ui';
import { CompanyResearch, GeneratedEmail, EmailTone, EmailType } from '../types';
import { generateEmail } from '../services/gemini';
import { colors, typography, spacing, borderRadius, transitions, gradients } from '../styles/theme';

interface EmailGeneratorProps {
  company: CompanyResearch;
  initialEmails?: Record<string, GeneratedEmail>;
  onEmailsUpdate?: (emails: Record<string, GeneratedEmail>) => void;
}

const TONES: { id: EmailTone; label: string; description: string; icon: string }[] = [
  { id: 'formal', label: 'Formal', description: 'Professional', icon: 'M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4' },
  { id: 'friendly', label: 'Friendly', description: 'Warm', icon: 'M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z' },
  { id: 'direct', label: 'Direct', description: 'Concise', icon: 'M13 10V3L4 14h7v7l9-11h-7z' },
];

const EMAIL_TABS: { id: EmailType; label: string; description: string }[] = [
  { id: 'hook', label: 'Initial Hook', description: 'First touchpoint' },
  { id: 'asset', label: 'Value Add', description: 'Provide insights' },
  { id: 'close', label: 'Soft Close', description: 'Call to action' },
];

export const EmailGenerator: React.FC<EmailGeneratorProps> = ({
  company,
  initialEmails = {},
  onEmailsUpdate,
}) => {
  const [tone, setTone] = useState<EmailTone>('formal');
  const [activeTab, setActiveTab] = useState<EmailType>('hook');
  const [emails, setEmails] = useState<Record<string, GeneratedEmail>>(initialEmails);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);

  const currentKey = `${activeTab}-${tone}`;
  const currentEmail = emails[currentKey];

  const handleGenerateEmail = async () => {
    setLoading(true);
    try {
      const email = await generateEmail(company, tone, activeTab);
      const newEmails = { ...emails, [currentKey]: email };
      setEmails(newEmails);
      onEmailsUpdate?.(newEmails);
    } catch (error) {
      console.error('Failed to generate email:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = async () => {
    if (currentEmail) {
      const text = `Subject: ${currentEmail.subject}\n\n${currentEmail.body}`;
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const completedCount = Object.keys(emails).length;

  return (
    <GlassCard variant="elevated" padding="lg" style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <div style={headerStyles}>
        <div style={headerLeftStyles}>
          <div style={iconContainerStyles}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke={colors.primary} strokeWidth="2">
              <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
          </div>
          <div>
            <h2 style={titleStyles}>Outreach Sequence</h2>
            <p style={subtitleStyles}>Personalized for {company.name}</p>
          </div>
        </div>
        <div style={progressContainerStyles}>
          <div style={progressBarBgStyles}>
            <div style={{ ...progressBarFillStyles, width: `${(completedCount / 9) * 100}%` }} />
          </div>
          <span style={progressTextStyles}>{completedCount}/9</span>
        </div>
      </div>

      {/* Tone Selector */}
      <div style={sectionStyles}>
        <div style={sectionLabelStyles}>Select Tone</div>
        <div style={toneGridStyles}>
          {TONES.map((t) => (
            <ToneButton
              key={t.id}
              label={t.label}
              description={t.description}
              icon={t.icon}
              isActive={tone === t.id}
              onClick={() => setTone(t.id)}
            />
          ))}
        </div>
      </div>

      {/* Email Sequence Steps */}
      <div style={sectionStyles}>
        <div style={sectionLabelStyles}>Email Sequence</div>
        <div style={sequenceContainerStyles}>
          {EMAIL_TABS.map((tab, index) => {
            const hasEmail = emails[`${tab.id}-${tone}`];
            const isActive = activeTab === tab.id;
            return (
              <button
                key={tab.id}
                style={sequenceStepStyles(isActive, !!hasEmail)}
                onClick={() => setActiveTab(tab.id)}
              >
                <div style={stepNumberStyles(isActive, !!hasEmail)}>{index + 1}</div>
                <div style={stepContentStyles}>
                  <span style={stepLabelStyles(isActive)}>{tab.label}</span>
                  <span style={stepDescStyles}>{tab.description}</span>
                </div>
                {hasEmail && (
                  <div style={checkmarkStyles}>
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={colors.emerald} strokeWidth="3">
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                  </div>
                )}
              </button>
            );
          })}
        </div>
      </div>

      {/* Generate Button */}
      <Button
        onClick={handleGenerateEmail}
        loading={loading}
        fullWidth
        variant={currentEmail ? 'secondary' : 'primary'}
        style={{ marginBottom: spacing.md }}
      >
        {loading ? 'Crafting email...' : currentEmail ? 'Regenerate' : 'Generate Email'}
      </Button>

      {/* Email Preview Card */}
      <div style={emailClientContainerStyles}>
        {currentEmail ? (
          <div style={emailClientStyles}>
            {/* Email Header Bar */}
            <div style={emailHeaderBarStyles}>
              <div style={emailHeaderLeftStyles}>
                <div style={emailAvatarStyles}>
                  {company.name.charAt(0).toUpperCase()}
                </div>
                <div>
                  <div style={emailToStyles}>To: {company.name} Team</div>
                  <div style={emailMetaStyles}>{activeTab === 'hook' ? 'Initial Outreach' : activeTab === 'asset' ? 'Follow-up' : 'Closing'} - {tone} tone</div>
                </div>
              </div>
              <button
                style={expandButtonStyles}
                onClick={() => setIsExpanded(!isExpanded)}
                title={isExpanded ? 'Collapse' : 'Expand'}
              >
                <svg
                  width="16"
                  height="16"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  style={{ transform: isExpanded ? 'rotate(180deg)' : 'none', transition: transitions.fast }}
                >
                  <path d="M19 9l-7 7-7-7" />
                </svg>
              </button>
            </div>

            {/* Subject Line */}
            <div style={subjectContainerStyles}>
              <span style={subjectLabelStyles}>Subject:</span>
              <span style={subjectTextStyles}>{currentEmail.subject}</span>
            </div>

            {/* Email Body */}
            {isExpanded && (
              <div style={bodyContainerStyles}>
                <div style={bodyTextStyles}>{currentEmail.body}</div>
              </div>
            )}

            {/* Action Bar */}
            <div style={actionBarStyles}>
              <button
                style={copyButtonStyles(copied)}
                onClick={handleCopy}
              >
                {copied ? (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={colors.emerald} strokeWidth="2.5">
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                    <span>Copied!</span>
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2" />
                      <path d="M5 15H4a2 2 0 01-2-2V4a2 2 0 012-2h9a2 2 0 012 2v1" />
                    </svg>
                    <span>Copy to Clipboard</span>
                  </>
                )}
              </button>
            </div>
          </div>
        ) : (
          <div style={emptyStateStyles}>
            <div style={emptyIconContainerStyles}>
              <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke={colors.textMuted} strokeWidth="1.5">
                <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" />
                <polyline points="22,6 12,13 2,6" />
              </svg>
            </div>
            <p style={emptyTitleStyles}>Ready to craft your email</p>
            <p style={emptyTextStyles}>
              Select your preferred tone and click generate
            </p>
          </div>
        )}
      </div>
    </GlassCard>
  );
};

// Tone Button Component
interface ToneButtonProps {
  label: string;
  description: string;
  icon: string;
  isActive: boolean;
  onClick: () => void;
}

const ToneButton: React.FC<ToneButtonProps> = ({ label, description, icon, isActive, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <button
      style={{
        flex: 1,
        padding: spacing.md,
        borderRadius: borderRadius.md,
        textAlign: 'center',
        color: isActive ? colors.textPrimary : colors.textSecondary,
        background: isActive
          ? gradients.primarySubtle
          : isHovered
            ? 'rgba(255, 255, 255, 0.04)'
            : 'transparent',
        border: `1px solid ${isActive ? colors.glassBorderActive : colors.glassBorder}`,
        cursor: 'pointer',
        transition: transitions.fast,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        gap: spacing.xs,
      }}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ opacity: isActive ? 1 : 0.6 }}>
        <path d={icon} />
      </svg>
      <div style={{
        fontSize: typography.sizes.sm,
        fontWeight: typography.weights.medium,
      }}>
        {label}
      </div>
      <div style={{
        fontSize: '10px',
        color: colors.textMuted,
      }}>
        {description}
      </div>
    </button>
  );
};

// Styles
const headerStyles: React.CSSProperties = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: spacing.lg,
  paddingBottom: spacing.md,
  borderBottom: `1px solid ${colors.glassBorder}`,
};

const headerLeftStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.md,
};

const iconContainerStyles: React.CSSProperties = {
  width: 40,
  height: 40,
  borderRadius: borderRadius.md,
  background: 'rgba(99, 102, 241, 0.1)',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const titleStyles: React.CSSProperties = {
  fontSize: typography.sizes.base,
  fontWeight: typography.weights.semibold,
  color: colors.textPrimary,
  margin: 0,
};

const subtitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  margin: 0,
  marginTop: '2px',
};

const progressContainerStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.sm,
};

const progressBarBgStyles: React.CSSProperties = {
  width: 60,
  height: 4,
  borderRadius: borderRadius.full,
  background: colors.glass,
  overflow: 'hidden',
};

const progressBarFillStyles: React.CSSProperties = {
  height: '100%',
  background: gradients.primary,
  borderRadius: borderRadius.full,
  transition: transitions.normal,
};

const progressTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  fontWeight: typography.weights.medium,
};

const sectionStyles: React.CSSProperties = {
  marginBottom: spacing.md,
};

const sectionLabelStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  marginBottom: spacing.sm,
  textTransform: 'uppercase',
  letterSpacing: '0.5px',
  fontWeight: typography.weights.medium,
};

const toneGridStyles: React.CSSProperties = {
  display: 'flex',
  gap: spacing.sm,
};

const sequenceContainerStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  gap: spacing.xs,
};

const sequenceStepStyles = (isActive: boolean, _hasEmail: boolean): React.CSSProperties => ({
  display: 'flex',
  alignItems: 'center',
  gap: spacing.md,
  padding: `${spacing.sm} ${spacing.md}`,
  borderRadius: borderRadius.md,
  background: isActive ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
  border: `1px solid ${isActive ? colors.glassBorderActive : 'transparent'}`,
  cursor: 'pointer',
  transition: transitions.fast,
  textAlign: 'left',
});

const stepNumberStyles = (isActive: boolean, hasEmail: boolean): React.CSSProperties => ({
  width: 24,
  height: 24,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  borderRadius: borderRadius.sm,
  background: hasEmail ? 'rgba(16, 185, 129, 0.15)' : isActive ? 'rgba(99, 102, 241, 0.2)' : colors.glass,
  fontSize: typography.sizes.xs,
  fontWeight: typography.weights.semibold,
  color: hasEmail ? colors.emerald : isActive ? colors.primary : colors.textMuted,
});

const stepContentStyles: React.CSSProperties = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
};

const stepLabelStyles = (isActive: boolean): React.CSSProperties => ({
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.medium,
  color: isActive ? colors.textPrimary : colors.textSecondary,
});

const stepDescStyles: React.CSSProperties = {
  fontSize: '10px',
  color: colors.textMuted,
};

const checkmarkStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
};

const emailClientContainerStyles: React.CSSProperties = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  minHeight: 0,
};

const emailClientStyles: React.CSSProperties = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  background: 'rgba(0, 0, 0, 0.25)',
  borderRadius: borderRadius.lg,
  border: `1px solid ${colors.glassBorder}`,
  overflow: 'hidden',
};

const emailHeaderBarStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: spacing.md,
  background: 'rgba(0, 0, 0, 0.2)',
  borderBottom: `1px solid ${colors.glassBorder}`,
};

const emailHeaderLeftStyles: React.CSSProperties = {
  display: 'flex',
  alignItems: 'center',
  gap: spacing.md,
};

const emailAvatarStyles: React.CSSProperties = {
  width: 36,
  height: 36,
  borderRadius: borderRadius.md,
  background: gradients.primary,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.bold,
  color: colors.textPrimary,
};

const emailToStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.medium,
  color: colors.textPrimary,
};

const emailMetaStyles: React.CSSProperties = {
  fontSize: '10px',
  color: colors.textMuted,
  marginTop: '2px',
};

const expandButtonStyles: React.CSSProperties = {
  width: 28,
  height: 28,
  borderRadius: borderRadius.sm,
  background: 'transparent',
  border: `1px solid ${colors.glassBorder}`,
  cursor: 'pointer',
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: colors.textMuted,
  transition: transitions.fast,
};

const subjectContainerStyles: React.CSSProperties = {
  padding: spacing.md,
  borderBottom: `1px solid ${colors.glassBorder}`,
  display: 'flex',
  alignItems: 'flex-start',
  gap: spacing.sm,
};

const subjectLabelStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  flexShrink: 0,
  paddingTop: '2px',
};

const subjectTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.medium,
  color: colors.textPrimary,
  lineHeight: typography.lineHeights.relaxed,
};

const bodyContainerStyles: React.CSSProperties = {
  flex: 1,
  padding: spacing.md,
  overflow: 'auto',
};

const bodyTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  color: colors.textSecondary,
  lineHeight: typography.lineHeights.relaxed,
  whiteSpace: 'pre-wrap',
};

const actionBarStyles: React.CSSProperties = {
  padding: spacing.md,
  borderTop: `1px solid ${colors.glassBorder}`,
  background: 'rgba(0, 0, 0, 0.15)',
};

const copyButtonStyles = (copied: boolean): React.CSSProperties => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  gap: spacing.sm,
  width: '100%',
  padding: spacing.md,
  borderRadius: borderRadius.md,
  background: copied ? 'rgba(16, 185, 129, 0.15)' : 'rgba(6, 182, 212, 0.1)',
  border: `1px solid ${copied ? 'rgba(16, 185, 129, 0.3)' : 'rgba(6, 182, 212, 0.2)'}`,
  color: copied ? colors.emerald : colors.cyan,
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.medium,
  cursor: 'pointer',
  transition: transitions.fast,
});

const emptyStateStyles: React.CSSProperties = {
  flex: 1,
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: spacing.xl,
  textAlign: 'center',
  background: 'rgba(0, 0, 0, 0.15)',
  borderRadius: borderRadius.lg,
  border: `1px dashed ${colors.glassBorder}`,
};

const emptyIconContainerStyles: React.CSSProperties = {
  marginBottom: spacing.md,
  opacity: 0.4,
};

const emptyTitleStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  fontWeight: typography.weights.medium,
  color: colors.textSecondary,
  marginBottom: spacing.xs,
};

const emptyTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.xs,
  color: colors.textMuted,
  maxWidth: 200,
};
