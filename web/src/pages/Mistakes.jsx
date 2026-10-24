import React, { useEffect, useState } from 'react';
import { api } from '../api';
import Card from '../components/Card';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import { formatLocalDateTime } from '../utils/date';

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
    return <LoadingState message="Opening your mistake notebook..." />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchMistakes} botUsername={botUsername} />;
  }

  if (mistakes.length === 0) {
    return (
      <div>
        <h1 className="title-xl">Mistake Notebook</h1>
        <p className="subtitle">Track questions you got wrong and master them.</p>
        <EmptyState
          icon="🎉"
          title="No Mistakes to Practice!"
          description="You don't have any outstanding mistakes. Questions you answer correctly in practice automatically disappear from here."
          actionText="Take a Quiz in Telegram"
          actionHref={`https://t.me/${botUsername}`}
        />
      </div>
    );
  }

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '1rem', marginBottom: '1.5rem' }}>
        <div>
          <h1 className="title-xl">Mistake Notebook</h1>
          <p className="subtitle">
            {mistakes.length} active {mistakes.length === 1 ? 'mistake' : 'mistakes'} recorded.
          </p>
        </div>
        <a
          href={botPracticeUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          🎯 Practice All Mistakes
        </a>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
        {mistakes.map((m, idx) => {
          const attemptDate = formatLocalDateTime(m.last_attempt_at);

          return (
            <Card key={`${m.note_id}_${m.q_index}_${idx}`}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: '0.5rem', marginBottom: '0.6rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                  From: {m.note_title || `Note #${m.note_id}`} • {attemptDate}
                </span>
                {m.topic && (
                  <span className="badge badge-purple" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#c4b5fd' }}>
                    {m.topic}
                  </span>
                )}
              </div>

              <h3 style={{ fontSize: '1rem', fontWeight: 700, marginBottom: '0.8rem', color: 'var(--text-primary)' }}>
                {idx + 1}. {m.question}
              </h3>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', marginBottom: '0.8rem' }}>
                {m.options?.map((opt, optIdx) => {
                  const isCorrect = optIdx === m.correct_index;
                  const isChosen = optIdx === m.chosen_index;

                  let styleClass = '';
                  let tag = null;

                  if (isCorrect) {
                    styleClass = 'correct';
                    tag = (
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#34d399' }}>
                        ✓ Correct Answer
                      </span>
                    );
                  } else if (isChosen) {
                    tag = (
                      <span style={{ fontSize: '0.78rem', fontWeight: 700, color: '#fb7185' }}>
                        ✗ Your Answer
                      </span>
                    );
                  }

                  return (
                    <div
                      key={optIdx}
                      className={`mcq-option ${styleClass}`}
                      style={{
                        background: isChosen && !isCorrect ? 'rgba(244, 63, 94, 0.12)' : undefined,
                        border: isChosen && !isCorrect ? '1px solid rgba(244, 63, 94, 0.3)' : undefined,
                      }}
                    >
                      <span style={{ fontWeight: 700, width: '20px' }}>
                        {['A', 'B', 'C', 'D'][optIdx] || optIdx + 1}.
                      </span>
                      <span style={{ flex: 1 }}>{opt}</span>
                      {tag}
                    </div>
                  );
                })}
              </div>

              {m.explanation && (
                <div style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', background: 'rgba(255, 255, 255, 0.02)', padding: '0.6rem 0.85rem', borderRadius: 'var(--radius-sm)' }}>
                  <strong>Explanation:</strong> {m.explanation}
                </div>
              )}
            </Card>
          );
        })}
      </div>
    </div>
  );
}
