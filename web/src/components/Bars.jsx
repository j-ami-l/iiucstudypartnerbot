import React from 'react';

/**
 * Minimal SVG/CSS bar chart for weekly accuracy trends.
 * UI_PORTAL.md Section 5.6: bars in --accent, axis text in --text-3.
 */
export default function Bars({ weekly = [] }) {
  if (!weekly || weekly.length === 0) {
    return (
      <div className="bars-empty" style={{ color: 'var(--text-3)', fontSize: '0.85rem', textAlign: 'center', padding: '1.5rem 0' }}>
        No weekly quiz history yet.
      </div>
    );
  }

  const maxHeight = 120;

  return (
    <div className="portal-bars-container" style={{ marginTop: '1rem', width: '100%' }}>
      <div
        className="portal-bars-chart"
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'space-between',
          gap: '0.5rem',
          height: `${maxHeight + 24}px`,
          padding: '0.5rem 0.5rem 0',
          borderBottom: '1px solid var(--card-border)',
        }}
      >
        {weekly.map((item, idx) => {
          const acc = Math.max(0, Math.min(100, item.accuracy_percent || 0));
          const heightPx = Math.max(8, Math.round((acc / 100) * maxHeight));
          const isZero = item.attempts === 0;

          return (
            <div
              key={item.week || idx}
              style={{
                flex: 1,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'flex-end',
                height: '100%',
              }}
            >
              <div
                style={{
                  fontSize: '0.72rem',
                  fontWeight: 600,
                  fontFamily: 'var(--font-head)',
                  color: isZero ? 'var(--text-3)' : 'var(--text)',
                  marginBottom: '0.25rem',
                }}
              >
                {isZero ? '—' : `${acc}%`}
              </div>
              <div
                style={{
                  width: '100%',
                  maxWidth: '32px',
                  height: `${heightPx}px`,
                  backgroundColor: isZero ? 'rgba(255, 255, 255, 0.04)' : 'var(--accent)',
                  borderRadius: '4px 4px 0 0',
                  boxShadow: !isZero ? '0 0 12px var(--accent-glow)' : 'none',
                }}
                title={`${item.week}: ${acc}% (${item.attempts} questions)`}
              />
            </div>
          );
        })}
      </div>

      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          gap: '0.5rem',
          marginTop: '0.5rem',
          padding: '0 0.5rem',
        }}
      >
        {weekly.map((item, idx) => (
          <div
            key={item.week || idx}
            style={{
              flex: 1,
              textAlign: 'center',
              fontSize: '0.7rem',
              color: 'var(--text-3)',
              fontFamily: 'var(--font-body)',
            }}
          >
            {item.week || `W${idx + 1}`}
          </div>
        ))}
      </div>
    </div>
  );
}
