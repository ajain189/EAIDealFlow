import React from 'react';
import { motion } from 'framer-motion';
import { colors, typography, spacing, borderRadius, transitions } from '../styles/theme';

interface LayoutProps {
  children: React.ReactNode;
  sidebar?: React.ReactNode;
}

export const Layout: React.FC<LayoutProps> = ({ children, sidebar }) => {
  const containerStyles: React.CSSProperties = {
    display: 'flex',
    height: '100vh',
    width: '100vw',
    overflow: 'hidden',
    position: 'relative',
  };

  const mainStyles: React.CSSProperties = {
    flex: 1,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    position: 'relative',
  };

  return (
    <div style={containerStyles}>
      {sidebar}
      <main style={mainStyles}>{children}</main>
    </div>
  );
};

interface SidebarProps {
  children: React.ReactNode;
}

export const Sidebar: React.FC<SidebarProps> = ({ children }) => {
  const sidebarStyles: React.CSSProperties = {
    width: 280,
    minWidth: 280,
    height: '100%',
    // Black glass effect
    background: 'rgba(14, 17, 23, 0.7)',
    backdropFilter: 'blur(20px)',
    WebkitBackdropFilter: 'blur(20px)',
    borderRight: `1px solid rgba(255, 255, 255, 0.08)`,
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    position: 'relative',
  };

  return (
    <aside style={sidebarStyles}>
      {/* Top highlight */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '1px',
          background: 'linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent)',
          pointerEvents: 'none',
        }}
      />
      {children}
    </aside>
  );
};

interface HeaderProps {
  title: string;
  subtitle?: string;
  actions?: React.ReactNode;
}

export const Header: React.FC<HeaderProps> = ({ title, subtitle, actions }) => {
  const headerStyles = {
    padding: `${spacing.lg} ${spacing.xl}`,
    paddingTop: spacing['2xl'],
    borderBottom: `1px solid rgba(255, 255, 255, 0.06)`,
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    WebkitAppRegion: 'drag',
    background: 'rgba(14, 17, 23, 0.4)',
    backdropFilter: 'blur(12px)',
    WebkitBackdropFilter: 'blur(12px)',
  } as React.CSSProperties;

  const titleContainerStyles: React.CSSProperties = {
    display: 'flex',
    flexDirection: 'column',
    gap: spacing.xs,
  };

  const titleStyles: React.CSSProperties = {
    fontSize: typography.sizes['2xl'],
    fontWeight: typography.weights.bold,
    color: colors.textPrimary,
    letterSpacing: '-0.5px',
    margin: 0,
  };

  const subtitleStyles: React.CSSProperties = {
    fontSize: typography.sizes.sm,
    color: colors.textSecondary,
    margin: 0,
  };

  const actionsStyles = {
    display: 'flex',
    gap: spacing.sm,
    WebkitAppRegion: 'no-drag',
  } as React.CSSProperties;

  return (
    <motion.header
      style={headerStyles}
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
    >
      <div style={titleContainerStyles}>
        <h1 style={titleStyles}>{title}</h1>
        {subtitle && <p style={subtitleStyles}>{subtitle}</p>}
      </div>
      {actions && <div style={actionsStyles}>{actions}</div>}
    </motion.header>
  );
};

interface ContentProps {
  children: React.ReactNode;
  padding?: boolean;
}

export const Content: React.FC<ContentProps> = ({ children, padding = true }) => {
  const contentStyles: React.CSSProperties = {
    flex: 1,
    overflow: 'auto', // Enable full vertical scrolling
    padding: padding ? spacing.xl : 0,
    // Ensure content can scroll
    minHeight: 0,
  };

  return (
    <motion.div
      style={contentStyles}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.3, delay: 0.1 }}
    >
      {children}
    </motion.div>
  );
};

interface NavItemProps {
  label: string;
  isActive?: boolean;
  onClick: () => void;
  icon?: React.ReactNode;
  count?: number;
}

export const NavItem: React.FC<NavItemProps> = ({
  label,
  isActive = false,
  onClick,
  icon,
  count,
}) => {
  const [isHovered, setIsHovered] = React.useState(false);

  const itemStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: spacing.md,
    padding: `${spacing.md} ${spacing.lg}`,
    margin: `0 ${spacing.sm}`,
    borderRadius: borderRadius.md,
    cursor: 'pointer',
    transition: transitions.fast,
    background: isActive
      ? 'rgba(99, 102, 241, 0.15)'
      : isHovered
        ? 'rgba(255, 255, 255, 0.05)'
        : 'transparent',
    color: isActive ? colors.primary : colors.textSecondary,
    border: isActive ? '1px solid rgba(99, 102, 241, 0.2)' : '1px solid transparent',
  };

  const labelStyles: React.CSSProperties = {
    flex: 1,
    fontSize: typography.sizes.sm,
    fontWeight: isActive ? typography.weights.medium : typography.weights.normal,
  };

  const countStyles: React.CSSProperties = {
    fontSize: typography.sizes.xs,
    color: colors.textMuted,
    background: 'rgba(255, 255, 255, 0.08)',
    padding: `2px ${spacing.sm}`,
    borderRadius: borderRadius.full,
    border: '1px solid rgba(255, 255, 255, 0.06)',
  };

  return (
    <motion.div
      style={itemStyles}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      whileHover={{ x: 4 }}
      whileTap={{ scale: 0.98 }}
      transition={{ duration: 0.15 }}
    >
      {icon}
      <span style={labelStyles}>{label}</span>
      {count !== undefined && count > 0 && (
        <span style={countStyles}>{count}</span>
      )}
    </motion.div>
  );
};
