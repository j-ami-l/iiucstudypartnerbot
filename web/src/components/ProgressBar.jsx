import React from 'react';

/**
 * 6px accessible progress bar.
 * UI_PORTAL.md Section 4 & 7: role="progressbar", aria-valuenow.
 */
export default function ProgressBar({ value = 0, max = 100, className = '', color = 'var(--accent)' }) {
  const clamped = Math.max(0, Math.min(max, Number(value) || 0));
  const percent = max > 0 ? Math.round((clamped / max) * 100) : 0;

  return (
    <div
      role="progressbar"
      aria-valuenow={clamped}
      aria-valuemin={0}
      aria-valuemax={max}
      className={`portal-progress-track ${className}`.trim()}
    >
      <div
        className="portal-progress-fill"
        style={{ width: `${percent}%`, backgroundColor: color }}
      />
    </div>
  );
}
