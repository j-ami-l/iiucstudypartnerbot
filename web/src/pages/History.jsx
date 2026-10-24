import React, { useEffect, useState } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Bars from '../components/Bars';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';
import { timeAgo, fullDate } from '../format';

/**
 * Quiz History page — UI_PORTAL.md Section 5.6
 * 6-week SVG/CSS accuracy bar chart with Bars, and chronological quiz attempts.
 */
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
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Quiz History</h1>
        <p className="portal-page-subtitle">Track your accuracy over time and review past quizzes.</p>
        <Skeleton count={3} type="note" />
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchHistory} botUsername={botUsername} />;
  }

  const hasData = (data.attempts && data.attempts.length > 0) || (data.weekly && data.weekly.length > 0);

  if (!hasData || data.attempts.length === 0) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Quiz History</h1>
        <p className="portal-page-subtitle">Track your accuracy over time and review past quizzes.</p>
        <EmptyState
          icon="📊"
          title="No quiz history yet"
          description="Take quizzes on Telegram after uploading your study notes to see your weekly performance trend here."
          actionText="Take a Quiz in Telegram"
          actionHref={botBaseUrl}
        />
      </div>
    );
  }

  return (
    <div className="portal-page">
      <div style={{ marginBottom: '20px' }}>
        <h1 className="portal-page-title">Quiz History</h1>
        <p className="portal-page-subtitle">6-week accuracy trends and past quiz attempts.</p>
      </div>

      {/* 6-Week Progress Trend */}
      {data.weekly && data.weekly.length > 0 && (
        <Card style={{ marginBottom: '24px' }}>
          <h2 className="portal-section-title" style={{ marginBottom: '4px' }}>
            Weekly Accuracy Trend
          </h2>
          <p style={{ fontSize: '13px', color: 'var(--text-2)', marginBottom: '8px' }}>
            Aggregated percentage of correct answers per week over the last 6 weeks.
          </p>
          <Bars weekly={data.weekly} />
        </Card>
      )}

      {/* Attempts Log */}
      <div>
        <h2 className="portal-section-title" style={{ marginBottom: '14px' }}>
          Past Quiz Attempts ({data.attempts.length})
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          {data.attempts.map((att, idx) => {
            const relativeTime = timeAgo(att.created_at);
            const exactDate = fullDate(att.created_at);
            const percent = att.total > 0 ? Math.round((att.score / att.total) * 100) : 0;
            const isPassing = percent >= 70;

            return (
              <Card key={idx} style={{ padding: '14px 18px', marginBottom: 0 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '12px' }}>
                  <div>
                    <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text)', marginBottom: '2px' }}>
                      {att.title || `Note #${att.note_id}`}
                    </h3>
                    <span title={exactDate} style={{ fontSize: '12px', color: 'var(--text-3)' }}>
                      {relativeTime}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <Badge variant={isPassing ? 'ok' : 'accent'}>
                      {att.score}/{att.total} ({percent}%)
                    </Badge>
                  </div>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </div>
  );
}
