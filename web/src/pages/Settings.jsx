import React, { useState } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Icon from '../components/Icon';

/**
 * Settings page — UI_PORTAL.md Section 5.4
 * - Cards for student name and language (read only)
 * - Log out button (secondary style, not red)
 * - Privacy statement: "Photos are not stored. The AI-generated summary and quiz are saved, and only you can see them."
 */
export default function Settings({ user, onLogout }) {
  const [loggingOut, setLoggingOut] = useState(false);
  const [loggedOut, setLoggedOut] = useState(false);

  const handleLogout = async () => {
    setLoggingOut(true);
    try {
      await api.logout();
    } catch {
      // Ignore network errors on logout
    }
    setLoggingOut(false);
    setLoggedOut(true);
    if (onLogout) {
      onLogout();
    }
  };

  const botUsername = user?.bot_username || 'iiucstudypartnerbot';
  const botBaseUrl = `https://t.me/${botUsername}`;

  if (loggedOut) {
    return (
      <div className="portal-page" style={{ maxWidth: '480px', margin: '40px auto 0' }}>
        <Card style={{ textAlign: 'center', padding: '36px 20px' }}>
          <div style={{ fontSize: '36px', marginBottom: '12px' }}>👋</div>
          <h2 className="portal-section-title" style={{ marginBottom: '8px' }}>
            Logged Out Successfully
          </h2>
          <p style={{ color: 'var(--text-2)', fontSize: '14px', marginBottom: '24px', lineHeight: 1.6 }}>
            Your session has ended. To sign back in, send <code>/portal</code> to the bot in Telegram.
          </p>
          <a
            href={botBaseUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="portal-btn-primary"
            style={{ width: '100%' }}
          >
            Open Bot in Telegram
          </a>
        </Card>
      </div>
    );
  }

  return (
    <div className="portal-page" style={{ maxWidth: '600px', margin: '0 auto' }}>
      <div style={{ marginBottom: '24px' }}>
        <h1 className="portal-page-title">Settings</h1>
        <p className="portal-page-subtitle">Your student profile and session settings.</p>
      </div>

      {/* Profile Card */}
      <Card style={{ marginBottom: '20px' }}>
        <h2 className="portal-section-title" style={{ marginBottom: '16px' }}>
          Student Profile
        </h2>

        <div className="settings-row">
          <span className="settings-label">Name</span>
          <span className="settings-val">{user?.name || 'Anonymous Student'}</span>
        </div>

        <div className="settings-row">
          <span className="settings-label">Language</span>
          <Badge variant="neutral">
            {user?.language === 'bn' ? 'বাংলা (Bengali)' : 'English'}
          </Badge>
        </div>

        <div className="settings-row">
          <span className="settings-label">Telegram Bot</span>
          <a
            href={botBaseUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{ color: 'var(--accent-light)', fontSize: '14px', fontWeight: 500 }}
          >
            @{botUsername}
          </a>
        </div>
      </Card>

      {/* Session / Log out Card */}
      <Card style={{ marginBottom: '20px' }}>
        <h2 className="portal-section-title" style={{ marginBottom: '12px' }}>
          Session
        </h2>
        <p style={{ color: 'var(--text-2)', fontSize: '13px', marginBottom: '16px' }}>
          Log out of this browser. You can request a fresh login link anytime with <code>/portal</code>.
        </p>
        <button
          onClick={handleLogout}
          disabled={loggingOut}
          className="portal-btn-secondary"
          type="button"
        >
          <Icon name="logout" size={16} />
          <span>{loggingOut ? 'Logging out…' : 'Log out'}</span>
        </button>
      </Card>

      {/* Short privacy statement per UI_PORTAL.md 5.4 */}
      <p className="privacy-notice">
        Photos are not stored. The AI-generated summary and quiz are saved, and only you can see them.
      </p>
    </div>
  );
}
