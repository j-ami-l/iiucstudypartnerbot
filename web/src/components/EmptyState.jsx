import React from 'react';

export default function EmptyState({
  icon = '📚',
  title = 'No items found',
  description = 'Send a photo of your notes to the bot to get started.',
  actionText,
  actionHref,
  onAction,
}) {
  return (
    <div className="empty-state">
      <div className="empty-icon">{icon}</div>
      <h3 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.4rem' }}>{title}</h3>
      <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', marginBottom: '1.25rem', maxWidth: '420px', margin: '0 auto 1.25rem' }}>
        {description}
      </p>
      {actionHref && (
        <a
          href={actionHref}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          {actionText || 'Open Telegram Bot'}
        </a>
      )}
      {onAction && !actionHref && (
        <button onClick={onAction} className="btn btn-primary">
          {actionText || 'Continue'}
        </button>
      )}
    </div>
  );
}
