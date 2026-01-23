import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { HistoryEntry } from '../types';
import { colors, typography, spacing, borderRadius, transitions, glassEffect } from '../styles/theme';

interface HistoryListProps {
  entries: HistoryEntry[];
  onSelect: (entry: HistoryEntry) => void;
  onDelete: (id: string) => void;
  selectedId?: string;
  variant?: 'sidebar' | 'full';
}

export const HistoryList: React.FC<HistoryListProps> = ({
  entries,
  onSelect,
  onDelete,
  selectedId,
  variant = 'sidebar',
}) => {
  if (entries.length === 0) {
    return (
      <div style={emptyStateStyles}>
        <div style={emptyIconStyles}>
          <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke={colors.textMuted} strokeWidth="1.5">
            <path d="M9 12h6M9 16h6M17 21H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <p style={emptyTextStyles}>No reports yet</p>
        <p style={emptySubtextStyles}>Research a company to get started</p>
      </div>
    );
  }

  // Full variant uses grid layout with staggered animation
  if (variant === 'full') {
    return (
      <motion.div
        style={gridStyles}
        initial="hidden"
        animate="visible"
        variants={{
          hidden: { opacity: 0 },
          visible: {
            opacity: 1,
            transition: { staggerChildren: 0.06 },
          },
        }}
      >
        {entries.map((entry) => (
          <motion.div
            key={entry.id}
            variants={{
              hidden: { opacity: 0, y: 20 },
              visible: { opacity: 1, y: 0 },
            }}
          >
            <HistoryCard
              entry={entry}
              isSelected={selectedId === entry.id}
              onSelect={() => onSelect(entry)}
              onDelete={() => onDelete(entry.id)}
            />
          </motion.div>
        ))}
      </motion.div>
    );
  }

  // Sidebar variant uses compact list
  return (
    <div style={listStyles}>
      {entries.map((entry) => (
        <HistoryItemCompact
          key={entry.id}
          entry={entry}
          isSelected={selectedId === entry.id}
          onSelect={() => onSelect(entry)}
          onDelete={() => onDelete(entry.id)}
        />
      ))}
    </div>
  );
};

