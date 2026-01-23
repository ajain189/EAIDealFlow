import React from 'react';
import { colors, borderRadius, typography, spacing, gradients, transitions, shadows } from '../../styles/theme';

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  loading?: boolean;
  fullWidth?: boolean;
  style?: React.CSSProperties;
  type?: 'button' | 'submit';
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = 'primary',
  size = 'md',
  disabled = false,
  loading = false,
  fullWidth = false,
  style,
  type = 'button',
}) => {
  const [isHovered, setIsHovered] = React.useState(false);
  const [isPressed, setIsPressed] = React.useState(false);

  const sizeStyles = {
    sm: {
      padding: `${spacing.sm} ${spacing.md}`,
      fontSize: typography.sizes.sm,
    },
    md: {
      padding: `${spacing.md} ${spacing.xl}`,
      fontSize: typography.sizes.base,
    },
    lg: {
      padding: `${spacing.lg} ${spacing['2xl']}`,
      fontSize: typography.sizes.md,
    },
  };

  const getVariantStyles = (): React.CSSProperties => {
    const isDisabled = disabled || loading;

    switch (variant) {
      case 'primary':
        return {
          background: isDisabled ? colors.textDisabled : (isHovered ? gradients.primaryHover : gradients.primary),
          color: colors.textPrimary,
          boxShadow: isHovered && !isDisabled ? shadows.glow : 'none',
        };
      case 'secondary':
        return {
          background: isHovered && !isDisabled ? colors.glassHover : colors.glass,
          color: colors.textPrimary,
          border: `1px solid ${isHovered && !isDisabled ? colors.glassBorderHover : colors.glassBorder}`,
        };
      case 'ghost':
        return {
          background: isHovered && !isDisabled ? 'rgba(99, 102, 241, 0.1)' : 'transparent',
          color: isHovered ? colors.primary : colors.textSecondary,
        };
      case 'danger':
        return {
          background: isHovered && !isDisabled ? colors.redLight : colors.red,
          color: colors.textPrimary,
        };
      default:
        return {};
    }
  };

  const baseStyles: React.CSSProperties = {
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: spacing.sm,
    borderRadius: borderRadius.md,
    fontFamily: typography.fontFamily,
    fontWeight: typography.weights.semibold,
    cursor: disabled || loading ? 'not-allowed' : 'pointer',
    opacity: disabled || loading ? 0.5 : 1,
    transition: transitions.normal,
    border: 'none',
    width: fullWidth ? '100%' : 'auto',
    transform: isPressed && !disabled ? 'scale(0.98)' : 'scale(1)',
    ...sizeStyles[size],
    ...getVariantStyles(),
    ...style,
  };

  return (
    <button
      type={type}
      style={baseStyles}
      onClick={onClick}
      disabled={disabled || loading}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setIsPressed(false);
      }}
      onMouseDown={() => setIsPressed(true)}
      onMouseUp={() => setIsPressed(false)}
    >
      {loading ? (
        <>
          <LoadingSpinner size={size === 'sm' ? 14 : 16} />
          <span>Processing...</span>
        </>
      ) : (
        children
      )}
    </button>
  );
};

const LoadingSpinner: React.FC<{ size: number }> = ({ size }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    style={{
      animation: 'spin 1s linear infinite',
    }}
  >
    <style>
      {`@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }`}
    </style>
    <circle
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="3"
      fill="none"
      strokeLinecap="round"
      strokeDasharray="31.416"
      strokeDashoffset="10"
      opacity="0.8"
    />
  </svg>
);
