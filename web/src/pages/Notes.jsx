import React, { useEffect, useState } from 'react';
import { api } from '../api';
import NoteCard from '../components/NoteCard';
import EmptyState from '../components/EmptyState';
import ErrorState from '../components/ErrorState';
import Skeleton from '../components/Skeleton';

/**
 * Notes list page — UI_PORTAL.md Section 5.2
 * - Title "Notes"
 * - Vertical list of NoteCard
 * - 3 skeleton cards while loading
 * - Empty state with link to Telegram bot
 */
export default function Notes({ user }) {
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

  if (loading && items.length === 0) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Notes</h1>
        <p className="portal-page-subtitle">Your study notes and practice summaries.</p>
        <Skeleton count={3} type="note" />
      </div>
    );
  }

  if (error) {
    return <ErrorState error={error} onRetry={() => fetchNotes(offset)} botUsername={botUsername} />;
  }

  if (total === 0) {
    return (
      <div className="portal-page">
        <h1 className="portal-page-title">Notes</h1>
        <p className="portal-page-subtitle">Your study notes and practice summaries.</p>
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

  return (
    <div className="portal-page">
      <div style={{ marginBottom: '20px' }}>
        <h1 className="portal-page-title">Notes</h1>
        <p className="portal-page-subtitle">
          Showing {items.length} of {total} notes in your library.
        </p>
      </div>

      <div className="portal-notes-list">
        {items.map((note) => (
          <NoteCard key={note.id} note={note} />
        ))}
      </div>

      {total > items.length && (
        <div style={{ marginTop: '24px', textAlign: 'center' }}>
          <button
            onClick={() => fetchNotes(offset + limit)}
            className="portal-btn-secondary"
            disabled={loading}
            type="button"
          >
            {loading ? 'Loading…' : 'Load more notes'}
          </button>
        </div>
      )}
    </div>
  );
}
