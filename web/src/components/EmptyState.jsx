import React from 'react';

/**
 * EmptyState: Designed honest empty state for Dashboards and Lists.
 * UI_PORTAL.md Section 1, 4 & 5.1.
 */
export default function EmptyState({
  icon = '📚',
  title = 'No notes yet',
  description = 'Send a photo of your notes to the bot to get started.',
  actionText = 'Open Telegram Bot',
  actionHref,
  onAction,
}) {
  return (
    <div className="portal-empty-state">
      <div className="empty-state-icon" aria-hidden="true">
        {icon}
      </div>
      <h3 className="empty-state-title">{title}</h3>
      <p className="empty-state-desc">{description}</p>
      {actionHref && (
        <a
          href={actionHref}
          target="_blank"
          rel="noopener noreferrer"
          className="portal-btn-primary"
        >
          {actionText}
        </a>
      )}
      {onAction && !actionHref && (
        <button onClick={onAction} className="portal-btn-primary" type="button">
          {actionText}
        </button>
      )}
    </div>
  );
}
