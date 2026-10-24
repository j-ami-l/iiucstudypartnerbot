import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api';
import Card from '../components/Card';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function NoteDetail({ user }) {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [note, setNote] = useState(null);

  const fetchDetail = () => {
    setLoading(true);
    setError(null);
    api
      .getNoteDetail(id)
      .then((res) => {
        setNote(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchDetail();
  }, [id]);

  const botUsername = user?.bot_username || 'iiucstudypartnerbot';
  const botPracticeUrl = `https://t.me/${botUsername}?start=practice`;

  if (loading) {
    return <LoadingState message="Loading note details & summary..." />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchDetail} botUsername={botUsername} />;
  }

  if (!note) {
    return null;
  }

  const localDate = note.created_at
    ? new Date(note.created_at.replace(' ', 'T') + 'Z').toLocaleString(undefined, {
        dateStyle: 'medium',
        timeStyle: 'short',
      })
    : '';

  const isBengali = note.language === 'bn';

  return (
    <div lang={isBengali ? 'bn' : 'en'}>
      {/* Back Link */}
      <div style={{ marginBottom: '1.25rem' }}>
        <Link to="/notes" style={{ color: 'var(--accent-primary)', fontSize: '0.9rem', fontWeight: 600 }}>
          ← Back to Notes
        </Link>
      </div>

      {/* Note Header */}
      <div style={{ marginBottom: '1.75rem' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem', marginBottom: '0.5rem' }}>
          <span className="badge badge-blue">{note.language.toUpperCase()}</span>
          <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>📅 {localDate}</span>
        </div>
        <h1 className="title-xl" style={{ lineHeight: 1.3 }}>
          {note.title || `Study Note #${note.id}`}
        </h1>
      </div>

      {/* AI Summary Card */}
      <Card style={{ marginBottom: '1.75rem' }}>
        <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <span>📖</span> Study Summary
        </h2>
        {/* Render safely without dangerouslySetInnerHTML using white-space: pre-wrap */}
        <div className="note-summary">
          {note.summary_text}
        </div>
      </Card>

      {/* MCQs Section */}
      {note.mcqs && note.mcqs.length > 0 && (
        <Card style={{ marginBottom: '1.75rem' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>❓</span> Interactive Quiz Questions ({note.mcqs.length})
          </h2>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.25rem' }}>
            {note.mcqs.map((q, qIdx) => (
              <div key={qIdx} className="mcq-item">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.5rem', marginBottom: '0.4rem' }}>
                  <div style={{ fontWeight: 700, fontSize: '0.98rem', color: 'var(--text-primary)' }}>
                    {qIdx + 1}. {q.question}
                  </div>
                  {q.topic && (
                    <span className="badge badge-purple" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#c4b5fd', flexShrink: 0 }}>
                      {q.topic}
                    </span>
                  )}
                </div>

                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.35rem', marginTop: '0.6rem' }}>
                  {q.options?.map((opt, optIdx) => {
                    const isCorrect = optIdx === q.correct_index;
                    return (
                      <div
                        key={optIdx}
                        className={`mcq-option ${isCorrect ? 'correct' : ''}`}
                      >
                        <span style={{ fontWeight: 700, width: '20px' }}>
                          {['A', 'B', 'C', 'D'][optIdx] || optIdx + 1}.
                        </span>
                        <span style={{ flex: 1 }}>{opt}</span>
                        {isCorrect && (
                          <span style={{ fontSize: '0.8rem', fontWeight: 700, color: '#34d399' }}>
                            ✓ Correct
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>

                {q.explanation && (
                  <div style={{ marginTop: '0.6rem', fontSize: '0.85rem', color: 'var(--text-secondary)', background: 'rgba(255, 255, 255, 0.02)', padding: '0.5rem 0.75rem', borderRadius: 'var(--radius-sm)' }}>
                    <strong>Explanation:</strong> {q.explanation}
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Past Quiz Attempts */}
      {note.attempts && note.attempts.length > 0 && (
        <Card style={{ marginBottom: '1.75rem' }}>
          <h2 style={{ fontSize: '1.15rem', fontWeight: 700, marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <span>🎯</span> Past Quiz Attempts
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {note.attempts.map((att, aIdx) => {
              const attemptDate = att.created_at
                ? new Date(att.created_at.replace(' ', 'T') + 'Z').toLocaleString(undefined, {
                    dateStyle: 'medium',
                    timeStyle: 'short',
                  })
                : '';
              const percent = att.total > 0 ? Math.round((att.score / att.total) * 100) : 0;

              return (
                <div
                  key={aIdx}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '0.6rem 0.85rem',
                    background: 'rgba(255, 255, 255, 0.02)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--border-color)',
                  }}
                >
                  <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    Attempt #{att.attempt_number || aIdx + 1} • {attemptDate}
                  </span>
                  <span
                    className={`badge ${percent >= 70 ? 'badge-green' : 'badge-rose'}`}
                    style={{ fontSize: '0.82rem' }}
                  >
                    {att.score}/{att.total} ({percent}%)
                  </span>
                </div>
              );
            })}
          </div>
        </Card>
      )}

      {/* Practice Button */}
      <div style={{ textAlign: 'center', marginTop: '2rem' }}>
        <a
          href={botPracticeUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-primary"
        >
          🎯 Practice Mistakes on Telegram
        </a>
      </div>
    </div>
  );
}