// Full-width card for History page grid
interface HistoryCardProps {
  entry: HistoryEntry;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

const HistoryCard: React.FC<HistoryCardProps> = ({
  entry,
  isSelected,
  onSelect,
  onDelete,
}) => {
  const [isHovered, setIsHovered] = useState(false);

  const emailCount = Object.keys(entry.emails || {}).length;
  const hasReport = !!entry.pdfPath;
  const servicesCount = entry.research.services?.length || 0;
  const keyMetricsCount = entry.research.keyMetrics?.filter(m => m).length || 0;

  const truncateText = (text: string, maxLength: number) => {
    if (text.length <= maxLength) return text;
    return text.slice(0, maxLength).trim() + '...';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  };

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
    });
  };

  const cardStyles: React.CSSProperties = {
    ...glassEffect.elevated,
    padding: 0,
    borderRadius: borderRadius.xl,
    cursor: 'pointer',
    position: 'relative',
    display: 'flex',
    flexDirection: 'column',
    overflow: 'hidden',
    border: isSelected
      ? '1px solid rgba(99, 102, 241, 0.5)'
      : '1px solid rgba(255, 255, 255, 0.08)',
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete();
  };

  return (
    <motion.div
      style={cardStyles}
      onClick={onSelect}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      whileHover={{ y: -4, boxShadow: '0 16px 48px rgba(0, 0, 0, 0.4)' }}
      transition={{ duration: 0.2 }}
    >
      {/* Top highlight */}
      <div style={{
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        height: '1px',
        background: 'linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.15) 50%, transparent 100%)',
        pointerEvents: 'none',
      }} />

      {/* Card Header with company icon */}
      <div style={{
        padding: spacing.lg,
        paddingBottom: spacing.md,
        display: 'flex',
        alignItems: 'flex-start',
        gap: spacing.md,
        borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
      }}>
        {/* Company Avatar */}
        <div style={{
          width: 48,
          height: 48,
          borderRadius: borderRadius.lg,
          background: 'linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%)',
          border: '1px solid rgba(99, 102, 241, 0.25)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: typography.sizes.lg,
          fontWeight: typography.weights.bold,
          color: colors.primary,
          flexShrink: 0,
        }}>
          {entry.companyName.charAt(0).toUpperCase()}
        </div>

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{
            fontSize: typography.sizes.md,
            fontWeight: typography.weights.semibold,
            color: colors.textPrimary,
            marginBottom: '4px',
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            whiteSpace: 'nowrap',
          }}>
            {entry.companyName}
          </div>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: spacing.sm,
            fontSize: typography.sizes.xs,
            color: colors.textMuted,
          }}>
            <span style={{
              padding: '2px 8px',
              background: 'rgba(99, 102, 241, 0.1)',
              borderRadius: borderRadius.sm,
              color: colors.primary,
              fontWeight: typography.weights.medium,
            }}>
              {entry.research.industry}
            </span>
            {entry.research.location && entry.research.location !== 'Unknown' && (
              <span style={{ display: 'flex', alignItems: 'center', gap: '3px' }}>
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z" />
                  <circle cx="12" cy="10" r="3" />
                </svg>
                {entry.research.location}
              </span>
            )}
          </div>
        </div>

        {/* Status indicators */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', alignItems: 'flex-end' }}>
          {hasReport && <StatusBadge type="report" />}
          {emailCount > 0 && <StatusBadge type="emails" count={emailCount} />}
        </div>
      </div>

      {/* Description */}
      <div style={{
        padding: `${spacing.md} ${spacing.lg}`,
        fontSize: typography.sizes.sm,
        color: colors.textSecondary,
        lineHeight: typography.lineHeights.relaxed,
        display: '-webkit-box',
        WebkitLineClamp: 2,
        WebkitBoxOrient: 'vertical',
        overflow: 'hidden',
        minHeight: '52px',
      } as React.CSSProperties}>
        {truncateText(entry.research.description, 160)}
      </div>

      {/* Competitive advantage highlight */}
      {entry.research.competitiveAdvantage && (
        <div style={{
          margin: `0 ${spacing.lg}`,
          marginBottom: spacing.md,
          padding: spacing.md,
          background: 'rgba(99, 102, 241, 0.08)',
          borderLeft: '3px solid rgba(99, 102, 241, 0.5)',
          borderRadius: `0 ${borderRadius.sm} ${borderRadius.sm} 0`,
          fontSize: typography.sizes.xs,
          color: colors.textSecondary,
          lineHeight: 1.5,
        }}>
          <span style={{ color: colors.primary, fontWeight: typography.weights.medium }}>Edge: </span>
          {truncateText(entry.research.competitiveAdvantage, 100)}
        </div>
      )}

      {/* Services preview */}
      {servicesCount > 0 && (
        <div style={{
          padding: `0 ${spacing.lg}`,
          paddingBottom: spacing.md,
          display: 'flex',
          flexWrap: 'wrap',
          gap: '6px',
        }}>
          {entry.research.services.slice(0, 3).map((service, idx) => (
            <span key={idx} style={{
              fontSize: '10px',
              padding: '3px 8px',
              background: 'rgba(255, 255, 255, 0.04)',
              border: '1px solid rgba(255, 255, 255, 0.06)',
              borderRadius: borderRadius.full,
              color: colors.textMuted,
            }}>
              {truncateText(service, 25)}
            </span>
          ))}
          {servicesCount > 3 && (
            <span style={{
              fontSize: '10px',
              padding: '3px 8px',
              color: colors.textMuted,
            }}>
              +{servicesCount - 3} more
            </span>
          )}
        </div>
      )}

      {/* Metrics Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(4, 1fr)',
        gap: '1px',
        background: 'rgba(255, 255, 255, 0.04)',
        borderTop: '1px solid rgba(255, 255, 255, 0.04)',
      }}>
        <MetricCell
          label="Founded"
          value={entry.research.yearFounded || '-'}
          icon="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
        />
        <MetricCell
          label="Team"
          value={entry.research.employeeCount || '-'}
          icon="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0z"
        />
        <MetricCell
          label="Services"
          value={`${servicesCount}`}
          icon="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
        />
        <MetricCell
          label="Insights"
          value={`${keyMetricsCount}`}
          icon="M13 10V3L4 14h7v7l9-11h-7z"
          highlight
        />
      </div>

      {/* Footer with date */}
      <div style={{
        padding: `${spacing.sm} ${spacing.lg}`,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        background: 'rgba(0, 0, 0, 0.15)',
        borderTop: '1px solid rgba(255, 255, 255, 0.04)',
      }}>
        <div style={{
          fontSize: typography.sizes.xs,
          color: colors.textMuted,
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
        }}>
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M12 6v6l4 2" />
          </svg>
          {formatDate(entry.createdAt)} at {formatTime(entry.createdAt)}
        </div>
        <motion.button
          style={{
            width: 24,
            height: 24,
            borderRadius: borderRadius.sm,
            background: 'rgba(239, 68, 68, 0.1)',
            border: '1px solid rgba(239, 68, 68, 0.2)',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          onClick={handleDelete}
          title="Delete"
          initial={{ opacity: 0 }}
          animate={{ opacity: isHovered ? 1 : 0 }}
          whileHover={{ background: 'rgba(239, 68, 68, 0.2)' }}
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={colors.red} strokeWidth="2">
            <path d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
          </svg>
        </motion.button>
      </div>
    </motion.div>
  );
};

// Metric Cell component for the grid
const MetricCell: React.FC<{ label: string; value: string; icon: string; highlight?: boolean }> = ({
  label, value, icon, highlight
}) => (
  <div style={{
    padding: spacing.md,
    background: highlight ? 'rgba(99, 102, 241, 0.08)' : 'rgba(0, 0, 0, 0.1)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    gap: '4px',
  }}>
    <svg
      width="14" height="14" viewBox="0 0 24 24" fill="none"
      stroke={highlight ? colors.primary : colors.textMuted} strokeWidth="1.5"
      style={{ opacity: 0.7 }}
    >
      <path d={icon} />
    </svg>
    <span style={{
      fontSize: typography.sizes.sm,
      fontWeight: typography.weights.semibold,
      color: highlight ? colors.primary : colors.textPrimary,
    }}>
      {value}
    </span>
    <span style={{
      fontSize: '9px',
      color: colors.textMuted,
      textTransform: 'uppercase',
      letterSpacing: '0.5px',
    }}>
      {label}
    </span>
  </div>
);

// Compact item for sidebar
interface HistoryItemCompactProps {
  entry: HistoryEntry;
  isSelected: boolean;
  onSelect: () => void;
  onDelete: () => void;
}

const HistoryItemCompact: React.FC<HistoryItemCompactProps> = ({
  entry,
  isSelected,
  onSelect,
  onDelete,
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [showDelete, setShowDelete] = useState(false);

  const emailCount = Object.keys(entry.emails || {}).length;
  const hasReport = !!entry.pdfPath;

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days === 0) {
      return 'Today';
    } else if (days === 1) {
      return 'Yesterday';
    } else if (days < 7) {
      return `${days}d ago`;
    } else {
      return date.toLocaleDateString('en-US', {
        month: 'short',
        day: 'numeric',
      });
    }
  };

  const itemStyles: React.CSSProperties = {
    padding: `${spacing.sm} ${spacing.md}`,
    borderRadius: borderRadius.md,
    cursor: 'pointer',
    transition: transitions.fast,
    background: isSelected
      ? 'rgba(99, 102, 241, 0.15)'
      : isHovered
        ? 'rgba(255, 255, 255, 0.05)'
        : 'transparent',
    border: `1px solid ${isSelected ? 'rgba(99, 102, 241, 0.3)' : 'transparent'}`,
    marginBottom: spacing.xs,
    position: 'relative',
  };

  const headerStyles: React.CSSProperties = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '2px',
  };

  const nameStyles: React.CSSProperties = {
    fontSize: typography.sizes.sm,
    fontWeight: typography.weights.medium,
    color: colors.textPrimary,
    flex: 1,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
  };

  const dateStyles: React.CSSProperties = {
    fontSize: '10px',
    color: colors.textMuted,
    flexShrink: 0,
    marginLeft: spacing.sm,
  };

  const bottomRowStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: spacing.sm,
  };

  const industryStyles: React.CSSProperties = {
    fontSize: typography.sizes.xs,
    color: colors.textSecondary,
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    flex: 1,
  };

  const miniIndicatorsStyles: React.CSSProperties = {
    display: 'flex',
    gap: '4px',
    alignItems: 'center',
  };

  const miniDotStyles = (color: string): React.CSSProperties => ({
    width: 6,
    height: 6,
    borderRadius: '50%',
    background: color,
  });

  const deleteButtonStyles: React.CSSProperties = {
    position: 'absolute',
    top: '50%',
    right: spacing.sm,
    transform: 'translateY(-50%)',
    width: 20,
    height: 20,
    borderRadius: borderRadius.sm,
    background: 'rgba(239, 68, 68, 0.15)',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    opacity: showDelete ? 1 : 0,
    transition: transitions.fast,
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete();
  };

  return (
    <div
      style={itemStyles}
      onClick={onSelect}
      onMouseEnter={() => {
        setIsHovered(true);
        setShowDelete(true);
      }}
      onMouseLeave={() => {
        setIsHovered(false);
        setShowDelete(false);
      }}
    >
      <div style={headerStyles}>
        <span style={nameStyles}>{entry.companyName}</span>
        <span style={dateStyles}>{formatDate(entry.createdAt)}</span>
      </div>
      <div style={bottomRowStyles}>
        <span style={industryStyles}>{entry.research.industry}</span>
        <div style={miniIndicatorsStyles}>
          {hasReport && <div style={miniDotStyles(colors.emerald)} title="Report Ready" />}
          {emailCount > 0 && <div style={miniDotStyles(colors.cyan)} title={`${emailCount} emails`} />}
        </div>
      </div>
      <button
        style={deleteButtonStyles}
        onClick={handleDelete}
        title="Delete"
      >
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={colors.red} strokeWidth="2">
          <path d="M18 6L6 18M6 6l12 12" />
        </svg>
      </button>
    </div>
  );
};

