import React from 'react';
import Icon from './Icon';

/**
 * ErrorState: Honest error states for 401, 404, and network errors.
 * UI_PORTAL.md Section 1, 4 & 5.5.
 */
export default function ErrorState({ error, onRetry, botUsername = 'iiucstudypartnerbot' }) {
  const is401 = error?.status === 401 || error?.detail === 'unauthorized';
  const botLink = `https://t.me/${botUsername || 'iiucstudypartnerbot'}`;

  if (is401) {
    return (
      <div className="portal-error-card">
        <div className="error-icon" aria-hidden="true">
          <Icon name="logout" size={24} color="var(--accent)" />
        </div>
        <h3 className="error-title">Session Ended</h3>
        <p className="error-desc">
          Your session ended. Send <code>/portal</code> to the bot to get a new link.
        </p>
        <div className="error-actions">
          <a
            href={botLink}
            target="_blank"
            rel="noopener noreferrer"
            className="portal-btn-primary"
          >
            Open Telegram Bot
          </a>
        </div>
      </div>
    );
  }

  const is404 =
    error?.status === 404 ||
    error?.detail === 'not_found' ||
    error?.detail === 'note_not_found';

  if (is404) {
    return (
      <div className="portal-error-card">
        <div className="error-icon" aria-hidden="true">
          <Icon name="alert" size={24} color="var(--warn)" />
        </div>
        <h3 className="error-title">Note Not Found</h3>
        <p className="error-desc">
          This study note does not exist or belongs to another user.
        </p>
        <div className="error-actions">
          <a href="/notes" className="portal-btn-secondary">
            Back to Notes
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="portal-error-card">
      <div className="error-icon" aria-hidden="true">
        <Icon name="alert" size={24} color="var(--accent)" />
      </div>
      <h3 className="error-title">Unable to Load Data</h3>
      <p className="error-desc">
        {error?.message || 'A network error occurred. Please try again.'}
      </p>
      {onRetry && (
        <div className="error-actions">
          <button onClick={onRetry} className="portal-btn-secondary" type="button">
            Try Again
          </button>
        </div>
      )}
    </div>
  );
}
