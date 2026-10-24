import React from 'react';
import ShinyButton from './ShinyButton';
import Icon from './Icon';

/**
 * PracticeCard: The state-driven practice card on Dashboard.
 * Follows exact UI_PORTAL.md Section 5.1 specifications:
 *
 * | Data                           | What the card shows                                             |
 * |--------------------------------|-----------------------------------------------------------------|
 * | Mistakes / Weak topics > 0     | "You have N questions to fix." + ShinyButton "Practice in Telegram" |
 * | Quizzes = 0                    | "Take your first quiz in Telegram." + secondary link "Open the bot" |
 * | Quizzes > 0 and no mistakes    | "No mistakes to practice 🎉" (no button)                        |
 */
export default function PracticeCard({
  quizzesTaken = 0,
  weakCount = 0,
  botUsername = 'iiucstudypartnerbot',
}) {
  const telegramBase = `https://t.me/${botUsername || 'iiucstudypartnerbot'}`;
  const practiceLink = `${telegramBase}?start=practice`;

  // State 1: Has mistakes / weak topics to fix
  if (weakCount > 0) {
    return (
      <div className="portal-practice-card card-state-active">
        <div className="practice-header">
          <div className="practice-badge">
            <Icon name="target" size={16} />
            <span>Practice</span>
          </div>
          <div className="practice-pulse" aria-hidden="true" />
        </div>
        <div className="practice-body">
          <h3 className="practice-title">
            You have {weakCount} {weakCount === 1 ? 'topic' : 'topics'} needing practice.
          </h3>
          <p className="practice-desc">
            Revisit questions you got wrong to turn weak topics into 100% mastery.
          </p>
        </div>
        <div className="practice-action">
          <ShinyButton
            href={practiceLink}
            target="_blank"
            rel="noopener noreferrer"
            icon={<Icon name="bolt" size={16} />}
          >
            Practice in Telegram
          </ShinyButton>
        </div>
      </div>
    );
  }

  // State 2: No quizzes taken yet
  if (quizzesTaken === 0) {
    return (
      <div className="portal-practice-card card-state-idle">
        <div className="practice-header">
          <div className="practice-badge">
            <Icon name="target" size={16} />
            <span>Get Started</span>
          </div>
        </div>
        <div className="practice-body">
          <h3 className="practice-title">Take your first quiz in Telegram.</h3>
          <p className="practice-desc">
            Send a photo of your notes to the bot to generate an instant summary and quiz.
          </p>
        </div>
        <div className="practice-action">
          <a
            href={telegramBase}
            target="_blank"
            rel="noopener noreferrer"
            className="portal-btn-secondary"
          >
            Open the bot <Icon name="arrow-right" size={14} />
          </a>
        </div>
      </div>
    );
  }

  // State 3: Quizzes > 0 and 0 mistakes
  return (
    <div className="portal-practice-card card-state-mastered">
      <div className="practice-header">
        <div className="practice-badge badge-mastered">
          <Icon name="check" size={16} />
          <span>All Clear</span>
        </div>
      </div>
      <div className="practice-body">
        <h3 className="practice-title">No mistakes to practice 🎉</h3>
        <p className="practice-desc">
          Outstanding job! You have answered all quiz questions accurately.
        </p>
      </div>
    </div>
  );
}
