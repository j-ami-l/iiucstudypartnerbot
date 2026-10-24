# SnapStudy AI — IIUC Study Partner Bot

> **Snap a photo of your notes or lecture slide → Get an instant summary, key takeaways, difficult terms, and a practice quiz in English or Bangla.**  
> Built solo for MLH Hackathon powered by **Google Gemma 4**.

---

## 📌 The Problem

University students often sit through fast-paced lectures with dozens of complex slides and messy handwritten notebook pages. Reviewing them later is tedious:
- Manually reading dense textbook pages and slide decks takes hours.
- Copy-pasting text into web chatbots is impossible with handwriting, diagrams, and equations.
- Most students lack immediate self-assessment to test whether they actually understood the lecture.

**Who it's for:** Students who want instant, structured revision and self-testing directly on their phones.  
**Why it's different:** No web dashboard or app login required. Just open Telegram, send a photo of your notes, and get a structured study breakdown and quiz in seconds.

---

## 💡 The Solution

**SnapStudy AI** turns any smartphone into an AI study partner inside Telegram:
1. **Camera In**: Snap a picture of handwritten notes, textbook paragraphs, equations, or lecture slides.
2. **Gemma 4 Vision**: The open-source Gemma 4 model analyzes the visual content and extracts core concepts without hallucinating unseen facts.
3. **Structured Study Output**: Instantly replies with:
   - 📖 **Summary**: Under 120 words capturing core ideas.
   - 💡 **Key Points**: 3 to 6 bullet points of formulas and takeaways.
   - 🔍 **Difficult Terms**: Technical vocabulary defined in simple, plain language.
   - 📝 **5-Question Quiz** *(In Progress)*: Interactive multiple-choice questions with instant scoring.
4. **Bilingual Support**: Fully supports both **English** and **Bangla** (`bn`).

---

## ⚙️ How It Works

### AI Architecture & Model
- **Core Model**: Open-source **Gemma 4** (`google/gemma-4-31b-it`)
- **API Provider**: Hosted via [OpenRouter API](https://openrouter.ai/) (OpenAI-compatible chat completions with vision base64 data URL)
- **Validation**: Strict **Pydantic v2** schema enforcement with automatic single-retry on malformed JSON.
- **Privacy by Design**: **User photos are NEVER stored** on disk or in the database. Images are resized in-memory, analyzed, and immediately discarded.

### Technology Stack
| Layer | Technology | Purpose |
|---|---|---|
| **Language** | Python 3.12+ | Core runtime |
| **Interface** | `python-telegram-bot` v22+ | Async polling bot (zero server setup) |
| **AI Model** | Google Gemma 4 31B | Vision and multimodal reasoning |
| **HTTP Client** | `httpx` (async) | Low-latency async API calls to OpenRouter |
| **Image Processing** | `Pillow` | Aspect-ratio preserving resize (max 1280px) and JPEG compression |
| **Schema Validation** | `pydantic` v2 | Strict JSON structure and type validation |
| **Database** | Built-in `sqlite3` | Zero-dependency local persistence |
| **Testing** | `pytest`, `pytest-asyncio` | Automated unit tests |

### Why Telegram?
Telegram provides zero-friction mobile access. Students already have it installed, camera integration is native, and bots require zero app downloads or account logins.

---

## 📸 Screenshots & Demo

> _[PLACEHOLDER: Add demo screenshot of bot summary reply on Telegram here]_  
> _[PLACEHOLDER: Add 60-second video demo link / animated GIF here]_

---

## 🚀 How to Run Locally

### 1. Prerequisites
- Python 3.12 or newer installed
- A Telegram bot token from [@BotFather](https://t.me/BotFather)
- An OpenRouter API key with access to `google/gemma-4-31b-it`

### 2. Clone and Setup
```bash
git clone https://github.com/j-ami-l/iiucstudypartnerbot.git
cd iiucstudypartnerbot

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt
```

### 3. Configure Environment
Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```
Edit `.env` and fill in your credentials:
```env
TELEGRAM_TOKEN=your_telegram_bot_token_from_botfather
GEMMA_API_KEY=your_openrouter_api_key
GEMMA_BASE_URL=https://openrouter.ai/api/v1
GEMMA_MODEL=google/gemma-4-31b-it
DATABASE_PATH=snapstudy.db
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=60
MAX_IMAGE_SIDE=1280
```

### 4. Run the Gemma Smoke Test (CLI)
Verify model connectivity and schema validation before running the bot:
```bash
# Test with English output
python scripts/test_gemma.py samples/note1.jpg en

# Test with Bangla output
python scripts/test_gemma.py samples/note1.jpg bn
```

### 5. Run Unit Tests
```bash
python -m pytest
```

### 6. Start the Telegram Bot
```bash
python -m app.main
```
Open Telegram, message your bot, and send `/start` or upload a photo of your notes!

---

## 🚧 What's Not Done Yet (Honest Status)

- [x] **F0**: Project skeleton & config loading
- [x] **F1**: Standalone Gemma vision smoke test & schema validation
- [x] **F2**: Telegram photo receiving & image compression pipeline
- [x] **F3**: Gemma note understanding & formatted summary replies
- [ ] **F4**: Interactive inline quiz flow with instant score feedback *(Next)*
- [ ] **F5**: SQLite persistence for user history and notes
- [ ] **F6**: Inline Bangla / English language toggle button
- [ ] **F7**: Reliability & UX polish (typing indicators, friendly error fallback)
- [ ] **G1–G3**: Telegram study group quiz poll mode

---

## 👥 Credits & Hackathon Note

- Built for the **MLH Hackathon** leveraging **Google Gemma 4**.
- Built with the assistance of an agentic coding AI pair programmer following disciplined test-driven feature milestones specified in `AGENT.md` and `PROMPTS.md`.
- No proprietary closed-source models are used for note reasoning; all AI logic is powered by open Gemma 4.
