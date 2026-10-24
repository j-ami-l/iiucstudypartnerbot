# SnapStudy AI — IIUC Study Partner Bot (`@iiucstudypartnerbot`)

> **Snap a photo of your handwritten notes, textbook pages, or lecture slides → Get instant bullet summaries, difficult term explanations, interactive quizzes, 3D flashcards, and weak-topic tracking in English or Bangla.**  
> Built for the Hackathon powered by **Google Gemma 4** (`google/gemma-4-31b-it`).  
> **Telegram Bot Username:** [@iiucstudypartnerbot](https://t.me/iiucstudypartnerbot)

---

## 📌 The Problem

University students (especially in STEM fields like CSE, EEE, and Pharmacy at IIUC) sit through fast-paced lectures with dozens of dense slides, whiteboard diagrams, and handwritten notes. Reviewing them later is painful:
- Scrolling through hundreds of phone gallery photos before exams is slow and disorganized.
- Manually transcribing formulas and handwriting into generic chatbots is tedious and error-prone.
- Students lack immediate self-assessment to discover what they *actually* understood before exam day.
- Existing tools don't understand mixed English/Bangla (Banglish) lecture notes or deliver natural Bangla explanations.

**Who it's for:** University students who want instant, structured revision and self-testing directly from their phone camera.  
**Why it's different:**
1. **Camera-to-Quiz in under 30 seconds**: No manual typing. Snap notes in Telegram and get an immediate breakdown and 5-question practice quiz.
2. **Bilingual Intelligence**: Native English and natural Bangla (`bn`) support tailored for local university coursework.
3. **Zero-Friction Access**: Telegram bot for quick mobile snaps + a passwordless **Red Noir Web Study Portal** for deep active recall revision and analytics.
4. **Privacy-First**: Student photos are processed directly in-memory and **never stored on disk or in the database**.

---

## 💡 Key Features

### 1. 📸 Multimodal Note Understanding (Gemma 4)
- **Instant Bullet Summaries**: Core concepts summarized in under 120 words.
- **Key Points**: 3 to 6 bullet takeaways including equations and definitions.
- **Difficult Terms**: Complex jargon defined in simple, accessible language.
- **Format Support**: Handwritten notebooks, slide screenshots, whiteboard photos, printed textbooks, and JPEG/PNG image documents.

### 2. 📝 Interactive Telegram Quizzes & Scoring
- 5-question multiple-choice quiz generated instantly from your notes.
- In-chat interactive `A, B, C, D` inline buttons with instant answer validation, correct option reveal, and conceptual explanations.
- Final score cards with mastery feedback.

### 3. 🎯 Weak Topics Tracking & Spaced Repetition (`/weak` & `/practice`)
- **`/weak`**: Flags topics where student accuracy falls below 60%.
- **`/practice`**: Generates targeted practice quizzes pulling directly from past mistake questions until mastery is reached.

### 4. 💻 Red Noir Web Study Dashboard (`/portal`)
- Passwordless magic link login via `/portal` with secure 7-day `HttpOnly` sessions.
- **Red Noir Design System**: Calm dark mode aesthetic (`#050506`), glass pill navbar, mobile-friendly bottom tab bar, and self-hosted variable typography (`Manrope`, `Inter`, `Noto Sans Bengali` with zero CDN requests).
- Real-time KPI metrics: notes uploaded, quizzes taken, accuracy progress bar, and weak topics breakdown.
- **Mistake Notebook**: Dedicated view of past mistakes with the correct answers and explanations highlighted.
- **Weekly Analytics**: 6-week SVG/CSS accuracy trend chart.

### 5. ⚡ Interactive 3D Flip Flashcards (Active Recall)
- Switch any note into interactive flip-cards with smooth 3D CSS animation.
- Tap or press `Space`/`Enter` to flip between question and answer.
- Self-assessment controls: *"Still Learning"* vs *"Mastered"* tracking active recall progress.

### 6. ⚔️ "Challenge a Classmate" Deep Links
- On any note or quiz, click **"⚔️ Challenge Classmate"** to copy a Telegram deep link:
  `https://t.me/iiucstudypartnerbot?start=challenge_<note_id>`
- When your friend taps it, the bot greets them with *"⚔️ Classmate Challenge Accepted!"* and immediately serves Question 1 of that exact quiz.

### 7. 🤖 Ask AI Tutor (Gemma 4 Q&A)
- Have a question about a tricky equation or concept in your notes?
- Ask Gemma directly on the web portal to receive simplified explanations and real-world analogies grounded strictly in your study material.

### 8. 🏆 Campus Study League (Weekly Leaderboard)
- Weekly campus leaderboard ranking students by quizzes completed, questions solved, and accuracy.
- Top 3 podium presentation (🥇, 🥈, 🥉) with personalized "YOU" badge.

---

## ⚙️ Technology Stack & Architecture

```
                       ┌────────────────────────────────────────────────────────┐
                       │                     TELEGRAM CLIENT                    │
                       │             @iiucstudypartnerbot                       │
                       │  - Camera Photo Uploads       - /practice              │
                       │  - Interactive Inline Quizzes - /portal                │
                       └───────────────────────────┬────────────────────────────┘
                                                   │
                                                   ▼
┌───────────────────────────────────────────────────────────────────────────────────────────────┐
│                           FASTAPI UNIFIED BACKEND (server.py)                                 │
│  ┌──────────────────────────────┐                 ┌────────────────────────────────────────┐  │
│  │   Telegram Bot Lifespan      │                 │            Portal REST API             │  │
│  │  - python-telegram-bot v21+  │                 │  - /api/dashboard   - /api/weak-topics │  │
│  │  - Async Polling Loop        │                 │  - /api/notes       - /api/mistakes    │  │
│  │  - Drop Pending Updates      │                 │  - /api/history     - /api/leaderboard │  │
│  └──────────────┬───────────────┘                 └───────────────────┬────────────────────┘  │
└─────────────────┼─────────────────────────────────────────────────────┼───────────────────────┘
                  │                                                     │
                  ▼                                                     ▼
     ┌─────────────────────────┐                           ┌─────────────────────────┐
     │  Google Gemma 4 (31B)   │                           │     SQLite Database     │
     │  - OpenRouter Vision    │                           │  - WAL Mode Enabled     │
     │  - Strict Pydantic v2   │                           │  - Persistent SSD Disk  │
     │  - In-Memory Processing │                           │  - Strict User Data     │
     └─────────────────────────┘                           └─────────────────────────┘
```

| Component | Technology | Rationale |
|---|---|---|
| **AI Reasoning & Vision** | Google Gemma 4 31B (`google/gemma-4-31b-it`) via OpenRouter | High accuracy open-weights multimodal vision model capable of parsing complex handwriting and Bengali. |
| **Bot Framework** | `python-telegram-bot` v21+ | Native async engine handling photos, callbacks, deep links, and inline keyboards. |
| **Backend & Web Server** | FastAPI + Uvicorn | High-performance async ASGI server with automated `lifespan` orchestration. |
| **Web Frontend** | React 18 + Vite | Lightweight, fast SPA with Red Noir design tokens and 3D card flips. No heavy UI kits. |
| **Typography** | `@fontsource` (Manrope, Inter, Noto Sans Bengali) | Self-hosted variable fonts eliminating CDN requests and ensuring zero layout shifts or clipped Bengali characters. |
| **Persistence** | SQLite (WAL mode) | Embedded zero-latency relational persistence for notes, quizzes, mistakes, and user stats. |
| **Validation** | Pydantic v2 | Strict JSON schema parsing with automatic retry on malformed model responses. |

---

## 🔒 Privacy & Security by Design

- **Photos are NEVER stored**: Images sent by students are compressed in-memory, converted to a temporary base64 data URL for Gemma 4 analysis, and immediately discarded. No photo files exist in storage.
- **Isolated User Data**: All notes, quizzes, and stats in SQLite are strictly scoped to the student's unique Telegram ID.
- **Signed HttpOnly Cookies**: Web portal authentication uses cryptographic single-use magic tokens exchanged for a signed 7-day `HttpOnly` `SameSite=Lax` cookie. No auth tokens are ever exposed in `localStorage`.

---

## 🚀 Running Locally

### 1. Prerequisites
- Python 3.11+ installed
- Node.js 18+ and npm installed
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An OpenRouter API key with access to `google/gemma-4-31b-it`

### 2. Clone and Setup
```bash
git clone https://github.com/j-ami-l/iiucstudypartnerbot.git
cd iiucstudypartnerbot

# Create and activate Python virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies and build SPA
cd web
npm install
npm run build
cd ..
```

### 3. Configure Environment Variables
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Fill in your credentials:
```env
TELEGRAM_TOKEN=your_telegram_bot_token_from_botfather
BOT_USERNAME=iiucstudypartnerbot
GEMMA_API_KEY=your_openrouter_api_key
GEMMA_BASE_URL=https://openrouter.ai/api/v1
GEMMA_MODEL=google/gemma-4-31b-it:free
DATABASE_PATH=snapstudy.db
LOG_LEVEL=INFO
PORTAL_SECRET=any_random_32_character_string_here
PORTAL_BASE_URL=http://localhost:8000
PORTAL_HOST=0.0.0.0
PORTAL_PORT=8000
```

### 4. Run Automated Test Suite
Verify that all unit and isolation tests pass:
```bash
python -m pytest
```
*(All 61 test cases should pass cleanly).*

### 5. Launch the Unified Service
Start the single-service server (runs both the Telegram bot polling and the FastAPI portal on port 8000):
```bash
uvicorn server:app --host 0.0.0.0 --port 8000
```
- Open `http://localhost:8000/healthz` → returns `{"status": "ok"}`
- Open `http://localhost:8000/dashboard` → displays the study portal
- Open Telegram and message [@iiucstudypartnerbot](https://t.me/iiucstudypartnerbot) to start learning!

---

## 🌐 Cloud Deployment Guide

### Deploying on Render (Unified Single Service)
1. Push your repository to GitHub.
2. In [Render Dashboard](https://dashboard.render.com/), select **New +** → **Blueprint** and connect your repository (it will auto-detect [`render.yaml`](file:///e:/projects/hacktoberfest/render.yaml)).
3. Fill in your environment variables (`TELEGRAM_TOKEN`, `GEMMA_API_KEY`, `BOT_USERNAME`, `PORTAL_BASE_URL`).
4. Render mounts a 1 GB persistent SSD disk at `/var/data` to ensure notes and quiz history persist across deployments.

### Split Deployment (Frontend on Vercel + Backend on Render)
- **Vercel**: Import the repository, set Root Directory to `web`, Framework to `Vite`. The included [`web/vercel.json`](file:///e:/projects/hacktoberfest/web/vercel.json) rewrites `/api/*` requests to your Render backend to prevent cross-origin cookie issues.
- **Render**: Deploy `server.py` as a web service and set `PORTAL_BASE_URL=https://your-app.vercel.app`.

---

## 🤖 Available Bot Commands

| Command | Description |
|---|---|
| `/start` | Welcome onboarding guide and study session initialization. |
| `/portal` | Generates a 24-hour secure magic link to open your personal web dashboard. |
| `/weak` | Displays your current weak topics (accuracy < 60%) and correct/attempt ratio. |
| `/practice` | Launches targeted revision quizzes from questions you previously missed. |
| `/help` | Detailed study tips, photo guidelines, and command list. |

---

## 👥 Credits & Hackathon Note

- Built for the **Hacktoberfest Hack Day Chittagong x IEEE Computer Society IIUC SBC** MLH event.
- **AI Core:** Google Gemma 4 (`google/gemma-4-31b-it`) hosted via OpenRouter.
- Built with the assistance of agentic AI pair programming following rigorous test-driven milestones (`AGENT.md`, `AGENT_PORTAL.md`, `UI_PORTAL.md`).
