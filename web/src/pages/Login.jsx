import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import Card from '../components/Card';
import LoadingState from '../components/LoadingState';

export default function Login({ onLoginSuccess }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [errorMsg, setErrorMsg] = useState(null);
  const [botUsername, setBotUsername] = useState('iiucstudypartnerbot');
  const exchangeAttemptedRef = useRef(false);

  useEffect(() => {
    // Prevent duplicate concurrent execution (e.g. React StrictMode)
    if (exchangeAttemptedRef.current) return;
    exchangeAttemptedRef.current = true;

    // Read the fragment after #
    const hash = window.location.hash || '';
    const token = hash.startsWith('#') ? hash.slice(1).trim() : hash.trim();

    // Clear fragment immediately from browser address bar
    if (window.location.hash) {
      window.history.replaceState(null, '', window.location.pathname + window.location.search);
    }

    // Step 1: Check if the user is ALREADY validated and has an active session cookie!
    api
      .getMe()
      .then((me) => {
        if (me?.bot_username) {
          setBotUsername(me.bot_username);
        }
        if (onLoginSuccess) onLoginSuccess();
        // Already logged in from Telegram validation -> go straight to dashboard!
        navigate('/dashboard', { replace: true });
      })
      .catch(async () => {
        // Step 2: Not logged in yet
        if (!token) {
          setLoading(false);
          return;
        }

        // Exchange single-use magic token for signed 7-day session cookie
        try {
          await api.exchangeToken(token);
          if (onLoginSuccess) {
            await onLoginSuccess();
          }
          navigate('/dashboard', { replace: true });
        } catch (err) {
          // Double-check if the session was established
          try {
            const me = await api.getMe();
            if (me) {
              if (onLoginSuccess) await onLoginSuccess();
              navigate('/dashboard', { replace: true });
              return;
            }
          } catch {
            // Truly unauthenticated
          }

          setLoading(false);
          if (err.status === 400) {
            setErrorMsg(
              'This link expired or has already been used. Send /portal to the bot to get a fresh link.'
            );
          } else {
            setErrorMsg(
              err.message || 'Unable to log in. Please try requesting a new link from the bot.'
            );
          }
        }
      });
  }, [navigate, onLoginSuccess]);

  const botLink = `https://t.me/${botUsername}`;

  if (loading) {
    return (
      <div style={{ maxWidth: '440px', margin: '4rem auto 0', padding: '0 1rem' }}>
        <Card style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
          <LoadingState message="Verifying login link & securing session..." />
        </Card>
      </div>
    );
  }

  if (errorMsg) {
    return (
      <div style={{ maxWidth: '440px', margin: '4rem auto 0', padding: '0 1rem' }}>
        <Card style={{ textAlign: 'center', padding: '2.5rem 1.5rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⌛</div>
          <h2 style={{ fontSize: '1.25rem', fontWeight: 800, marginBottom: '0.6rem', color: '#f87171' }}>
            Link Expired or Used
          </h2>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '1.75rem', lineHeight: 1.6 }}>
            {errorMsg}
          </p>
          <a
            href={botLink}
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
    <div style={{ maxWidth: '440px', margin: '4rem auto 0', padding: '0 1rem' }}>
      <Card style={{ textAlign: 'center', padding: '2.5rem 1.5rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚡</div>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 800, marginBottom: '0.5rem' }}>
          SnapStudy Portal
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '1.75rem', lineHeight: 1.6 }}>
          To log in to your personal study dashboard, send <code>/portal</code> to the bot on Telegram.
        </p>
        <a
          href={botLink}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary btn-block"
        >
          Send /portal to Bot
        </a>
      </Card>
    </div>
  );
}
