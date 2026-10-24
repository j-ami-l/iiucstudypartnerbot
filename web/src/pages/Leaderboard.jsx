import React, { useEffect, useState } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import Badge from '../components/Badge';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';

/**
 * Campus Study League — Leaderboard
 * Red Noir podium and ranking table with Badge components.
 */
export default function Leaderboard({ user }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [board, setBoard] = useState([]);

  const fetchBoard = () => {
    setLoading(true);
    setError(null);
    api
      .getLeaderboard()
      .then((res) => {
        setBoard(res || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchBoard();
  }, []);

  const botUsername = user?.bot_username || 'iiucstudypartnerbot';

  if (loading) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Campus Study League</h1>
        <p className="portal-page-subtitle">Weekly leaderboard ranking active student learners.</p>
        <Skeleton count={3} type="note" />
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchBoard} botUsername={botUsername} />;
  }

  if (!board || board.length === 0) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Campus Study League</h1>
        <p className="portal-page-subtitle">Weekly leaderboard ranking active student learners.</p>
        <EmptyState
          icon="🏆"
          title="No leaderboard entries yet"
          description="Take quizzes on Telegram to earn points and appear on the campus study leaderboard."
          actionText="Take a Quiz in Telegram"
          actionHref={`https://t.me/${botUsername}`}
        />
      </div>
    );
  }

  const top3 = board.slice(0, 3);
  const rest = board.slice(3);

  return (
    <div className="portal-page">
      <div style={{ marginBottom: '20px' }}>
        <h1 className="portal-page-title">Campus Study League</h1>
        <p className="portal-page-subtitle">
          Weekly rankings based on quizzes completed, questions solved, and accuracy.
        </p>
      </div>

      {/* Top 3 Podium */}
      {top3.length > 0 && (
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
            gap: '12px',
            marginBottom: '24px',
          }}
        >
          {top3.map((entry, index) => {
            const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : '🥉';
            const placeTitle = index === 0 ? '1st Place' : index === 1 ? '2nd Place' : '3rd Place';

            return (
              <Card
                key={entry.user_id}
                style={{
                  textAlign: 'center',
                  padding: '20px 12px',
                  borderColor: entry.is_me ? 'var(--accent)' : 'var(--card-border)',
                }}
              >
                <div style={{ fontSize: '28px', marginBottom: '4px' }}>{medal}</div>
                <div style={{ marginBottom: '8px' }}>
                  <Badge variant={index === 0 ? 'warn' : 'neutral'}>{placeTitle}</Badge>
                </div>
                <h4 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text)', marginBottom: '4px' }}>
                  {entry.name} {entry.is_me && '(You)'}
                </h4>
                <div style={{ fontSize: '12px', color: 'var(--text-2)' }}>
                  {entry.quizzes_taken} quizzes • {entry.accuracy_percent}%
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Rankings List */}
      <div>
        <h2 className="portal-section-title" style={{ marginBottom: '12px' }}>
          Leaderboard Rankings
        </h2>

        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {board.map((entry) => (
            <Card
              key={entry.user_id}
              style={{
                padding: '12px 16px',
                marginBottom: 0,
                borderColor: entry.is_me ? 'var(--accent)' : 'var(--card-border)',
                background: entry.is_me
                  ? 'linear-gradient(180deg, rgba(239, 35, 60, 0.1) 0%, #000000 100%)'
                  : undefined,
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <span
                    style={{
                      fontFamily: 'var(--font-head)',
                      fontWeight: 700,
                      fontSize: '15px',
                      color: entry.rank <= 3 ? 'var(--accent-light)' : 'var(--text-3)',
                      width: '24px',
                    }}
                  >
                    #{entry.rank}
                  </span>
                  <div>
                    <div style={{ fontWeight: 600, fontSize: '14px', color: 'var(--text)' }}>
                      {entry.name} {entry.is_me && <Badge variant="accent">YOU</Badge>}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--text-3)' }}>
                      {entry.correct_count} correct / {entry.attempts_count} questions
                    </div>
                  </div>
                </div>

                <div style={{ textAlign: 'right' }}>
                  <div style={{ fontWeight: 700, fontSize: '15px', color: 'var(--text)' }}>
                    {entry.accuracy_percent}%
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--text-3)' }}>
                    {entry.quizzes_taken} quizzes
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
}