// Status badge component
interface StatusBadgeProps {
  type: 'report' | 'emails';
  count?: number;
}

const StatusBadge: React.FC<StatusBadgeProps> = ({ type, count }) => {
  const isReport = type === 'report';

  const badgeStyles: React.CSSProperties = {
    display: 'flex',
    alignItems: 'center',
    gap: '4px',
    padding: `${spacing.xs} ${spacing.sm}`,
    borderRadius: borderRadius.full,
    fontSize: '10px',
    fontWeight: typography.weights.medium,
    background: isReport
      ? 'rgba(16, 185, 129, 0.12)'
      : 'rgba(6, 182, 212, 0.12)',
    color: isReport ? colors.emerald : colors.cyan,
    border: `1px solid ${isReport ? 'rgba(16, 185, 129, 0.25)' : 'rgba(6, 182, 212, 0.25)'}`,
    textTransform: 'uppercase',
    letterSpacing: '0.3px',
  };

  return (
    <span style={badgeStyles}>
      {isReport ? (
        <>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M9 12l2 2 4-4" />
            <path d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          Report Ready
        </>
      ) : (
        <>
          <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
            <path d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          {count} Email{count !== 1 ? 's' : ''}
        </>
      )}
    </span>
  );
};

// Grid layout for full History page - larger cards for more data
const gridStyles: React.CSSProperties = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(420px, 1fr))',
  gap: spacing.xl,
  padding: spacing.md,
};

const listStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
};

const emptyStateStyles: React.CSSProperties = {
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: spacing['2xl'],
  textAlign: 'center',
};

const emptyIconStyles: React.CSSProperties = {
  marginBottom: spacing.md,
  opacity: 0.5,
};

const emptyTextStyles: React.CSSProperties = {
  fontSize: typography.sizes.base,
  fontWeight: typography.weights.medium,
  color: colors.textSecondary,
  marginBottom: spacing.xs,
};

const emptySubtextStyles: React.CSSProperties = {
  fontSize: typography.sizes.sm,
  color: colors.textMuted,
};
