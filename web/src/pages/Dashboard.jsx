import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../api';
import KpiCard from '../components/KpiCard';
import ProgressBar from '../components/ProgressBar';
import PracticeCard from '../components/PracticeCard';
import NoteCard from '../components/NoteCard';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';
import Icon from '../components/Icon';

/**
 * Dashboard page — UI_PORTAL.md Section 5.1
 * - Gradient title & personalized greeting
 * - 4 KPI cards (Notes, Quizzes, Accuracy with ProgressBar, Weak topics)
 * - State-driven PracticeCard with ShinyButton
 * - Recent notes with NoteCard
 * - Empty state when no notes
 */
export default function Dashboard({ user }) {
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
  const firstName = user?.name ? user.name.split(' ')[0] : 'there';
  const isDemoUser = user?.is_demo || false;

  if (loading) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Study Dashboard</h1>
        <p className="portal-page-subtitle">Hi, {firstName}. Here is your progress.</p>
        <div className="portal-kpi-grid">
          <Skeleton count={4} type="kpi" />
        </div>
        <div style={{ marginTop: '24px' }}>
          <Skeleton count={3} type="note" />
        </div>
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error} onRetry={fetchDashboard} botUsername={botUsername} />;
  }

  if (!data || data.notes_count === 0) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Study Dashboard</h1>
        <p className="portal-page-subtitle">
          Hi, {firstName}. Here is your progress.{' '}
          {isDemoUser && <span style={{ color: 'var(--text-3)' }}>(sample data)</span>}
        </p>
        <EmptyState
          icon="📚"
          title="No notes yet"
          description="Send a photo of your notes to the bot to get started."
          actionText="Open Telegram Bot"
          actionHref={`https://t.me/${botUsername}`}
        />
      </div>
    );
  }

  // KPI rule Section 5.1:
  // Accuracy: "—" when no quizzes yet, otherwise "NN%" with a ProgressBar.
  const hasQuizzes = data.quizzes_taken > 0;
  const accuracyDisplay = hasQuizzes && data.accuracy_percent !== null ? `${data.accuracy_percent}%` : '—';
  
  // Weak topics: "—" until at least one quiz exists. A real "0" in --ok only after quizzes exist.
  const weakDisplay = hasQuizzes ? String(data.weak_topics_count) : '—';
  const weakColor = hasQuizzes
    ? data.weak_topics_count === 0
      ? 'var(--ok)'
      : 'var(--accent-light)'
    : undefined;

  return (
    <div className="portal-page">
      <div style={{ marginBottom: '20px' }}>
        <h1 className="portal-page-title">Study Dashboard</h1>
        <p className="portal-page-subtitle">
          Hi, {firstName}. Here is your progress.{' '}
          {isDemoUser && <span style={{ color: 'var(--text-3)' }}>(sample data)</span>}
        </p>
      </div>

      {/* 4 KPIs: 2 cols phone, 4 cols desktop */}
      <div className="portal-kpi-grid">
        <KpiCard
          label="Notes"
          value={data.notes_count}
        />
        <KpiCard
          label="Quizzes taken"
          value={data.quizzes_taken}
        />
        <KpiCard
          label="Accuracy"
          value={accuracyDisplay}
          footer={
            hasQuizzes && data.accuracy_percent !== null ? (
              <ProgressBar
                value={data.accuracy_percent}
                color={data.accuracy_percent >= 70 ? 'var(--ok)' : 'var(--accent)'}
              />
            ) : null
          }
        />
        <KpiCard
          label="Weak topics"
          value={weakDisplay}
          valueColor={weakColor}
          subtext={hasQuizzes && data.weak_topics_count === 0 ? 'All mastered' : undefined}
        />
      </div>

      {/* Practice CTA (State-driven card) */}
      <PracticeCard
        quizzesTaken={data.quizzes_taken}
        weakCount={data.weak_topics_count}
        botUsername={botUsername}
      />

      {/* Recent Notes Section */}
      <div style={{ marginTop: '28px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '12px',
          }}
        >
          <h2 className="portal-section-title" style={{ margin: 0 }}>
            Recent notes
          </h2>
          <Link
            to="/notes"
            style={{
              color: 'var(--accent-light)',
              fontSize: '13px',
              fontWeight: 500,
              display: 'inline-flex',
              alignItems: 'center',
              gap: '4px',
              minHeight: '44px',
            }}
          >
            <span>View all</span>
            <Icon name="arrow-right" size={14} />
          </Link>
        </div>

        <div className="portal-notes-list">
          {data.recent_notes && data.recent_notes.length > 0 ? (
            data.recent_notes.map((note) => <NoteCard key={note.id} note={note} />)
          ) : (
            <p style={{ color: 'var(--text-3)', fontSize: '14px' }}>No notes found.</p>
          )}
        </div>
      </div>
    </div>
  );
}
