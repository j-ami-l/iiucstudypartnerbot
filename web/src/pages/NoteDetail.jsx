import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../api';
import Card from '../components/Card';
import Badge from '../components/Badge';
import Icon from '../components/Icon';
import Flashcards from '../components/Flashcards';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';
import { noteTitle, timeAgo, fullDate } from '../format';

/**
 * NoteDetail page — UI_PORTAL.md Section 5.3
 * - Back link, title via noteTitle, meta row (language badge, relative date with full date tooltip, last score)
 * - Summary card: white-space: pre-wrap, body font, Bangla styles when language === 'bn'
 * - Quiz card: status (ready / preparing), past scores as badges, deep link to Telegram
 * - Flashcards tab mode & Gemma AI Tutor preserved with Red Noir design
 */
export default function NoteDetail({ user }) {
  const { id } = useParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [note, setNote] = useState(null);

  // View mode: 'summary' or 'flashcards'
  const [activeTab, setActiveTab] = useState('summary');

  // AI Tutor state
  const [aiQuestion, setAiQuestion] = useState('');
  const [aiLoading, setAiLoading] = useState(false);
  const [aiAnswer, setAiAnswer] = useState(null);
  const [aiError, setAiError] = useState(null);

  // Challenge link state
  const [copiedChallenge, setCopiedChallenge] = useState(false);

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
  const challengeUrl = `https://t.me/${botUsername}?start=challenge_${id}`;

  const handleAskAi = async (e) => {
    e.preventDefault();
    if (!aiQuestion.trim() || aiLoading) return;

    setAiLoading(true);
    setAiError(null);
    try {
      const res = await api.askNote(id, aiQuestion.trim());
      setAiAnswer(res.answer);
      setAiQuestion('');
    } catch (err) {
      setAiError(err.message || 'Unable to get answer from AI tutor. Please try again.');
    } finally {
      setAiLoading(false);
    }
  };

  const handleCopyChallenge = () => {
    navigator.clipboard.writeText(challengeUrl).then(() => {
      setCopiedChallenge(true);
      setTimeout(() => setCopiedChallenge(false), 3000);
    });
  };

  if (loading) {
    return (
      <div className="portal-page">
        <Link to="/notes" className="note-back-link">
          <Icon name="arrow-right" size={14} style={{ transform: 'rotate(180deg)' }} />
          <span>Back to Notes</span>
        </Link>
        <div style={{ marginTop: '16px' }}>
          <Skeleton count={2} type="note" />
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchDetail} botUsername={botUsername} />;
  }

  if (!note) {
    return null;
  }

  const title = noteTitle(note);
  const relativeTime = timeAgo(note.created_at);
  const exactDate = fullDate(note.created_at);
  const isBengali = note.language === 'bn';
  const isQuizReady = Boolean(note.quiz_ready);

  return (
    <div className="portal-page" lang={isBengali ? 'bn' : 'en'}>
      {/* Back Link */}
      <Link to="/notes" className="note-back-link">
        <Icon name="arrow-right" size={14} style={{ transform: 'rotate(180deg)' }} />
        <span>Back to Notes</span>
      </Link>

      {/* Note Header */}
      <div className="note-detail-header">
        <h1 className="portal-page-title" style={{ fontSize: '26px' }}>
          {title}
        </h1>

        <div className="note-meta-row">
          <Badge variant="neutral">
            {note.language ? note.language.toUpperCase() : 'EN'}
          </Badge>
          {isQuizReady ? (
            <Badge variant="ok">Quiz Ready</Badge>
          ) : (
            <Badge variant="warn">Quiz Preparing…</Badge>
          )}
          <span title={exactDate} style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
            <Icon name="calendar" size={13} />
            <span>{relativeTime}</span>
          </span>
          {note.past_scores && note.past_scores.length > 0 && (
            <span>
              Last score: <strong style={{ color: 'var(--ok)' }}>{note.past_scores[note.past_scores.length - 1].score}/{note.past_scores[note.past_scores.length - 1].total}</strong>
            </span>
          )}
        </div>
      </div>

      {/* View Mode Switcher (Tabs) */}
      <div
        style={{
          display: 'flex',
          gap: '8px',
          marginBottom: '20px',
          borderBottom: '1px solid var(--card-border)',
          paddingBottom: '8px',
        }}
      >
        <button
          onClick={() => setActiveTab('summary')}
          className={`portal-btn-secondary ${activeTab === 'summary' ? 'active' : ''}`}
          style={{
            background: activeTab === 'summary' ? 'var(--accent-soft)' : 'transparent',
            borderColor: activeTab === 'summary' ? 'var(--accent)' : 'transparent',
            color: activeTab === 'summary' ? 'var(--text)' : 'var(--text-2)',
            minHeight: '40px',
            padding: '6px 14px',
            fontSize: '13px',
          }}
          type="button"
        >
          📖 Summary & Quiz
        </button>
        <button
          onClick={() => setActiveTab('flashcards')}
          className={`portal-btn-secondary ${activeTab === 'flashcards' ? 'active' : ''}`}
          style={{
            background: activeTab === 'flashcards' ? 'var(--accent-soft)' : 'transparent',
            borderColor: activeTab === 'flashcards' ? 'var(--accent)' : 'transparent',
            color: activeTab === 'flashcards' ? 'var(--text)' : 'var(--text-2)',
            minHeight: '40px',
            padding: '6px 14px',
            fontSize: '13px',
          }}
          type="button"
        >
          ⚡ Flashcards ({note.mcqs?.length || 0})
        </button>
      </div>

      {/* FLASHCARD MODE */}
      {activeTab === 'flashcards' && (
        <Flashcards mcqs={note.mcqs} title={title} />
      )}

      {/* SUMMARY & MCQ MODE */}
      {activeTab === 'summary' && (
        <>
          {/* Summary Card */}
          <Card style={{ marginBottom: '20px' }}>
            <h2 className="portal-section-title" style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '12px' }}>
              <span>📖</span> Study Summary
            </h2>
            <div className="note-summary-text">{note.summary_text}</div>
          </Card>

          {/* Quiz Card */}
          <Card style={{ marginBottom: '20px' }}>
            <div
              style={{
                display: 'flex',
                flexWrap: 'wrap',
                alignItems: 'center',
                justifyContent: 'space-between',
                gap: '12px',
                marginBottom: '16px',
              }}
            >
              <div>
                <h2 className="portal-section-title" style={{ margin: 0 }}>
                  📝 Practice Quiz
                </h2>
                <p style={{ color: 'var(--text-2)', fontSize: '13px', marginTop: '4px' }}>
                  Quizzes are taken interactively in Telegram.
                </p>
              </div>

              <div style={{ display: 'flex', gap: '8px' }}>
                <a
                  href={`https://t.me/${botUsername}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="portal-btn-primary"
                >
                  Take Quiz in Bot
                </a>
                <button
                  onClick={handleCopyChallenge}
                  className="portal-btn-secondary"
                  title="Challenge a classmate to take this exact quiz!"
                  type="button"
                >
                  {copiedChallenge ? '✅ Link Copied!' : '⚔️ Challenge Classmate'}
                </button>
              </div>
            </div>

            {/* Past score badges */}
            {note.past_scores && note.past_scores.length > 0 ? (
              <div style={{ marginTop: '12px' }}>
                <div style={{ fontSize: '12px', color: 'var(--text-2)', marginBottom: '8px' }}>
                  Past attempts:
                </div>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                  {note.past_scores.map((ps, i) => (
                    <Badge key={i} variant={ps.score >= (ps.total * 0.7) ? 'ok' : 'neutral'}>
                      Attempt #{i + 1}: {ps.score}/{ps.total}
                    </Badge>
                  ))}
                </div>
              </div>
            ) : (
              <p style={{ color: 'var(--text-3)', fontSize: '13px', margin: 0 }}>
                No quiz attempts recorded yet for this note.
              </p>
            )}
          </Card>

          {/* AI Tutor Interactive Q&A (Gemma 4) */}
          <Card style={{ marginBottom: '20px', borderColor: 'rgba(239, 35, 60, 0.25)' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '12px' }}>
              <span style={{ fontSize: '20px' }}>🤖</span>
              <div>
                <h3 style={{ fontSize: '15px', fontWeight: 600, color: 'var(--text)' }}>
                  Ask AI Tutor (Gemma 4)
                </h3>
                <p style={{ fontSize: '12px', color: 'var(--text-2)' }}>
                  Have questions about this note? Ask Gemma for an explanation or simplified example.
                </p>
              </div>
            </div>

            <form onSubmit={handleAskAi} style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <textarea
                value={aiQuestion}
                onChange={(e) => setAiQuestion(e.target.value)}
                placeholder="Ask a question about this lecture note..."
                style={{
                  width: '100%',
                  minHeight: '70px',
                  padding: '10px 12px',
                  background: 'rgba(0, 0, 0, 0.4)',
                  border: '1px solid var(--card-border)',
                  borderRadius: '8px',
                  color: 'var(--text)',
                  fontFamily: 'var(--font-body)',
                  fontSize: '14px',
                  resize: 'vertical',
                }}
              />
              <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                <button
                  type="submit"
                  disabled={aiLoading || !aiQuestion.trim()}
                  className="portal-btn-primary"
                  style={{ minHeight: '38px', padding: '6px 16px', fontSize: '13px' }}
                >
                  {aiLoading ? 'Thinking with Gemma…' : 'Ask Gemma'}
                </button>
              </div>
            </form>

            {aiError && (
              <div style={{ marginTop: '12px', padding: '10px', background: 'rgba(239, 35, 60, 0.15)', borderRadius: '8px', color: 'var(--accent-light)', fontSize: '13px' }}>
                {aiError}
              </div>
            )}

            {aiAnswer && (
              <div style={{ marginTop: '14px', padding: '14px', background: 'rgba(24, 24, 27, 0.8)', border: '1px solid var(--card-border)', borderRadius: '12px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '12px', fontWeight: 600, color: 'var(--accent-light)' }}>
                    💡 Gemma Explanation:
                  </span>
                  <button
                    onClick={() => setAiAnswer(null)}
                    style={{ background: 'none', border: 'none', color: 'var(--text-3)', cursor: 'pointer', fontSize: '12px' }}
                    type="button"
                  >
                    Clear ✕
                  </button>
                </div>
                <div style={{ whiteSpace: 'pre-wrap', lineHeight: 1.6, fontSize: '14px', color: 'var(--text)' }}>
                  {aiAnswer}
                </div>
              </div>
            )}
          </Card>

          {/* MCQs Preview */}
          {note.mcqs && note.mcqs.length > 0 && (
            <Card style={{ marginBottom: '20px' }}>
              <h2 className="portal-section-title" style={{ marginBottom: '14px' }}>
                ❓ Quiz Questions ({note.mcqs.length})
              </h2>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                {note.mcqs.map((q, qIdx) => (
                  <div key={qIdx} style={{ paddingBottom: '14px', borderBottom: qIdx < note.mcqs.length - 1 ? '1px solid var(--card-border)' : 'none' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '8px', marginBottom: '8px' }}>
                      <div style={{ fontWeight: 600, fontSize: '14px', color: 'var(--text)' }}>
                        {qIdx + 1}. {q.question}
                      </div>
                      {q.topic && (
                        <Badge variant="accent">{q.topic}</Badge>
                      )}
                    </div>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', marginLeft: '4px' }}>
                      {q.options?.map((opt, optIdx) => {
                        const isCorrect = optIdx === q.correct_index;
                        return (
                          <div
                            key={optIdx}
                            style={{
                              padding: '8px 12px',
                              borderRadius: '8px',
                              background: isCorrect ? 'rgba(52, 211, 153, 0.1)' : 'rgba(255, 255, 255, 0.03)',
                              border: isCorrect ? '1px solid rgba(52, 211, 153, 0.3)' : '1px solid transparent',
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
                              <span style={{ marginLeft: 'auto', fontSize: '11px', fontWeight: 600 }}>✓ Correct</span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
