import React, { useState } from 'react';
import { motion, Variants } from 'framer-motion';
import { borderRadius, spacing, glassEffect } from '../../styles/theme';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  style?: React.CSSProperties;
  hover?: boolean;
  onClick?: () => void;
  padding?: 'none' | 'sm' | 'md' | 'lg' | 'xl';
  variant?: 'default' | 'elevated' | 'subtle' | 'glow';
  animate?: boolean;
  delay?: number;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  style,
  hover = false,
  onClick,
  padding = 'lg',
  variant = 'default',
  animate = true,
  delay = 0,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const paddingMap = {
    none: '0',
    sm: spacing.sm,
    md: spacing.md,
    lg: spacing.lg,
    xl: spacing.xl,
  };

  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'elevated':
        return {
          ...glassEffect.elevated,
        };
      case 'subtle':
        return {
          ...glassEffect.subtle,
        };
      case 'glow':
        return {
          ...(isHovered ? glassEffect.glow : glassEffect.elevated),
        };
      default:
        return {
          ...glassEffect.standard,
        };
    }
  };

  const baseStyles: React.CSSProperties = {
    borderRadius: borderRadius.xl,
    padding: paddingMap[padding],
    position: 'relative',
    overflow: 'hidden',
    ...(hover && { cursor: 'pointer' }),
    ...getVariantStyles(),
    ...style,
  };

  // Animation variants for Framer Motion
  const cardVariants: Variants = {
    hidden: { opacity: 0, y: 20, scale: 0.98 },
    visible: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: 0.4,
        delay: delay,
        ease: [0.25, 0.1, 0.25, 1] as const,
      },
    },
  };

  const hoverVariants: Variants = hover ? {
    hover: {
      y: -4,
      scale: 1.01,
      boxShadow: '0 12px 40px rgba(0, 0, 0, 0.5), 0 0 40px rgba(99, 102, 241, 0.1)',
      borderColor: 'rgba(255, 255, 255, 0.15)',
      transition: { duration: 0.2, ease: [0.4, 0, 0.2, 1] as const },
    },
  } : {};

  return (
    <motion.div
      className={className}
      style={baseStyles}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      initial={animate ? 'hidden' : false}
      animate={animate ? 'visible' : false}
      whileHover={hover ? 'hover' : undefined}
      variants={{ ...cardVariants, ...hoverVariants }}
    >
      {/* Top highlight edge - makes glass effect pop */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.12) 20%, rgba(255,255,255,0.15) 50%, rgba(255,255,255,0.12) 80%, transparent 100%)',
          pointerEvents: 'none',
        }}
      />
      {/* Inner glow overlay */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '40%',
          background: 'linear-gradient(180deg, rgba(255,255,255,0.03) 0%, transparent 100%)',
          pointerEvents: 'none',
          borderRadius: `${borderRadius.xl} ${borderRadius.xl} 0 0`,
        }}
      />
      {children}
    </motion.div>
  );
};
