import React, { useEffect, useState } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import Bars from '../components/Bars';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import { formatLocalDateTime } from '../utils/date';

export default function History({ user }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState({ attempts: [], weekly: [] });

  const fetchHistory = () => {
    setLoading(true);
    setError(null);
    api
      .getHistory()
      .then((res) => {
        setData(res || { attempts: [], weekly: [] });
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  const botUsername = user?.bot_username || 'iiucstudypartnerbot';
  const botBaseUrl = `https://t.me/${botUsername}`;

  if (loading) {
    return <LoadingState message="Loading your quiz history & trend..." />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchHistory} botUsername={botUsername} />;
  }

  const hasData = (data.attempts && data.attempts.length > 0) || (data.weekly && data.weekly.length > 0);

  if (!hasData || data.attempts.length === 0) {
    return (
      <div>
        <h1 className="title-xl">Quiz History</h1>
        <p className="subtitle">Track your accuracy over time and review past quizzes.</p>
        <EmptyState
          icon="📊"
          title="No Quiz History Yet"
          description="Take quizzes on Telegram after uploading your study notes to see your weekly performance trend here."
          actionText="Take a Quiz in Telegram"
          actionHref={botBaseUrl}
        />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="title-xl">Quiz History & Analytics</h1>
        <p className="subtitle">6-week accuracy trends and past quiz attempts.</p>
      </div>

      {/* 6-Week Progress Trend */}
      {data.weekly && data.weekly.length > 0 && (
        <Card style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.1rem', fontWeight: 700, marginBottom: '0.4rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>📈</span> Weekly Accuracy Trend (Last 6 Weeks)
          </h2>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
            Aggregated percentage of correct answers per week.
          </p>
          <Bars weekly={data.weekly} />
        </Card>
      )}

      {/* Attempts Log */}
      <div>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>⏱️</span> Past Quiz Attempts ({data.attempts.length})
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {data.attempts.map((att, idx) => {
            const attemptDate = formatLocalDateTime(att.created_at);
            const percent = att.total > 0 ? Math.round((att.score / att.total) * 100) : 0;

            return (
              <Card key={idx} style={{ padding: '0.9rem 1.15rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.75rem' }}>
                  <div>
                    <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.2rem' }}>
                      {att.title || `Note #${att.note_id}`}
                    </h3>
                    <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      📅 {attemptDate}
                    </div>
                  </div>

                  <span
                    className={`badge ${percent >= 70 ? 'badge-green' : percent >= 50 ? 'badge-amber' : 'badge-rose'}`}
                    style={{ fontSize: '0.88rem', padding: '0.35rem 0.75rem' }}
                  >
                    {att.score}/{att.total} ({percent}%)
                  </span>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
