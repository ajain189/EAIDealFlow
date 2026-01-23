import React from 'react';
import { colors, typography, spacing, borderRadius } from '../../styles/theme';
import { GlassCard } from './GlassCard';

interface LoadingStateProps {
  message?: string;
  submessage?: string;
}

export const LoadingState: React.FC<LoadingStateProps> = ({
  message = 'Processing...',
  submessage,
}) => {
  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    padding: spacing['2xl'],
    gap: spacing.lg,
  };

  const spinnerContainerStyles: React.CSSProperties = {
    position: 'relative',
    width: 60,
    height: 60,
  };

  const messageStyles: React.CSSProperties = {
    fontSize: typography.sizes.md,
    fontWeight: typography.weights.medium,
    color: colors.textPrimary,
    textAlign: 'center',
  };

  const submessageStyles: React.CSSProperties = {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    textAlign: 'center',
  };

  return (
    <GlassCard>
      <div style={containerStyles}>
        <div style={spinnerContainerStyles}>
          <svg
            width="60"
            height="60"
            viewBox="0 0 60 60"
            style={{ animation: 'spin 1.5s linear infinite' }}
          >
            <style>
              {`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}
            </style>
            <circle
              cx="30"
              cy="30"
              r="26"
              stroke="rgba(99, 102, 241, 0.2)"
              strokeWidth="4"
              fill="none"
            />
            <circle
              cx="30"
              cy="30"
              r="26"
              stroke="url(#gradient)"
              strokeWidth="4"
              fill="none"
              strokeLinecap="round"
              strokeDasharray="120"
              strokeDashoffset="80"
            />
            <defs>
              <linearGradient id="gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#6366f1" />
                <stop offset="100%" stopColor="#8b5cf6" />
              </linearGradient>
            </defs>
          </svg>
        </div>
        <div>
          <p style={messageStyles}>{message}</p>
          {submessage && <p style={submessageStyles}>{submessage}</p>}
        </div>
      </div>
    </GlassCard>
  );
};

interface ProgressBarProps {
  progress: number;
  label?: string;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({ progress, label }) => {
  const containerStyles: React.CSSProperties = {
    width: '100%',
  };

  const labelStyles: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: spacing.sm,
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
  };

  const trackStyles: React.CSSProperties = {
    width: '100%',
    height: 6,
    background: colors.glass,
    borderRadius: borderRadius.full,
    overflow: 'hidden',
  };

  const fillStyles: React.CSSProperties = {
    width: `${Math.min(100, Math.max(0, progress))}%`,
    height: '100%',
    background: 'linear-gradient(90deg, #6366f1 0%, #8b5cf6 100%)',
    borderRadius: borderRadius.full,
    transition: 'width 0.3s ease',
  };

  return (
    <div style={containerStyles}>
      {label && (
        <div style={labelStyles}>
          <span>{label}</span>
          <span>{Math.round(progress)}%</span>
        </div>
      )}
      <div style={trackStyles}>
        <div style={fillStyles} />
      </div>
    </div>
  );
};
