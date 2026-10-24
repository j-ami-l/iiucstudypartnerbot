import React from 'react';
import { Link } from 'react-router-dom';
import Badge from './Badge';
import Icon from './Icon';
import { noteTitle, timeAgo, fullDate } from '../format';

/**
 * NoteCard: Compact card representation of a study note.
 * UI_PORTAL.md Section 4 & 5.1/5.2.
 * Solves "Invalid Date" and "Study Note #N" fallbacks.
 */
export default function NoteCard({ note }) {
  if (!note) return null;

  const title = noteTitle(note);
  const relativeTime = timeAgo(note.created_at);
  const exactDate = fullDate(note.created_at);

  const hasScore = note.last_score !== null && note.last_score !== undefined;
  const isQuizReady = Boolean(note.quiz_ready);

  return (
    <Link to={`/notes/${note.id}`} className="portal-note-card">
      <div className="note-card-top">
        <h4 className="note-card-title">{title}</h4>
        <div className="note-card-badges">
          <Badge variant="neutral">
            {note.language ? note.language.toUpperCase() : 'EN'}
          </Badge>
          {isQuizReady ? (
            <Badge variant="ok">Quiz ✓</Badge>
          ) : (
            <Badge variant="warn">Quiz …</Badge>
          )}
        </div>
      </div>

      <div className="note-card-bottom">
        <div className="note-card-meta" title={exactDate}>
          <Icon name="calendar" size={13} />
          <span>{relativeTime}</span>
        </div>

        {hasScore ? (
          <div className="note-card-score">
            <span>Last: </span>
            <strong>
              {note.last_score}/{note.last_total || 5}
            </strong>
          </div>
        ) : (
          <div className="note-card-score text-muted">
            <span>No attempts yet</span>
          </div>
        )}
      </div>
    </Link>
  );
}
