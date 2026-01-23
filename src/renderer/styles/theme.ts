export const colors = {
  // Backgrounds - Deep charcoal base
  background: '#0a0d12',
  backgroundLight: '#0e1117', // The exact color from edits.md
  backgroundGradientStart: '#151a28',
  backgroundGradientEnd: '#0a0d12',
  backgroundElevated: '#14181f',

  // Black Glass / Liquid Glass effect colors
  blackGlass: 'rgba(14, 17, 23, 0.85)', // Deep charcoal with high opacity
  blackGlassLight: 'rgba(14, 17, 23, 0.7)',
  blackGlassSolid: 'rgba(10, 13, 18, 0.95)',

  // Glass panels - Enhanced for liquid glass effect
  glass: 'rgba(255, 255, 255, 0.03)',
  glassLight: 'rgba(255, 255, 255, 0.05)',
  glassHover: 'rgba(255, 255, 255, 0.08)',
  glassBorder: 'rgba(255, 255, 255, 0.08)', // Subtle crisp edge
  glassBorderHover: 'rgba(255, 255, 255, 0.15)',
  glassBorderActive: 'rgba(99, 102, 241, 0.5)',

  // Primary actions - Blurple gradient
  primary: '#6366f1',
  primaryLight: '#818cf8',
  primaryDark: '#4f46e5',
  secondary: '#8b5cf6',

  // Accents
  cyan: '#06b6d4',
  cyanLight: '#22d3ee',
  cyanDark: '#0891b2',
  emerald: '#10b981',
  emeraldLight: '#34d399',
  amber: '#f59e0b',
  amberLight: '#fbbf24',
  red: '#ef4444',
  redLight: '#f87171',

  // Text
  textPrimary: '#f8fafc',
  textSecondary: '#94a3b8',
  textMuted: '#64748b',
  textDisabled: '#475569',

  // Borders
  border: 'rgba(255, 255, 255, 0.08)',
  borderLight: 'rgba(255, 255, 255, 0.12)',

  // Chart colors
  chartPrimary: 'rgba(99, 102, 241, 0.8)',
  chartSecondary: 'rgba(139, 92, 246, 0.6)',
  chartCyan: 'rgba(6, 182, 212, 0.9)',
  chartGhost: 'rgba(148, 163, 184, 0.3)',
  chartBand: 'rgba(99, 102, 241, 0.12)',
};

export const gradients = {
  primary: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
  primaryHover: 'linear-gradient(135deg, #818cf8 0%, #a78bfa 100%)',
  primarySubtle: 'linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(139,92,246,0.1) 100%)',

  // Mesh gradients for behind glass elements
  meshPrimary: `
    radial-gradient(at 40% 20%, rgba(99, 102, 241, 0.15) 0px, transparent 50%),
    radial-gradient(at 80% 0%, rgba(139, 92, 246, 0.12) 0px, transparent 50%),
    radial-gradient(at 0% 50%, rgba(6, 182, 212, 0.08) 0px, transparent 50%),
    radial-gradient(at 80% 50%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
    radial-gradient(at 0% 100%, rgba(139, 92, 246, 0.1) 0px, transparent 50%)
  `,
  meshSubtle: `
    radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.08) 0px, transparent 50%),
    radial-gradient(at 100% 100%, rgba(6, 182, 212, 0.06) 0px, transparent 50%)
  `,
  meshCyan: `
    radial-gradient(at 50% 0%, rgba(6, 182, 212, 0.12) 0px, transparent 50%),
    radial-gradient(at 100% 50%, rgba(99, 102, 241, 0.08) 0px, transparent 50%)
  `,

  background: 'radial-gradient(ellipse 120% 80% at 50% -20%, #1e2436 0%, #0a0d12 60%)',
  backgroundAlt: 'radial-gradient(circle at 20% 80%, rgba(99,102,241,0.08) 0%, transparent 50%)',
  card: 'linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%)',
  cardHover: 'linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%)',
  glow: 'radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%)',
  glowCyan: 'radial-gradient(circle, rgba(6,182,212,0.2) 0%, transparent 70%)',
  shimmer: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.06) 50%, transparent 100%)',

  // Glass card internal gradient
  glassCard: 'linear-gradient(135deg, rgba(255,255,255,0.05) 0%, rgba(255,255,255,0.02) 50%, rgba(255,255,255,0.01) 100%)',
};

