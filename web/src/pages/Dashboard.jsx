import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api } from '../api';
import Card from '../components/Card';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import { formatLocalDate } from '../utils/date';

export default function Dashboard({ user }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [data, setData] = useState(null);

  const fetchDashboard = () => {
    setLoading(true);
    setError(null);
    api
      .getDashboard()
      .then((res) => {
        setData(res);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const botUsername = user?.bot_username || 'iiucstudypartnerbot';
  const botPracticeUrl = `https://t.me/${botUsername}?start=practice`;
  const botBaseUrl = `https://t.me/${botUsername}`;

  if (loading) {
    return <LoadingState message="Loading your study overview..." />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchDashboard} botUsername={botUsername} />;
  }

  if (!data || data.notes_count === 0) {
    return (
      <div>
        <h1 className="title-xl">Welcome{user?.name ? `, ${user.name}` : ''}! 👋</h1>
        <p className="subtitle">Your AI-powered study partner dashboard.</p>
        <EmptyState
          icon="📸"
          title="No Study Notes Yet"
          description="Send a photo or document of your notes to the bot on Telegram to generate summaries and interactive quizzes."
          actionText="Send Notes in Telegram"
          actionHref={botBaseUrl}
        />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="title-xl">Study Dashboard</h1>
        <p className="subtitle">
          Welcome back{user?.name ? `, ${user.name}` : ''}! Here is your current learning progress.
        </p>
      </div>

      {/* Overview Stat Cards */}
      <div className="stat-grid">
        <div className="stat-card">
          <span className="stat-label">Notes Uploaded</span>
          <span className="stat-value">{data.notes_count}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Quizzes Taken</span>
          <span className="stat-value">{data.quizzes_taken}</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Overall Accuracy</span>
          <span className="stat-value" style={{ color: data.accuracy_percent != null && data.accuracy_percent >= 70 ? 'var(--accent-green)' : 'inherit' }}>
            {data.accuracy_percent != null ? `${data.accuracy_percent}%` : '—'}
          </span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Weak Topics</span>
          <span
            className="stat-value"
            style={{ color: data.weak_topics_count > 0 ? 'var(--accent-rose)' : 'var(--accent-green)' }}
          >
            {data.weak_topics_count}
          </span>
        </div>
      </div>

      {/* Practice Callout Banner */}
      <Card style={{ background: 'linear-gradient(135deg, rgba(59, 130, 246, 0.12), rgba(139, 92, 246, 0.12))', border: '1px solid rgba(59, 130, 246, 0.25)', marginBottom: '2rem' }}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, marginBottom: '0.25rem' }}>
              🎯 Interactive Telegram Practice
            </h3>
            <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
              Practice questions you previously missed to strengthen your weak topics.
            </p>
          </div>
          <div>
            <a
              href={botPracticeUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn btn-primary"
            >
              Start Practice in Bot
            </a>
          </div>
        </div>
      </Card>

      {/* Recent Notes Section */}
      <div style={{ marginBottom: '1.5rem' }}>
        <div className="section-title">
          <span>Recent Notes</span>
          <Link to="/notes" style={{ fontSize: '0.88rem', color: 'var(--accent-primary)', fontWeight: 600 }}>
            View All ({data.notes_count}) →
          </Link>
        </div>

        {data.recent_notes.length === 0 ? (
          <EmptyState
            icon="📝"
            title="No Recent Notes"
            description="Take your first quiz in Telegram to see your notes here."
            actionText="Open Telegram"
            actionHref={botBaseUrl}
          />
        ) : (
          <div>
            {data.recent_notes.map((note) => {
              const localDate = formatLocalDate(note.created_at);

              return (
                <Card
                  key={note.id}
                  clickable
                  onClick={() => navigate(`/notes/${note.id}`)}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: '0.75rem', marginBottom: '0.5rem' }}>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {note.title || `Study Note #${note.id}`}
                    </h3>
                    <div style={{ display: 'flex', gap: '0.4rem', flexShrink: 0 }}>
                      <span className="badge badge-blue">{note.language.toUpperCase()}</span>
                      {note.last_score != null ? (
                        <span className="badge badge-green">
                          {note.last_score}/{note.last_total}
                        </span>
                      ) : note.quiz_ready ? (
                        <span className="badge badge-amber">Quiz Ready</span>
                      ) : null}
                    </div>
                  </div>

                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', alignItems: 'center', marginTop: '0.75rem' }}>
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>📅 {localDate}</span>
                    {note.topics && note.topics.length > 0 && (
                      <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginLeft: '0.5rem' }}>
                        • {note.topics.join(', ')}
                      </span>
                    )}
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
