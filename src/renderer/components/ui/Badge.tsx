import React from 'react';
import { colors, borderRadius, typography, spacing } from '../../styles/theme';

interface BadgeProps {
  children: React.ReactNode;
  variant?: 'default' | 'primary' | 'secondary' | 'success' | 'warning' | 'error' | 'cyan';
  size?: 'sm' | 'md';
}

export const Badge: React.FC<BadgeProps> = ({
  children,
  variant = 'default',
  size = 'sm',
}) => {
  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'primary':
        return {
          background: 'rgba(99, 102, 241, 0.15)',
          color: colors.primaryLight,
          border: `1px solid rgba(99, 102, 241, 0.3)`,
        };
      case 'secondary':
        return {
          background: 'rgba(255, 255, 255, 0.04)',
          color: colors.textSecondary,
          border: `1px solid rgba(255, 255, 255, 0.08)`,
        };
      case 'cyan':
        return {
          background: 'rgba(6, 182, 212, 0.15)',
          color: colors.cyanLight,
          border: `1px solid rgba(6, 182, 212, 0.3)`,
        };
      case 'success':
        return {
          background: 'rgba(16, 185, 129, 0.15)',
          color: colors.emeraldLight,
          border: `1px solid rgba(16, 185, 129, 0.3)`,
        };
      case 'warning':
        return {
          background: 'rgba(245, 158, 11, 0.15)',
          color: colors.amberLight,
          border: `1px solid rgba(245, 158, 11, 0.3)`,
        };
      case 'error':
        return {
          background: 'rgba(239, 68, 68, 0.15)',
          color: colors.redLight,
          border: `1px solid rgba(239, 68, 68, 0.3)`,
        };
      default:
        return {
          background: colors.glass,
          color: colors.textSecondary,
          border: `1px solid ${colors.glassBorder}`,
        };
    }
  };

  const sizeStyles = {
    sm: {
      padding: `${spacing.xs} ${spacing.sm}`,
      fontSize: typography.sizes.xs,
    },
    md: {
      padding: `${spacing.sm} ${spacing.md}`,
      fontSize: typography.sizes.sm,
    },
  };

  const badgeStyles: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    borderRadius: borderRadius.full,
    fontWeight: typography.weights.medium,
    ...sizeStyles[size],
    ...getVariantStyles(),
  };

  return <span style={badgeStyles}>{children}</span>;
};
