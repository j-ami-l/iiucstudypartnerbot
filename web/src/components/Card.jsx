import React from 'react';

export default function Card({ children, className = '', onClick, clickable = false }) {
  const classes = ['card', clickable ? 'card-clickable' : '', className]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={classes} onClick={onClick}>
      {children}
    </div>
  );
}
