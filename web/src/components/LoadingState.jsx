import React from 'react';

export default function LoadingState({ message = 'Loading study data...' }) {
  return (
    <div style={{ textAlign: 'center', padding: '3rem 1rem' }}>
      <div className="spinner"></div>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginTop: '1rem' }}>
        {message}
      </p>
    </div>
  );
}
