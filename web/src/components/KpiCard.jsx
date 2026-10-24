import React from 'react';

/**
 * KPI Metric Card for Dashboard (feature P3b).
 * Label, large tabular value, optional footer (progress bar or hint).
 */
export default function KpiCard({ label, value, subtext, footer, highlight = false, valueColor }) {
  return (
    <div className={`portal-kpi-card ${highlight ? 'kpi-highlight' : ''}`}>
      <div className="kpi-label">{label}</div>
      <div className="kpi-value" style={valueColor ? { color: valueColor } : undefined}>
        {value}
      </div>
      {footer ? (
        <div className="kpi-footer">{footer}</div>
      ) : subtext ? (
        <div className="kpi-subtext">{subtext}</div>
      ) : null}
    </div>
  );
}
