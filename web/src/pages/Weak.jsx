import React, { useEffect, useState } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import Badge from '../components/Badge';
import ProgressBar from '../components/ProgressBar';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';
import Icon from '../components/Icon';

/**
 * Weak Topics page — UI_PORTAL.md Section 5.6
 * Rows with topic, ProgressBar, accuracy and attempts, worst first, weak ones tagged accent.
 */
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
  const practiceUrl = `https://t.me/${botUsername}?start=practice`;

  if (loading) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Weak Topics</h1>
        <p className="portal-page-subtitle">Topics needing reinforcement based on quiz accuracy.</p>
        <Skeleton count={3} type="note" />
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchTopics} botUsername={botUsername} />;
  }

  const weakOnly = topics.filter((t) => t.is_weak);

  if (topics.length === 0 || weakOnly.length === 0) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Weak Topics</h1>
        <p className="portal-page-subtitle">Topics needing reinforcement based on quiz accuracy.</p>
        <EmptyState
          icon="🎉"
          title="No weak topics right now"
          description="Great job! You have mastered all topics tested so far or have not taken any quizzes yet."
          actionText="Take a Quiz in Telegram"
          actionHref={`https://t.me/${botUsername}`}
        />
      </div>
    );
  }

  return (
    <div className="portal-page">
      <div style={{ marginBottom: '20px' }}>
        <h1 className="portal-page-title">Weak Topics</h1>
        <p className="portal-page-subtitle">
          Found {weakOnly.length} {weakOnly.length === 1 ? 'topic' : 'topics'} needing reinforcement (accuracy under 60%).
        </p>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {weakOnly.map((t) => (
          <Card key={t.topic}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '12px', marginBottom: '8px' }}>
              <div>
                <h3 style={{ fontSize: '16px', fontWeight: 600, color: 'var(--text)' }}>
                  {t.topic}
                </h3>
                <div style={{ fontSize: '13px', color: 'var(--text-2)', marginTop: '2px' }}>
                  {t.correct} of {t.attempts} questions answered correctly
                </div>
              </div>

              <Badge variant="accent">
                {t.accuracy_percent}% Accuracy
              </Badge>
            </div>

            <div style={{ marginTop: '10px' }}>
              <ProgressBar
                value={t.accuracy_percent}
                color="var(--accent)"
              />
            </div>

            <div style={{ marginTop: '14px', display: 'flex', justifyContent: 'flex-end' }}>
              <a
                href={practiceUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="portal-btn-secondary"
                style={{ minHeight: '38px', padding: '6px 14px', fontSize: '13px' }}
              >
                <span>Practice this topic</span>
                <Icon name="arrow-right" size={13} />
              </a>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
