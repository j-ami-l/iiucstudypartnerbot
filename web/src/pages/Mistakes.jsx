import React, { useEffect, useState } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import Badge from '../components/Badge';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';
import { timeAgo, fullDate } from '../format';

/**
 * Mistake Notebook — UI_PORTAL.md Section 5.6
 * Question cards with correct options highlighted in --ok.
 */
export default function Mistakes({ user }) {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [mistakes, setMistakes] = useState([]);

  const fetchMistakes = () => {
    setLoading(true);
    setError(null);
    api
      .getMistakes()
      .then((res) => {
        setMistakes(res || []);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchMistakes();
  }, []);

  const botUsername = user?.bot_username || 'iiucstudypartnerbot';
  const botPracticeUrl = `https://t.me/${botUsername}?start=practice`;

  if (loading) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Mistake Notebook</h1>
        <p className="portal-page-subtitle">Track questions you got wrong and master them.</p>
        <Skeleton count={3} type="note" />
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchMistakes} botUsername={botUsername} />;
  }

  if (mistakes.length === 0) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Mistake Notebook</h1>
        <p className="portal-page-subtitle">Track questions you got wrong and master them.</p>
        <EmptyState
          icon="🎉"
          title="No mistakes to practice!"
          description="You don't have any outstanding mistakes. Questions you answer correctly in practice automatically disappear from here."
          actionText="Take a Quiz in Telegram"
          actionHref={`https://t.me/${botUsername}`}
        />
      </div>
    );
  }

  return (
    <div className="portal-page">
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'flex-start',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '20px',
        }}
      >
        <div>
          <h1 className="portal-page-title">Mistake Notebook</h1>
          <p className="portal-page-subtitle">
            {mistakes.length} active {mistakes.length === 1 ? 'question' : 'questions'} recorded.
          </p>
        </div>
        <a
          href={botPracticeUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="portal-btn-primary"
        >
          🎯 Practice in Telegram
        </a>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {mistakes.map((m, idx) => {
          const relativeTime = timeAgo(m.last_attempt_at);
          const exactDate = fullDate(m.last_attempt_at);

          return (
            <Card key={`${m.note_id}_${m.q_index}_${idx}`}>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  gap: '8px',
                  marginBottom: '10px',
                }}
              >
                <span
                  title={exactDate}
                  style={{ fontSize: '12px', color: 'var(--text-3)' }}
                >
                  From: {m.note_title || `Note #${m.note_id}`} • {relativeTime}
                </span>
                {m.topic && <Badge variant="accent">{m.topic}</Badge>}
              </div>

              <h3
                style={{
                  fontSize: '15px',
                  fontWeight: 600,
                  marginBottom: '12px',
                  color: 'var(--text)',
                }}
              >
                {idx + 1}. {m.question}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginBottom: '10px' }}>
                {m.options?.map((opt, optIdx) => {
                  const isCorrect = optIdx === m.correct_index;
                  return (
                    <div
                      key={optIdx}
                      style={{
                        padding: '8px 12px',
                        borderRadius: '8px',
                        background: isCorrect ? 'rgba(52, 211, 153, 0.12)' : 'rgba(255, 255, 255, 0.03)',
                        border: isCorrect ? '1px solid rgba(52, 211, 153, 0.35)' : '1px solid transparent',
                        color: isCorrect ? 'var(--ok)' : 'var(--text-2)',
                        fontSize: '13px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px',
                      }}
                    >
                      <span style={{ fontWeight: 600, width: '18px' }}>
                        {['A', 'B', 'C', 'D'][optIdx] || optIdx + 1}.
                      </span>
                      <span>{opt}</span>
                      {isCorrect && (
                        <span style={{ marginLeft: 'auto', fontSize: '11px', fontWeight: 600 }}>
                          ✓ Correct Answer
                        </span>
                      )}
                    </div>
                  );
                })}
              </div>

              {m.explanation && (
                <div
                  style={{
                    fontSize: '12px',
                    color: 'var(--text-2)',
                    background: 'rgba(0, 0, 0, 0.3)',
                    padding: '8px 10px',
                    borderRadius: '6px',
                    marginTop: '8px',
                  }}
                >
                  <strong style={{ color: 'var(--text)' }}>Explanation:</strong> {m.explanation}
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
