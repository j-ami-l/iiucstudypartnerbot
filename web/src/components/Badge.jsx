import React from 'react';

/**
 * Small pill badge for status, score, language, or topic tags.
 * Variants: 'neutral', 'ok', 'warn', 'accent'
 */
export default function Badge({ children, variant = 'neutral', className = '' }) {
  return (
    <span className={`portal-badge badge-${variant} ${className}`.trim()}>
      {children}
    </span>
  );
}
