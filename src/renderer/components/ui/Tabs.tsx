import React from 'react';
import { colors, borderRadius, typography, spacing, transitions } from '../../styles/theme';

interface Tab {
  id: string;
  label: string;
}

interface TabsProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  style?: React.CSSProperties;
}

export const Tabs: React.FC<TabsProps> = ({
  tabs,
  activeTab,
  onTabChange,
  style,
}) => {
  const containerStyles: React.CSSProperties = {
    display: 'flex',
    gap: spacing.sm,
    padding: spacing.xs,
    background: colors.glass,
    borderRadius: borderRadius.md,
    border: `1px solid ${colors.glassBorder}`,
    ...style,
  };

  return (
    <div style={containerStyles}>
      {tabs.map((tab) => (
        <TabButton
          key={tab.id}
          label={tab.label}
          isActive={activeTab === tab.id}
          onClick={() => onTabChange(tab.id)}
        />
      ))}
    </div>
  );
};

interface TabButtonProps {
  label: string;
  isActive: boolean;
  onClick: () => void;
}

const TabButton: React.FC<TabButtonProps> = ({ label, isActive, onClick }) => {
  const [isHovered, setIsHovered] = React.useState(false);

  const buttonStyles: React.CSSProperties = {
    flex: 1,
    padding: `${spacing.sm} ${spacing.md}`,
    borderRadius: borderRadius.sm,
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: isActive ? colors.textPrimary : colors.textSecondary,
    background: isActive
      ? 'rgba(99, 102, 241, 0.2)'
      : isHovered
        ? 'rgba(255, 255, 255, 0.05)'
        : 'transparent',
    border: 'none',
    cursor: 'pointer',
    transition: transitions.fast,
  };

  return (
    <button
      style={buttonStyles}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {label}
    </button>
  );
};
