import React from 'react';

/**
 * Minimal SVG/CSS bar chart for weekly accuracy trends.
 * No external charting libraries per AGENT_PORTAL.md Section 9.
 */
export default function Bars({ weekly = [] }) {
  if (!weekly || weekly.length === 0) {
    return (
      <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textAlign: 'center', padding: '1rem 0' }}>
        No weekly quiz history yet.
      </div>
    );
  }

  const maxHeight = 120;

  return (
    <div style={{ marginTop: '1rem', width: '100%' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-end',
          justifyContent: 'space-between',
          gap: '0.5rem',
          height: `${maxHeight + 20}px`,
          padding: '0.5rem 0.5rem 0',
          borderBottom: '1px solid var(--border-color)',
        }}
      >
        {weekly.map((item, idx) => {
          const acc = Math.max(0, Math.min(100, item.accuracy_percent || 0));
          const heightPx = Math.max(8, Math.round((acc / 100) * maxHeight));
          const isZero = item.attempts === 0;

          // Color gradient according to score
          let barBg = '#3b82f6';
          if (acc >= 75) barBg = '#10b981';
          else if (acc < 50 && !isZero) barBg = '#f43f5e';
          else if (isZero) barBg = 'rgba(255, 255, 255, 0.08)';

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
                  fontWeight: 700,
                  color: isZero ? 'var(--text-muted)' : 'var(--text-primary)',
                  marginBottom: '0.25rem',
                }}
              >
                {isZero ? '-' : `${acc}%`}
              </div>
              <div
                style={{
                  width: '100%',
                  maxWidth: '36px',
                  height: `${heightPx}px`,
                  backgroundColor: barBg,
                  borderRadius: '4px 4px 0 0',
                  transition: 'height 0.4s ease, background-color 0.3s ease',
                  boxShadow: !isZero ? '0 0 10px rgba(59, 130, 246, 0.2)' : 'none',
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
          padding: '0.5rem 0.5rem 0',
        }}
      >
        {weekly.map((item, idx) => (
          <div
            key={item.week || idx}
            style={{
              flex: 1,
              textAlign: 'center',
              fontSize: '0.7rem',
              color: 'var(--text-secondary)',
              fontWeight: 600,
              overflow: 'hidden',
              textOverflow: 'ellipsis',
              whiteSpace: 'nowrap',
            }}
          >
            {item.week}
          </div>
        ))}
      </div>
    </div>
  );
}
