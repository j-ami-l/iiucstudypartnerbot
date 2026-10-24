import React from 'react';

/**
 * Bento-style Card surface with noir border and gradient background.
 * UI_PORTAL.md Section 1 & 4.
 */
export default function Card({ children, className = '', onClick, clickable = false, id }) {
  const classes = [
    'portal-card',
    clickable ? 'card-clickable' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div id={id} className={classes} onClick={onClick}>
      {children}
    </div>
  );
}
