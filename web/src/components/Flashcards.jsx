import React, { useState } from 'react';
import Card from './Card';

export default function Flashcards({ mcqs = [], title = 'Study Note' }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [mastered, setMastered] = useState(new Set());
  const [reviewLater, setReviewLater] = useState(new Set());
  const [isFinished, setIsFinished] = useState(false);

  if (!mcqs || mcqs.length === 0) {
    return (
      <Card style={{ textAlign: 'center', padding: '2.5rem 1rem' }}>
        <p style={{ color: 'var(--text-secondary)' }}>
          No quiz questions available to generate flashcards from this note.
        </p>
      </Card>
    );
  }

  const currentCard = mcqs[currentIndex];
  const total = mcqs.length;

  const handleNext = (isMastered) => {
    setIsFlipped(false);
    if (isMastered) {
      setMastered((prev) => new Set(prev).add(currentIndex));
      setReviewLater((prev) => {
        const next = new Set(prev);
        next.delete(currentIndex);
        return next;
      });
    } else {
      setReviewLater((prev) => new Set(prev).add(currentIndex));
    }

    if (currentIndex + 1 < total) {
      setTimeout(() => setCurrentIndex((idx) => idx + 1), 150);
    } else {
      setIsFinished(true);
    }
  };

  const handleRestart = () => {
    setCurrentIndex(0);
    setIsFlipped(false);
    setMastered(new Set());
    setReviewLater(new Set());
    setIsFinished(false);
  };

  if (isFinished) {
    return (
      <Card style={{ textAlign: 'center', padding: '3rem 1.5rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '0.75rem' }}>🎯</div>
        <h2 style={{ fontSize: '1.35rem', fontWeight: 800, marginBottom: '0.5rem' }}>
          Active Recall Session Complete!
        </h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.92rem', marginBottom: '1.5rem' }}>
          You reviewed all {total} flashcards for {title}.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '1.5rem', marginBottom: '2rem' }}>
          <div style={{ background: 'rgba(16, 185, 129, 0.12)', border: '1px solid rgba(16, 185, 129, 0.3)', padding: '0.85rem 1.5rem', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-green)' }}>
              {mastered.size}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Mastered</div>
          </div>
          <div style={{ background: 'rgba(244, 63, 94, 0.12)', border: '1px solid rgba(244, 63, 94, 0.3)', padding: '0.85rem 1.5rem', borderRadius: 'var(--radius-md)' }}>
            <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--accent-rose)' }}>
              {reviewLater.size}
            </div>
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>Review Later</div>
          </div>
        </div>

        <button onClick={handleRestart} className="btn btn-primary">
          🔄 Practice Again
        </button>
      </Card>
    );
  }

  const correctOption =
    currentCard.options && currentCard.correct_index != null
      ? currentCard.options[currentCard.correct_index]
      : 'Correct answer not specified';

  return (
    <div>
      {/* Session Progress Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.85rem' }}>
        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
          Card {currentIndex + 1} of {total}
        </span>
        <div style={{ display: 'flex', gap: '0.6rem' }}>
          <span className="badge badge-green" style={{ fontSize: '0.75rem' }}>
            ✓ {mastered.size} Mastered
          </span>
          <span className="badge badge-rose" style={{ fontSize: '0.75rem' }}>
            ✗ {reviewLater.size} Needs Review
          </span>
        </div>
      </div>

      {/* Progress Bar */}
      <div
        style={{
          width: '100%',
          height: '4px',
          background: 'rgba(255, 255, 255, 0.08)',
          borderRadius: '2px',
          marginBottom: '1rem',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            width: `${((currentIndex + 1) / total) * 100}%`,
            height: '100%',
            background: 'var(--accent-primary)',
            transition: 'width 0.3s ease',
          }}
        />
      </div>

      {/* 3D Flip Card */}
      <div className="flashcard-wrapper" onClick={() => setIsFlipped(!isFlipped)}>
        <div className={`flashcard-inner ${isFlipped ? 'flipped' : ''}`}>
          {/* Front Face */}
          <div className="flashcard-face flashcard-front">
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                <span className="badge badge-blue">QUESTION #{currentIndex + 1}</span>
                {currentCard.topic && (
                  <span className="badge badge-purple" style={{ background: 'rgba(139, 92, 246, 0.15)', color: '#c4b5fd' }}>
                    {currentCard.topic}
                  </span>
                )}
              </div>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 700, lineHeight: 1.5, color: 'var(--text-primary)' }}>
                {currentCard.question}
              </h3>
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textAlign: 'center' }}>
              💡 Click or tap card to reveal answer
            </div>
          </div>

          {/* Back Face */}
          <div className="flashcard-face flashcard-back">
            <div>
              <div style={{ marginBottom: '0.75rem' }}>
                <span className="badge badge-green">CORRECT ANSWER</span>
              </div>
              <h4 style={{ fontSize: '1.1rem', fontWeight: 700, color: '#34d399', marginBottom: '0.85rem', lineHeight: 1.4 }}>
                {correctOption}
              </h4>
              {currentCard.explanation && (
                <p style={{ fontSize: '0.88rem', color: '#cbd5e1', lineHeight: 1.6, background: 'rgba(255, 255, 255, 0.03)', padding: '0.75rem', borderRadius: 'var(--radius-sm)' }}>
                  <strong>Explanation:</strong> {currentCard.explanation}
                </p>
              )}
            </div>
            <div style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textAlign: 'center' }}>
              💡 Click or tap card to flip back
            </div>
          </div>
        </div>
      </div>

      {/* Active Recall Response Controls */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr auto 1fr', gap: '0.75rem', alignItems: 'center' }}>
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleNext(false);
          }}
          className="btn btn-secondary"
          style={{ borderColor: 'rgba(244, 63, 94, 0.3)', color: '#fb7185' }}
        >
          ❌ Still Learning
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsFlipped(!isFlipped);
          }}
          className="btn btn-secondary"
          style={{ minWidth: '44px' }}
          title="Flip Card"
        >
          🔄 Flip
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            handleNext(true);
          }}
          className="btn btn-primary"
          style={{ background: 'var(--accent-green)' }}
        >
          ✅ Mastered!
        </button>
      </div>
    </div>
  );
}
