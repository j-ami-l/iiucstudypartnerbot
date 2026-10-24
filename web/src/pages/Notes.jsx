import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '../api';
import Card from '../components/Card';
import LoadingState from '../components/LoadingState';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import { formatLocalDate } from '../utils/date';

export default function Notes({ user }) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [offset, setOffset] = useState(0);
  const limit = 20;

  const fetchNotes = (newOffset = offset) => {
    setLoading(true);
    setError(null);
    api
      .getNotes(limit, newOffset)
      .then((res) => {
        setItems(res.items || []);
        setTotal(res.total || 0);
        setOffset(newOffset);
        setLoading(false);
      })
      .catch((err) => {
        setError(err);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchNotes(0);
  }, []);

  const botUsername = user?.bot_username || 'iiucstudypartnerbot';
  const botBaseUrl = `https://t.me/${botUsername}`;

  if (loading && items.length === 0) {
    return <LoadingState message="Loading your study notes..." />;
  }

  if (error) {
    return <ErrorState error={error} onRetry={() => fetchNotes(offset)} botUsername={botUsername} />;
  }

  if (total === 0) {
    return (
      <div>
        <h1 className="title-xl">My Study Notes</h1>
        <p className="subtitle">All notes and quiz summaries generated from your uploads.</p>
        <EmptyState
          icon="📚"
          title="No Notes Found"
          description="You haven't uploaded any study notes yet. Send a photo or document to the bot in Telegram to get started!"
          actionText="Send Notes in Telegram"
          actionHref={botBaseUrl}
        />
      </div>
    );
  }

  return (
    <div>
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 className="title-xl">My Study Notes</h1>
        <p className="subtitle">
          Showing {items.length} of {total} notes in your library.
        </p>
      </div>

      <div>
        {items.map((note) => {
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
                      Score: {note.last_score}/{note.last_total}
                    </span>
                  ) : note.quiz_ready ? (
                    <span className="badge badge-amber">Quiz Ready</span>
                  ) : null}
                </div>
              </div>

              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', alignItems: 'center', marginTop: '0.75rem' }}>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>📅 {localDate}</span>
                {note.topics && note.topics.length > 0 && (
                  <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                    • Topics: {note.topics.join(', ')}
                  </span>
                )}
              </div>
            </Card>
          );
        })}
      </div>

      {/* Pagination Controls */}
      {total > limit && (
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: '2rem' }}>
          <button
            onClick={() => fetchNotes(Math.max(0, offset - limit))}
            disabled={offset === 0}
            className="btn btn-secondary"
            style={{ opacity: offset === 0 ? 0.5 : 1 }}
          >
            ← Previous
          </button>
          <span style={{ fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
            Page {Math.floor(offset / limit) + 1} of {Math.ceil(total / limit)}
          </span>
          <button
            onClick={() => fetchNotes(offset + limit)}
            disabled={offset + limit >= total}
            className="btn btn-secondary"
            style={{ opacity: offset + limit >= total ? 0.5 : 1 }}
          >
            Next →
          </button>
        </div>
      )}
    </div>
  );
}