// Black Glass / Liquid Glass effect styles - EXACT spec from edits.md
export const glassEffect = {
  // Standard glass panel - matches edits.md exactly
  standard: {
    background: 'rgba(14, 17, 23, 0.7)',
    backdropFilter: 'blur(24px)',
    WebkitBackdropFilter: 'blur(24px)',
    border: '1px solid rgba(255, 255, 255, 0.08)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), inset 0 0 0 1px rgba(255, 255, 255, 0.05)',
  },
  // Elevated glass (more prominent) - enhanced version
  elevated: {
    background: 'rgba(14, 17, 23, 0.75)',
    backdropFilter: 'blur(24px)',
    WebkitBackdropFilter: 'blur(24px)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    boxShadow: '0 12px 40px rgba(0, 0, 0, 0.5), inset 0 0 0 1px rgba(255, 255, 255, 0.06)',
  },
  // Subtle glass (for nested elements)
  subtle: {
    background: 'rgba(14, 17, 23, 0.5)',
    backdropFilter: 'blur(16px)',
    WebkitBackdropFilter: 'blur(16px)',
    border: '1px solid rgba(255, 255, 255, 0.06)',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.3), inset 0 0 0 1px rgba(255, 255, 255, 0.03)',
  },
  // Glow effect for hover/active states
  glow: {
    background: 'rgba(14, 17, 23, 0.75)',
    backdropFilter: 'blur(24px)',
    WebkitBackdropFilter: 'blur(24px)',
    border: '1px solid rgba(99, 102, 241, 0.3)',
    boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 40px rgba(99, 102, 241, 0.15), inset 0 0 0 1px rgba(255, 255, 255, 0.05)',
  },
};

export const typography = {
  fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
  fontFamilyMono: "'JetBrains Mono', 'SF Mono', Monaco, 'Cascadia Code', monospace",

  sizes: {
    xs: '11px',
    sm: '13px',
    base: '14px',
    md: '15px',
    lg: '17px',
    xl: '20px',
    '2xl': '24px',
    '3xl': '30px',
    '4xl': '36px',
  },

  weights: {
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
  },

  lineHeights: {
    tight: 1.2,
    normal: 1.5,
    relaxed: 1.7,
  },
};

export const spacing = {
  xs: '4px',
  sm: '8px',
  md: '12px',
  lg: '16px',
  xl: '24px',
  '2xl': '32px',
  '3xl': '48px',
  '4xl': '64px',
};

export const borderRadius = {
  sm: '6px',
  md: '8px',
  lg: '12px',
  xl: '16px',
  '2xl': '20px',
  full: '9999px',
};

export const shadows = {
  sm: '0 1px 2px rgba(0, 0, 0, 0.4)',
  md: '0 4px 12px rgba(0, 0, 0, 0.4)',
  lg: '0 10px 24px rgba(0, 0, 0, 0.5)',
  xl: '0 20px 40px rgba(0, 0, 0, 0.6)',
  // Black glass specific shadows
  glass: '0 8px 32px rgba(0, 0, 0, 0.4)',
  glassElevated: '0 8px 32px rgba(0, 0, 0, 0.5), 0 0 0 1px rgba(255, 255, 255, 0.05) inset',
  inner: 'inset 0 1px 0 rgba(255, 255, 255, 0.05)',
  innerGlow: 'inset 0 0 20px rgba(99, 102, 241, 0.1)',
  glow: '0 0 30px rgba(99, 102, 241, 0.25)',
  glowCyan: '0 0 30px rgba(6, 182, 212, 0.25)',
  glowSubtle: '0 0 60px rgba(99, 102, 241, 0.1)',
  elevated: '0 8px 32px rgba(0, 0, 0, 0.4), 0 0 0 1px rgba(255, 255, 255, 0.05)',
};

export const transitions = {
  fast: '120ms cubic-bezier(0.4, 0, 0.2, 1)',
  normal: '200ms cubic-bezier(0.4, 0, 0.2, 1)',
  slow: '350ms cubic-bezier(0.4, 0, 0.2, 1)',
  spring: '400ms cubic-bezier(0.34, 1.56, 0.64, 1)',
  smooth: '300ms cubic-bezier(0.25, 0.1, 0.25, 1)',
};

// Blur values for backdrop-filter
export const blur = {
  sm: '8px',
  md: '12px',
  lg: '20px',
  xl: '24px',
  '2xl': '32px',
};
