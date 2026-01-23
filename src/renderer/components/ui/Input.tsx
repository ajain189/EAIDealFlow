import React from 'react';
import { colors, borderRadius, typography, spacing, transitions } from '../../styles/theme';

interface InputProps {
  label?: string;
  placeholder?: string;
  value: string;
  onChange: (value: string) => void;
  type?: 'text' | 'url' | 'email' | 'password' | 'number';
  error?: string;
  disabled?: boolean;
  multiline?: boolean;
  rows?: number;
  style?: React.CSSProperties;
}

export const Input: React.FC<InputProps> = ({
  label,
  placeholder,
  value,
  onChange,
  type = 'text',
  error,
  disabled = false,
  multiline = false,
  rows = 3,
  style,
}) => {
  const [isFocused, setIsFocused] = React.useState(false);

  const containerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: spacing.sm,
    ...style,
  };

  const labelStyles: React.CSSProperties = {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.textSecondary,
  };

  const inputWrapperStyles: React.CSSProperties = {
    position: 'relative',
  };

  const inputStyles: React.CSSProperties = {
    width: '100%',
    padding: `${spacing.md} ${spacing.lg}`,
    background: colors.glass,
    border: `1px solid ${error ? colors.red : isFocused ? colors.primary : colors.glassBorder}`,
    borderRadius: borderRadius.md,
    fontSize: typography.sizes.base,
    color: colors.textPrimary,
    transition: transitions.normal,
    fontFamily: typography.fontFamily,
    opacity: disabled ? 0.5 : 1,
    cursor: disabled ? 'not-allowed' : 'text',
    resize: multiline ? 'vertical' : 'none',
  };

  const errorStyles: React.CSSProperties = {
    fontSize: typography.sizes.sm,
    color: colors.red,
  };

  const InputComponent = multiline ? 'textarea' : 'input';

  return (
    <div style={containerStyles}>
      {label && <label style={labelStyles}>{label}</label>}
      <div style={inputWrapperStyles}>
        <InputComponent
          type={type}
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          disabled={disabled}
          onFocus={() => setIsFocused(true)}
          onBlur={() => setIsFocused(false)}
          style={inputStyles}
          rows={multiline ? rows : undefined}
        />
      </div>
      {error && <span style={errorStyles}>{error}</span>}
    </div>
  );
};
