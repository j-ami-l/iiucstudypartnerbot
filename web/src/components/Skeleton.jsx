import React from 'react';

/**
 * Skeleton loading placeholders in the exact shape of real cards.
 * UI_PORTAL.md Section 4 & 7: Shimmer-free subtle dark blocks.
 */
export function SkeletonBlock({ height = 20, width = '100%', radius = 8, className = '' }) {
  return (
    <div
      className={`portal-skeleton-block ${className}`.trim()}
      style={{
        height: typeof height === 'number' ? `${height}px` : height,
        width: typeof width === 'number' ? `${width}px` : width,
        borderRadius: typeof radius === 'number' ? `${radius}px` : radius,
      }}
      aria-hidden="true"
    />
  );
}

export function NoteCardSkeleton() {
  return (
    <div className="portal-note-card skeleton-note-card" aria-hidden="true">
      <div className="note-card-top">
        <SkeletonBlock height={20} width="65%" />
        <div style={{ display: 'flex', gap: '6px' }}>
          <SkeletonBlock height={18} width={34} radius={999} />
          <SkeletonBlock height={18} width={50} radius={999} />
        </div>
      </div>
      <div className="note-card-bottom" style={{ marginTop: '14px' }}>
        <SkeletonBlock height={14} width="35%" />
        <SkeletonBlock height={14} width="25%" />
      </div>
    </div>
  );
}

export function KpiCardSkeleton() {
  return (
    <div className="portal-kpi-card skeleton-kpi-card" aria-hidden="true">
      <SkeletonBlock height={14} width="50%" />
      <SkeletonBlock height={32} width="40%" style={{ marginTop: '8px' }} />
      <SkeletonBlock height={8} width="80%" style={{ marginTop: '8px' }} />
    </div>
  );
}

export default function Skeleton({ count = 3, type = 'note' }) {
  const items = Array.from({ length: count });
  return (
    <div className="skeleton-list" aria-label="Loading content...">
      {items.map((_, i) =>
        type === 'kpi' ? (
          <KpiCardSkeleton key={i} />
        ) : (
          <NoteCardSkeleton key={i} />
        )
      )}
    </div>
  );
}
