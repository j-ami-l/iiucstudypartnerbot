import React, { useEffect, useState } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';

export default function Weak({ user }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [topics, setTopics] = useState([]);

  const fetchTopics = () => {
    setLoading(true);
    setError(null);
    api
      .getWeakTopics()
      .then((res) => {
        setTopics(res || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchTopics();
  }, []);

  const botUsername = user?.bot_username || 'iiucstudypartnerbot';
  const botBaseUrl = `https://t.me/${botUsername}`;

  if (loading) {
    return <LoadingState message="Analyzing your topic performance..." />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchTopics} botUsername={botUsername} />;
  }

  const weakOnly = topics.filter((t) => t.is_weak);

  if (topics.length === 0 || weakOnly.length === 0) {
    return (
      <div>
        <h1 className="title-xl">Weak Topics</h1>
        <p className="subtitle">Topics where your accuracy falls below 60%.</p>
        <EmptyState
          icon="🎉"
          title="No Weak Topics Right Now!"
          description="Great job! You don't have any weak topics under the threshold. Keep taking quizzes to test your understanding."
          actionText="Take a Quiz in Telegram"
          actionHref={botBaseUrl}
        />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="title-xl">Weak Topics</h1>
        <p className="subtitle">
          Found {weakOnly.length} {weakOnly.length === 1 ? 'topic' : 'topics'} needing reinforcement (accuracy under 60%).
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
        {weakOnly.map((t) => {
          const practiceUrl = `https://t.me/${botUsername}?start=practice`;

          return (
            <Card key={t.topic}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '0.75rem' }}>
                <div>
                  <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {t.topic}
                  </h3>
                  <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '0.2rem' }}>
                    {t.correct} of {t.attempts} questions answered correctly
                  </div>
                </div>

                <span
                  className="badge"
                  style={{
                    background: 'rgba(244, 63, 94, 0.15)',
                    color: '#fb7185',
                    fontSize: '0.85rem',
                    padding: '0.3rem 0.65rem',
                  }}
                >
                  {t.accuracy_percent}% Accuracy
                </span>
              </div>

              {/* Progress Bar */}
              <div
                style={{
                  width: '100%',
                  height: '6px',
                  background: 'rgba(255, 255, 255, 0.08)',
                  borderRadius: '3px',
                  overflow: 'hidden',
                  margin: '0.75rem 0 1rem',
                }}
              >
                <div
                  style={{
                    width: `${Math.max(5, Math.min(100, t.accuracy_percent))}%`,
                    height: '100%',
                    background: 'var(--accent-rose)',
                    borderRadius: '3px',
                  }}
                />
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <a
                  href={practiceUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-secondary"
                  style={{ fontSize: '0.84rem', minHeight: '38px', padding: '0.4rem 0.9rem' }}
                >
                  🎯 Practice {t.topic} in Bot
                </a>
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
