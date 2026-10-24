import React, { useState } from 'react';
import { api } from '../api';
import Card from '../components/Card';

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
      <div style={{ maxWidth: '480px', margin: '2rem auto 0' }}>
        <Card style={{ textAlign: 'center', padding: '2.5rem 1.5rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👋</div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '0.6rem' }}>
            Logged Out Successfully
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '1.75rem', lineHeight: 1.6 }}>
            Your session cookie has been cleared. To sign back in, send <code>/portal</code> to the bot on Telegram.
          </p>
          <a
            href={botBaseUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="btn btn-primary btn-block"
          >
            Open Bot in Telegram
          </a>
        </Card>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '640px', margin: '0 auto' }}>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="title-xl">Account Settings</h1>
        <p className="subtitle">Manage your study partner profile and session.</p>
      </div>

      {/* Profile Card */}
      <Card style={{ marginBottom: '1.5rem' }}>
        <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>👤</span> Student Profile
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.85rem' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Student Name</span>
            <span style={{ fontWeight: 600 }}>{user?.name || 'Anonymous Student'}</span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '0.75rem', borderBottom: '1px solid var(--border-color)' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Preferred Language</span>
            <span className="badge badge-blue">
              {user?.language === 'bn' ? 'বাংলা (Bengali)' : 'English'}
            </span>
          </div>

          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Telegram Bot</span>
            <a
              href={botBaseUrl}
              target="_blank"
              rel="noopener noreferrer"
              style={{ color: 'var(--accent-primary)', fontSize: '0.9rem', fontWeight: 600 }}
            >
              @{botUsername}
            </a>
          </div>
        </div>
      </Card>

      {/* Privacy Notice Card */}
      <Card style={{ marginBottom: '1.5rem', background: 'rgba(255, 255, 255, 0.02)' }}>
        <h2 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.6rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>🛡️</span> Privacy & Security
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', lineHeight: 1.6 }}>
          SnapStudy AI prioritizes your privacy. Uploaded photos are processed directly in memory and
          are never stored on disk. Generated summaries, quiz attempts, and mistake history are stored
          securely in an encrypted SQLite database and are strictly isolated to your Telegram identity.
        </p>
      </Card>

      {/* Session Logout Card */}
      <Card>
        <h2 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.5rem' }}>
          Session Management
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.86rem', marginBottom: '1.25rem' }}>
          Signing out will invalidate your current session cookie on this browser.
        </p>
        <button
          onClick={handleLogout}
          disabled={loggingOut}
          className="btn btn-secondary"
          style={{ color: '#f87171', borderColor: 'rgba(248, 113, 113, 0.3)' }}
        >
          {loggingOut ? 'Signing Out...' : '🚪 Log Out of Portal'}
        </button>
      </Card>
    </div>
  );
}
