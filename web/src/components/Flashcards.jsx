import React, { useState } from 'react';
import Card from './Card';
import Badge from './Badge';
import ProgressBar from './ProgressBar';
import Icon from './Icon';

/**
 * Interactive 3D Flip Flashcards Mode (Active Recall).
 * Beautiful Red Noir styling with smooth 3D flip animation.
 */
export default function Flashcards({ mcqs = [], title = 'Study Note' }) {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [isFlipped, setIsFlipped] = useState(false);
  const [mastered, setMastered] = useState(new Set());
  const [reviewLater, setReviewLater] = useState(new Set());
  const [isFinished, setIsFinished] = useState(false);

  if (!mcqs || mcqs.length === 0) {
    return (
      <Card style={{ textAlign: 'center', padding: '40px 20px' }}>
        <p style={{ color: 'var(--text-2)', fontSize: '14px' }}>
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
      setTimeout(() => setCurrentIndex((idx) => idx + 1), 180);
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
      <Card style={{ textAlign: 'center', padding: '48px 24px' }}>
        <div style={{ fontSize: '40px', marginBottom: '12px' }}>🎯</div>
        <h2 className="portal-page-title" style={{ fontSize: '24px', marginBottom: '8px' }}>
          Active Recall Session Complete!
        </h2>
        <p style={{ color: 'var(--text-2)', fontSize: '14px', marginBottom: '24px' }}>
          You reviewed all {total} flashcards for {title}.
        </p>

        <div style={{ display: 'flex', justifyContent: 'center', gap: '20px', marginBottom: '28px' }}>
          <div
            style={{
              background: 'rgba(52, 211, 153, 0.12)',
              border: '1px solid rgba(52, 211, 153, 0.3)',
              padding: '16px 28px',
              borderRadius: 'var(--radius-card)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--ok)', fontFamily: 'var(--font-head)' }}>
              {mastered.size}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-2)', marginTop: '4px' }}>Mastered</div>
          </div>

          <div
            style={{
              background: 'var(--accent-soft)',
              border: '1px solid rgba(239, 35, 60, 0.3)',
              padding: '16px 28px',
              borderRadius: 'var(--radius-card)',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '28px', fontWeight: 800, color: 'var(--accent-light)', fontFamily: 'var(--font-head)' }}>
              {reviewLater.size}
            </div>
            <div style={{ fontSize: '12px', color: 'var(--text-2)', marginTop: '4px' }}>Review Later</div>
          </div>
        </div>

        <button onClick={handleRestart} className="portal-btn-primary" type="button">
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
    <div className="flashcards-container">
      {/* Session Progress Header */}
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
        <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-2)' }}>
          Card {currentIndex + 1} of {total}
        </span>
        <div style={{ display: 'flex', gap: '8px' }}>
          <Badge variant="ok">✓ {mastered.size} Mastered</Badge>
          <Badge variant="accent">✗ {reviewLater.size} Needs Review</Badge>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="flashcard-progress-bar">
        <ProgressBar
          value={currentIndex + 1}
          max={total}
          color="var(--accent)"
        />
      </div>

      {/* 3D Flip Card */}
      <div
        className="flashcard-wrapper"
        onClick={() => setIsFlipped(!isFlipped)}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === ' ' || e.key === 'Enter') {
            e.preventDefault();
            setIsFlipped(!isFlipped);
          }
        }}
        aria-label="Flashcard. Click or press Space to flip."
      >
        <div className={`flashcard-inner ${isFlipped ? 'flipped' : ''}`}>
          {/* Front Face */}
          <div className="flashcard-face flashcard-front">
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                <Badge variant="neutral">QUESTION #{currentIndex + 1}</Badge>
                {currentCard.topic && (
                  <Badge variant="accent">{currentCard.topic}</Badge>
                )}
              </div>
              <h3 className="flashcard-question">
                {currentCard.question}
              </h3>
            </div>
            <div className="flashcard-flip-hint">
              💡 Click or tap card to reveal answer
            </div>
          </div>

          {/* Back Face */}
          <div className="flashcard-face flashcard-back">
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
                <Badge variant="ok">CORRECT ANSWER</Badge>
                {currentCard.topic && (
                  <Badge variant="neutral">{currentCard.topic}</Badge>
                )}
              </div>
              <h4 className="flashcard-answer-text">
                {correctOption}
              </h4>
              {currentCard.explanation && (
                <div className="flashcard-explanation-box">
                  <strong style={{ color: 'var(--text)' }}>Explanation:</strong> {currentCard.explanation}
                </div>
              )}
            </div>
            <div className="flashcard-flip-hint">
              💡 Click or tap card to flip back
            </div>
          </div>
        </div>
      </div>

      {/* Active Recall Response Controls */}
      <div className="flashcard-controls">
        <button
          onClick={(e) => {
            e.stopPropagation();
            handleNext(false);
          }}
          className="portal-btn-secondary flashcard-btn-review"
          type="button"
        >
          ❌ Still Learning
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            setIsFlipped(!isFlipped);
          }}
          className="portal-btn-secondary flashcard-btn-flip"
          title="Flip Card (or tap anywhere on the card)"
          type="button"
        >
          <Icon name="bolt" size={14} />
          <span>Flip</span>
        </button>

        <button
          onClick={(e) => {
            e.stopPropagation();
            handleNext(true);
          }}
          className="portal-btn-primary flashcard-btn-mastered"
          type="button"
        >
          ✅ Mastered!
        </button>
      </div>
    </div>
  );
}
