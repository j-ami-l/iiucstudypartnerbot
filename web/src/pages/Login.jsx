import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import Card from '../components/Card';
import Icon from '../components/Icon';

/**
 * Login page — UI_PORTAL.md Section 5.5
 * - Centered card on noir background
 * - Friendly verification message while exchanging token
 * - Expired link notice: "This link expired. Send /portal to the bot to get a new one."
 */
export default function Login({ onLoginSuccess }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [botUsername, setBotUsername] = useState('iiucstudypartnerbot');
  const exchangeAttemptedRef = useRef(false);

  useEffect(() => {
    if (exchangeAttemptedRef.current) return;
    exchangeAttemptedRef.current = true;

    const hash = window.location.hash || '';
    const token = hash.startsWith('#') ? hash.slice(1).trim() : hash.trim();

    if (window.location.hash) {
      window.history.replaceState(null, '', window.location.pathname + window.location.search);
    }

    // Step 1: Check existing session cookie
    api
      .getMe()
      .then((me) => {
        if (me?.bot_username) {
          setBotUsername(me.bot_username);
        }
        if (onLoginSuccess) onLoginSuccess();
        navigate('/dashboard', { replace: true });
      })
      .catch(async () => {
        // Step 2: No session cookie, exchange token if present
        if (!token) {
          setLoading(false);
          return;
        }

        try {
          await api.exchangeToken(token);
          if (onLoginSuccess) {
            await onLoginSuccess();
          }
          navigate('/dashboard', { replace: true });
        } catch (err) {
          try {
            const me = await api.getMe();
            if (me) {
              if (onLoginSuccess) await onLoginSuccess();
              navigate('/dashboard', { replace: true });
              return;
            }
          } catch {
            // Unauthenticated
          }

          setLoading(false);
          setErrorMsg('This link expired. Send /portal to the bot to get a new one.');
        }
      });
  }, [navigate, onLoginSuccess]);

  const botLink = `https://t.me/${botUsername || 'iiucstudypartnerbot'}`;

  return (
    <div className="portal-page" style={{ maxWidth: '440px', margin: '60px auto 0', padding: '0 16px' }}>
      <Card style={{ textAlign: 'center', padding: '40px 24px' }}>
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '16px' }}>
          <div className="brand-icon-wrap" style={{ width: '40px', height: '40px' }}>
            <Icon name="bolt" size={22} />
          </div>
        </div>

        <h1 className="portal-page-title" style={{ fontSize: '24px', marginBottom: '8px' }}>
          SnapStudy Portal
        </h1>

        {loading ? (
          <div style={{ marginTop: '20px' }}>
            <p style={{ color: 'var(--text-2)', fontSize: '14px', lineHeight: 1.5 }}>
              Verifying your login link and setting up your study dashboard…
            </p>
          </div>
        ) : errorMsg ? (
          <div style={{ marginTop: '16px' }}>
            <div style={{ color: 'var(--accent-light)', marginBottom: '12px' }}>
              <Icon name="alert" size={28} />
            </div>
            <p style={{ color: 'var(--text-2)', fontSize: '14px', lineHeight: 1.6, marginBottom: '24px' }}>
              {errorMsg}
            </p>
            <a
              href={botLink}
              target="_blank"
              rel="noopener noreferrer"
              className="portal-btn-primary"
              style={{ width: '100%' }}
            >
              Open Telegram Bot
            </a>
          </div>
        ) : (
          <div style={{ marginTop: '16px' }}>
            <p style={{ color: 'var(--text-2)', fontSize: '14px', lineHeight: 1.6, marginBottom: '24px' }}>
              To log in to your personal dashboard, send <code>/portal</code> to the bot in Telegram.
            </p>
            <a
              href={botLink}
              target="_blank"
              rel="noopener noreferrer"
              className="portal-btn-primary"
              style={{ width: '100%' }}
            >
              Open Telegram Bot
            </a>
          </div>
        )}
      </Card>
    </div>
  );
}
