import React from 'react';
import { colors, borderRadius, spacing, gradients } from '../../styles/theme';

interface SkeletonProps {
  width?: string | number;
  height?: string | number;
  variant?: 'text' | 'rectangular' | 'circular';
  style?: React.CSSProperties;
}

export const Skeleton: React.FC<SkeletonProps> = ({
  width = '100%',
  height = 16,
  variant = 'text',
  style,
}) => {
  const getVariantStyles = (): React.CSSProperties => {
    switch (variant) {
      case 'circular':
        return {
          borderRadius: '50%',
          width: typeof width === 'number' ? width : 40,
          height: typeof height === 'number' ? height : 40,
        };
      case 'rectangular':
        return {
          borderRadius: borderRadius.md,
        };
      default:
        return {
          borderRadius: borderRadius.sm,
        };
    }
  };

  return (
    <div
      style={{
        width,
        height,
        background: 'rgba(255, 255, 255, 0.04)',
        position: 'relative',
        overflow: 'hidden',
        ...getVariantStyles(),
        ...style,
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: gradients.shimmer,
          animation: 'shimmer 1.5s infinite',
        }}
      />
    </div>
  );
};

// Skeleton card for loading states
interface SkeletonCardProps {
  lines?: number;
  showHeader?: boolean;
  showChart?: boolean;
}

export const SkeletonCard: React.FC<SkeletonCardProps> = ({
  lines = 3,
  showHeader = true,
  showChart = false,
}) => {
  return (
    <div
      style={{
        background: gradients.card,
        backdropFilter: 'blur(16px)',
        borderRadius: borderRadius.lg,
        border: `1px solid ${colors.glassBorder}`,
        padding: spacing.lg,
      }}
    >
      {showHeader && (
        <div style={{ marginBottom: spacing.lg }}>
          <Skeleton width="60%" height={24} style={{ marginBottom: spacing.sm }} />
          <Skeleton width="40%" height={14} />
        </div>
      )}

      {showChart && (
        <Skeleton
          variant="rectangular"
          width="100%"
          height={200}
          style={{ marginBottom: spacing.lg }}
        />
      )}

      {Array.from({ length: lines }).map((_, i) => (
        <Skeleton
          key={i}
          width={i === lines - 1 ? '70%' : '100%'}
          height={14}
          style={{ marginBottom: i < lines - 1 ? spacing.sm : 0 }}
        />
      ))}
    </div>
  );
};

// Research loading skeleton
export const ResearchSkeleton: React.FC = () => {
  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: spacing.xl }}>
      {/* Company info card skeleton */}
      <div
        style={{
          background: gradients.card,
          backdropFilter: 'blur(16px)',
          borderRadius: borderRadius.lg,
          border: `1px solid ${colors.glassBorder}`,
          padding: spacing.lg,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: spacing.lg }}>
          <div>
            <Skeleton width={200} height={28} style={{ marginBottom: spacing.sm }} />
            <div style={{ display: 'flex', gap: spacing.sm }}>
              <Skeleton width={80} height={22} variant="rectangular" />
              <Skeleton width={100} height={22} />
            </div>
          </div>
          <div style={{ display: 'flex', gap: spacing.sm }}>
            <Skeleton width={80} height={32} variant="rectangular" />
            <Skeleton width={80} height={32} variant="rectangular" />
          </div>
        </div>

        <Skeleton width="100%" height={14} style={{ marginBottom: spacing.sm }} />
        <Skeleton width="95%" height={14} style={{ marginBottom: spacing.sm }} />
        <Skeleton width="80%" height={14} style={{ marginBottom: spacing.xl }} />

        <Skeleton width={100} height={12} style={{ marginBottom: spacing.md }} />
        {[1, 2, 3].map((i) => (
          <div key={i} style={{ display: 'flex', alignItems: 'center', gap: spacing.md, marginBottom: spacing.sm }}>
            <Skeleton variant="circular" width={6} height={6} />
            <Skeleton width={`${80 - i * 10}%`} height={14} />
          </div>
        ))}

        <div
          style={{
            background: 'rgba(99, 102, 241, 0.08)',
            borderLeft: `3px solid ${colors.primary}`,
            padding: spacing.lg,
            borderRadius: `0 ${borderRadius.md} ${borderRadius.md} 0`,
            marginTop: spacing.lg,
          }}
        >
          <Skeleton width={120} height={12} style={{ marginBottom: spacing.sm }} />
          <Skeleton width="90%" height={16} />
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: spacing.md,
            marginTop: spacing.lg,
          }}
        >
          {[1, 2, 3].map((i) => (
            <div
              key={i}
              style={{
                background: colors.glass,
                padding: spacing.md,
                borderRadius: borderRadius.md,
                border: `1px solid ${colors.glassBorder}`,
                textAlign: 'center',
              }}
            >
              <Skeleton width={60} height={10} style={{ margin: '0 auto', marginBottom: spacing.xs }} />
              <Skeleton width={80} height={14} style={{ margin: '0 auto' }} />
            </div>
          ))}
        </div>
      </div>

      {/* Chart skeleton */}
      <div
        style={{
          background: gradients.card,
          backdropFilter: 'blur(16px)',
          borderRadius: borderRadius.lg,
          border: `1px solid ${colors.glassBorder}`,
          padding: spacing.lg,
        }}
      >
        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: spacing.lg }}>
          <div>
            <Skeleton width={180} height={18} style={{ marginBottom: spacing.xs }} />
            <Skeleton width={240} height={12} />
          </div>
          <div style={{ display: 'flex', gap: spacing.md }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
              <Skeleton variant="circular" width={8} height={8} />
              <Skeleton width={60} height={12} />
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: spacing.xs }}>
              <Skeleton variant="circular" width={8} height={8} />
              <Skeleton width={70} height={12} />
            </div>
          </div>
        </div>

        <div
          style={{
            background: 'rgba(0, 0, 0, 0.2)',
            borderRadius: borderRadius.md,
            padding: spacing.md,
            height: 280,
            position: 'relative',
          }}
        >
          {/* Fake scatter points */}
          {[
            { left: '20%', top: '30%' },
            { left: '35%', top: '45%' },
            { left: '45%', top: '35%' },
            { left: '55%', top: '50%' },
            { left: '65%', top: '40%' },
            { left: '75%', top: '55%' },
            { left: '50%', top: '42%' },
          ].map((pos, i) => (
            <Skeleton
              key={i}
              variant="circular"
              width={i === 6 ? 16 : 10}
              height={i === 6 ? 16 : 10}
              style={{
                position: 'absolute',
                left: pos.left,
                top: pos.top,
                background: i === 6 ? 'rgba(6, 182, 212, 0.3)' : 'rgba(255, 255, 255, 0.08)',
              }}
            />
          ))}
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(4, 1fr)',
            gap: spacing.md,
            marginTop: spacing.lg,
          }}
        >
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              style={{
                background: colors.glass,
                border: `1px solid ${colors.glassBorder}`,
                borderRadius: borderRadius.md,
                padding: spacing.md,
                textAlign: 'center',
              }}
            >
              <Skeleton width={80} height={10} style={{ margin: '0 auto', marginBottom: spacing.xs }} />
              <Skeleton width={60} height={16} style={{ margin: '0 auto' }} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
