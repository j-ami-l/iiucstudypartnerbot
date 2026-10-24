import React from 'react';

export default function ErrorState({ error, onRetry, botUsername = '' }) {
  const is401 = error?.status === 401 || error?.detail === 'unauthorized';
  const botLink = botUsername ? `https://t.me/${botUsername}` : 'https://t.me';

  if (is401) {
    return (
      <div className="empty-state" style={{ borderColor: 'rgba(239, 68, 68, 0.25)' }}>
        <div className="empty-icon">🔒</div>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.4rem', color: '#f87171' }}>
          Session Ended
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '1.25rem', maxWidth: '420px', margin: '0 auto 1.25rem' }}>
          Your session ended. Send <code>/portal</code> to the bot to get a new link.
        </p>
        <a
          href={botLink}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          Open Bot in Telegram
        </a>
      </div>
    );
  }

  const is404 = error?.status === 404 || error?.detail === 'not_found' || error?.detail === 'note_not_found';
  if (is404) {
    return (
      <div className="empty-state">
        <div className="empty-icon">🔍</div>
        <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.4rem' }}>
          Note Not Found
        </h3>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '1.25rem', maxWidth: '420px', margin: '0 auto 1.25rem' }}>
          This study note does not exist or belongs to another user.
        </p>
        <a href="/notes" className="btn btn-secondary">
          Back to Notes
        </a>
      </div>
    );
  }

  return (
    <div className="empty-state" style={{ borderColor: 'rgba(239, 68, 68, 0.25)' }}>
      <div className="empty-icon">⚠️</div>
      <h3 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.4rem', color: '#f87171' }}>
        Unable to Load Data
      </h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem', maxWidth: '420px', margin: '0 auto 1.25rem' }}>
        {error?.message || 'A network error occurred. Please try again.'}
      </p>
      {onRetry && (
        <button onClick={onRetry} className="btn btn-secondary">
          Try Again
        </button>
      )}
    </div>
  );
}
