# AGENT.md — SnapStudy AI

> A Telegram study assistant. A student sends a photo of notes or a lecture slide.
> Gemma 4 reads it and replies with a summary, key points, difficult terms and a
> 5-question quiz, in Bangla or English. Built solo for an MLH hackathon (4–6 hours).

You are the coding agent for this project. Read this whole file before writing any code.

---

## 0. THE MOST IMPORTANT RULE: WORK FEATURE BY FEATURE

Build **one feature at a time**, in the order of Section 9. Never build ahead.

For every feature, follow this loop exactly:

1. **Announce** which feature you are starting (e.g. "Starting F3: Summary reply").
2. **Plan** in 3–6 bullets: which files you will create or change. Keep it short.
3. **Implement** only what that feature's acceptance criteria require. Nothing extra.
4. **Self-check**: run the code, the linter and any tests you can. Fix what breaks.
5. **Report** using this exact format, then **STOP**:
   - ✅ What was built (files touched)
   - 🧪 **How I test it** (exact commands and exact Telegram steps, with expected output)
   - 🧠 **How it works in 3 lines** (so the human can explain this part to judges)
   - ⚠️ Known limits or open questions
   - ➡️ Next feature (name only)
6. **Wait for the human to say "next" or report a bug.** Do not start the next feature on your own.
7. Commit after each feature that the human approves, using the message format `feat(F3): summary reply`.

If you are blocked or unsure (API provider, model name, an ambiguous requirement), **ask one short
question and stop**. Never guess an endpoint, key name or model string and keep going.

If a feature turns out bigger than expected, build the smallest working version, say what you
cut, and stop. A small thing that works beats a big thing that half works.

---

## 1. Product in one paragraph

Student opens Telegram, sends a photo of handwritten notes or a slide. The bot shows
"Reading your notes…", then replies with a short summary, key points and difficult terms,
plus buttons. Pressing **Quiz** starts a 5-question multiple-choice quiz with instant
feedback and a final score. A language toggle switches everything between English and Bangla.

**Group mode:** the bot can also be added to a Telegram group. A member replies to a photo of
notes with `/summary@BotName` or `@BotName quiz`, and the bot answers in the group with a compact
summary and a short quiz made of native Telegram quiz polls. See Section 4.5 and features G1–G3.

**Primary demo (everything else is secondary):**

photo in → Gemma reads it → summary → quiz → score, in under one minute.

**Who it is for and why it is different** (the README "The problem" section must say this plainly):

- **Users:** university students (IIUC first) who photograph whiteboards, slides and handwritten
  notes and then have no quick way to revise from them. Today they scroll through photos, ask
  friends, or retype notes into a general chatbot.
- **Different from a generic "notes to quiz" tool:** it handles Bangla and mixed Bangla/English
  (Banglish) notes, the Bangla output must read naturally, a class group can quiz itself from one
  photo (group mode), and it needs no new app or account beyond Telegram.

---

## 2. Hackathon rules the code must respect

- Core model is **open-source Gemma 4**. No closed-model APIs. The README must name the model and the provider.
- The interface is a **Telegram bot**. No web UI, no React, no dashboard.
- **No secrets in the repo.** `.env` is gitignored. Provide `.env.example`.
- **No model weights in the repo.**
- **No fake demos.** Never hardcode answers and present them as model output.
- Use only made-up or self-made sample notes. Never store or commit real students' personal data.
- Every part of the code must be explainable by the human, so keep it simple and readable.
- `AGENT.md` and `PROMPTS.md` are planning documents written before the event. The application code
  is written during the event. The README credits must say that an AI coding agent was used and that
  these planning files exist.
- The bot runs by polling on the human's machine, so it is only live while the process runs. The
  README must say this honestly and include a demo video or GIF as a backup for judges.

---

## 3. Tech stack

| Part | Choice | Why |
|---|---|---|
| Language | Python 3.12+ | |
| Bot | `python-telegram-bot` v21+ (async, **polling mode**) | No web server needed |
| AI | Gemma 4 via a hosted API (provider set in `.env`) | Image understanding |
| HTTP | `httpx` (async) | |
| Image | `Pillow` | Resize and compress before upload |
| Validation | `pydantic` v2 | Validate the model's JSON |
| DB | built-in `sqlite3` | Zero setup |
| Config | `python-dotenv` | |
| Logging | built-in `logging` | |
| Tests | `pytest`, `pytest-asyncio` | Small, only for pure logic |

**Do NOT add:** FastAPI, SQLAlchemy, structlog, Docker, Redis, Celery, OAuth, any web
frontend, any CI/CD, any analytics. They cost hackathon time and add no demo value.

---

## 4. Architecture

### 4.1 Folder structure

```
snapstudy/
├── AGENT.md
├── PROMPTS.md
├── README.md                  # written in the last feature (F10)
├── .env.example
├── .gitignore
├── requirements.txt
├── scripts/
│   ├── __init__.py
│   └── test_gemma.py          # F1: run as  python -m scripts.test_gemma <image> en|bn
├── samples/                   # self-made sample notes/slides (small files)
│   └── README.md
├── app/
│   ├── __init__.py            # every folder under app/ and scripts/ has an __init__.py
│   ├── main.py                # builds the Application, registers handlers, runs polling
│   ├── config.py              # loads .env into a typed Settings object
│   ├── logging_setup.py       # logging config
│   ├── schemas.py             # Pydantic models: QuizResult, MCQ
│   ├── db.py                  # sqlite3: sync functions, one short-lived connection per call, WAL, all queries
│   ├── i18n.py                # all user-facing strings in en and bn
│   ├── keyboards.py           # all inline keyboards
│   ├── ai/
│   │   ├── gemma_client.py    # the ONLY file that talks to Gemma
│   │   └── json_utils.py      # extract and repair JSON from model text
│   ├── prompts/
│   │   ├── summary_prompt.md  # plain-text summary prompt (streamed to the user)
│   │   └── quiz_prompt.md     # JSON quiz prompt (runs in the background)
│   ├── services/
│   │   ├── study_service.py   # image + language -> streamed summary + background quiz job
│   │   └── quiz_service.py    # quiz progress, answer checking, scoring
│   ├── handlers/
│   │   ├── start.py           # /start, /help
│   │   ├── photo.py           # receives photos, calls StudyService
│   │   ├── quiz.py            # quiz button callbacks
│   │   ├── settings.py        # language toggle, /language
│   │   └── group.py           # G1–G3: reply-to-photo requests in groups, group quiz polls
│   └── utils/
│       ├── image.py           # resize + compress, bytes in -> bytes out (pure, no Telegram)
│       ├── guards.py          # KeyedLocks, in-flight sets, cooldown timers (pure, in-memory)
│       ├── formatting.py      # build message text (HTML), split long messages
│       └── intent.py          # parse group requests: action + language (pure function)
└── tests/
    ├── test_json_utils.py
    ├── test_quiz_service.py
    ├── test_formatting.py
    ├── test_intent.py
    └── test_guards.py
```

### 4.2 Layer rules (the only "clean architecture" we need)

```
Telegram update
      │
      ▼
 handlers/        parse input, call a service, send reply. NO AI code, NO SQL.
      │
      ▼
 services/        business logic. Orchestrates ai/, db.py, utils/.
      │
      ├──► ai/gemma_client.py     only place that makes HTTP calls to the model
      ├──► db.py                  only place that runs SQL
      └──► utils/                 pure helpers
```

- Handlers never import `httpx` or `sqlite3`.
- `ai/` never imports `telegram`.
- `db.py` never imports `telegram` or `ai`.
- Services take their dependencies (client, db) as constructor arguments. Plain constructor injection, no framework.
- Keep each file under about 250 lines. Split only when a file gets hard to read.
- Downloading the photo from Telegram (`bot.get_file` then bytes) is the **handler's** job.
  `utils/image.py` only transforms bytes, so it stays pure and testable.
- `db.py` exposes plain sync functions. Services call them with `await asyncio.to_thread(...)`.
  Each call opens its own short-lived connection, so no connection is shared across threads.
- Updates run concurrently (see 4.4 rule 9). Shared in-memory state (quiz progress, the quiz-task
  dict, in-flight sets) is changed only inside a short `KeyedLocks` section from `utils/guards.py`.
  Never `await` a model call while holding such a lock.

### 4.3 Data flow (two parallel calls: this is the speed design)

Why: one giant call ("summary + 5 MCQs + terms + questions") makes the user wait for the whole
generation before seeing anything. Instead we split the work and overlap it. The model reads
the image directly, so there is **no separate OCR/scan step**.

```
User sends photo
  → handlers/photo.py
      sends "⏳ Reading your notes…" + typing indicator
      downloads the largest photo size
  → utils/image.py            resize (max side 1024), JPEG q~75, in a worker thread
  → services/study_service.py
      sha256(resized JPEG bytes + language + style) → cache hit? reply from DB instantly, done
        (skipped when force=True, which is what 🔁 Regenerate uses)
      otherwise encode the image to base64 ONCE and start two calls at the same time:
        ┌ SUMMARY call: small output, STREAMED   → shown to the user as it arrives
        └ QUIZ call:    JSON, 5 MCQs, background → stored as an asyncio task
  → handlers/photo.py
      edits the Telegram message as summary text streams in (max ~1 edit/second)
      when the summary finishes, attaches the buttons
User presses 📝 Quiz
  → quiz task finished?  send question 1 instantly
  → still running?       show "⏳ Preparing your quiz…" and await the SAME task
                         (never start a second quiz call)
User presses 🔁 Regenerate
  → same pipeline with force=True: no cache read, and the new result becomes the newest cache row
```

Timing targets (measure them in F1 and adjust; these are targets, not promises):
- first summary text on screen: about 10–15 s
- full summary: about 20 s
- quiz ready: about 30 s after the photo, usually before the user taps Quiz

### 4.4 Speed rules (follow all of them)

1. **Output tokens are the main cost.** Fewer tokens generated means a faster answer. Hard limits:
   summary at most 80 words, at most 4 key points, at most 4 terms, each MCQ explanation one
   sentence. Set `max_tokens` on every call. Bangla needs several times more tokens per word than
   English, so caps are **per language**: `SUMMARY_MAX_TOKENS` and `QUIZ_MAX_TOKENS` for `en`,
   `SUMMARY_MAX_TOKENS_BN` and `QUIZ_MAX_TOKENS_BN` for `bn`. Measure real token counts for both
   languages in F1 and set each cap with about 30% headroom. If the provider counts reasoning
   tokens inside `max_tokens`, include them in the measurement. A cap that cuts the JSON in half is
   the most likely cause of "bad quiz" bugs.
2. **Two parallel calls, never one big call, never a chain.** No "OCR first, then summarize,
   then quiz". Each call gets the image directly.
3. **Stream the summary as plain text** (not JSON, because half a JSON object can't be shown).
   Edit the Telegram message at most once per second to stay under Telegram rate limits. If the
   provider does not support streaming, fall back to a normal call and say so in your report.
   In group chats never stream (see 4.5). Handle Telegram edit errors while streaming:
   `BadRequest: message is not modified` is ignored, and `RetryAfter` means skip that edit (do not
   sleep). The final edit always carries the complete text.
4. **Small images.** Max side 1024 px, JPEG quality about 75, done with Pillow in
   `asyncio.to_thread` so the event loop is not blocked. Only raise to 1280 if handwriting is
   misread (the human decides after F1).
5. **One shared `httpx.AsyncClient`** for the whole app (keep-alive connections), created at
   startup. Send one tiny warm-up request at startup so the first user doesn't pay cold-start time.
6. **Cache by image hash.** Key: `sha256(resized JPEG bytes + language + style)`. A repeated photo
   returns the stored real model output instantly. Log "cache hit". Mention the cache in the README.
   `🔁 Regenerate` bypasses the cache (`force=True`). Only one model run per key may be in flight:
   keep a dict `cache_key → task`, and a second identical request awaits the same task.
7. **Generate only the user's chosen language.** Never both at once.
8. **Retry policy.** Retry only fast failures (connection errors, 429, 5xx) once with a short
   backoff. After a timeout, do not auto-retry (it doubles the wait); tell the user. For invalid
   quiz JSON, retry the quiz call once.
9. **Concurrency.** Build the bot with `concurrent_updates(True)` so a slow model call never
   blocks other users or other button presses. Because updates now run concurrently, any change to
   shared state follows the `KeyedLocks` rule in 4.2.
10. **Perceived speed.** Typing indicator while waiting, and stage messages:
    "Reading…" → streamed summary → quiz ready.
11. **Optional faster model for the summary.** If the provider offers a smaller Gemma 4 variant,
    allow `GEMMA_SUMMARY_MODEL` to use it for the summary call only. Default is the same as
    `GEMMA_MODEL`. The human decides after comparing timings in F1.
12. **Log stage timings:** image download, resize, summary first token, summary total, quiz total.
13. **Per-user guard in private chat.** Each photo costs two API calls, so allow one in-flight photo
    request per user plus a short gap (`USER_COOLDOWN_SECONDS`). A second photo meanwhile gets one
    gentle message ("⏳ Still working on your last photo."). This protects the API quota.

### 4.5 Group mode design

Goal: in a group, a member **replies to a photo** and calls the bot. The bot answers in the group
in a way that is short, shared and does not flood the chat.

```
Member A posts a photo of notes in the group
Member B replies to that photo with   /summary@BotName    or    @BotName quiz
  → handlers/group.py
      ignore senders that are bots, and anything not addressed to this bot
      utils/intent.py parses the text: action (summary | quiz) + language override
      finds the photo: message.reply_to_message.photo[-1]
        (or the message's own photo when its caption triggers the bot)
      chat guard: per-chat cooldown + one request at a time
      replies TO THE PHOTO MESSAGE with "⏳ Reading…"
  → services/study_service.py   same service as private chat, but style="compact"
      cache lookup, then the same two parallel calls (no streaming in groups)
  → handlers/group.py   edits the placeholder ONCE with the compact summary + [📝 Quiz]
Anyone taps 📝 Quiz (or a request said "quiz")
  → native Telegram quiz polls, one at a time, first GROUP_QUIZ_LENGTH questions
```

| | Private chat | Group chat |
|---|---|---|
| Output size | full (80 words, 4 points, 4 terms) | compact (60 words, 3 points, 3 terms) |
| Streaming | yes | no, one single edit |
| Quiz | inline-button questions, personal score | native quiz polls, shared, first 3 questions |
| Language | per user | per chat default, keyword override |
| Buttons | Quiz, Regenerate | Quiz only |
| Reply target | the user's message | the original photo message |
| Spam control | per-user in-flight guard + short cooldown | per-chat cooldown + in-flight guard |
| State | `user_data` | `chat_data` |

Rules:
- **Triggers.** Commands `/summary`, `/quiz` (also in the `/summary@BotName` form) and mentions
  `@BotName` with optional keywords `summary`, `quiz`, `bn` / `bangla`, `en` / `english`.
  A bare mention means summary. Anything else is ignored. Never answer other bots (loop risk) or yourself.
- **Telegram privacy mode.** In groups a bot sees only a limited set of messages by default. The
  command form `/summary@BotName` is the one that is reliably delivered. Plain `@BotName`
  mentions may need privacy mode turned off (BotFather → `/setprivacy` → Disable, then remove
  and re-add the bot to the group) or the bot made an admin. Support both forms, and in G1 tell
  the human which one works in their test group.
- **Message budget.** Telegram limits groups to roughly 20 messages per minute. So: one
  placeholder message edited once, polls sent one at a time, no extra chatter.
- **Forum groups (topics).** Reply inside the same topic as the request.
- **Privacy.** Do not store photos from groups either. `/help` says: photos are not stored, but the
  AI-generated summary and quiz are saved and may be reused when the same photo is sent again, so
  do not send private information.
- **Poll limits.** Quiz polls allow about 300 characters for the question, 100 per option and
  200 for the explanation. Truncate defensively with a safe margin (see 6.2).

---

## 5. Environment variables

`.env.example` (commit this), real `.env` is gitignored:

```
TELEGRAM_TOKEN=
GEMMA_API_KEY=
GEMMA_BASE_URL=
GEMMA_MODEL=
DATABASE_PATH=snapstudy.db
LOG_LEVEL=INFO
REQUEST_TIMEOUT_SECONDS=60
MAX_IMAGE_SIDE=1024
GEMMA_SUMMARY_MODEL=            # optional: smaller/faster Gemma 4 variant for the summary call
SUMMARY_MAX_TOKENS=350       # en. Starting values, tune in F1 from measured token counts
QUIZ_MAX_TOKENS=900          # en
SUMMARY_MAX_TOKENS_BN=700    # bn needs far more tokens per word
QUIZ_MAX_TOKENS_BN=2000      # bn
GROUP_QUIZ_LENGTH=3          # how many of the 5 questions a group plays
GROUP_COOLDOWN_SECONDS=15    # minimum gap between requests in one group
USER_COOLDOWN_SECONDS=5      # minimum gap between photo requests from one user in private chat
MAX_DOWNLOAD_MB=10           # reject larger files before downloading
```

**Provider note:** the exact Gemma 4 provider, base URL and model string are decided by the
human. In F1, if they are not in `.env`, **ask the human and stop**. Write `GemmaClient` so
the provider is swappable by config. Default to an OpenAI-compatible chat-completions format
with the image sent as a base64 `data:` URL. If the chosen provider uses a different request
shape, adapt inside `gemma_client.py` only.

---

## 6. The AI contract (two prompts, two calls)

### 6.1 Summary prompt (`app/prompts/summary_prompt.md`): plain text, streamed

Stored as a file with a `{language}` placeholder. Must tell the model to:

- Read the image carefully (handwriting, slides, diagrams, equations).
- Write in `{language}` (English or Bangla).
- Obey `{style}`: `full` uses the limits below. `compact` (used in groups) means at most 60 words,
  3 key points and 3 terms, with the same layout.
- Use exactly this layout, with no markdown symbols other than a leading "- ":

```
📝 Summary
<at most 80 words>

🔑 Key points
- <3 to 4 short points>

📖 Difficult terms
- <term>: <short meaning>   (at most 4)
```

- If the image is unreadable or is not study material, reply with exactly: `UNREADABLE`
- Never invent content that is not visible in the image.

The bot shows this text (after `html.escape`) exactly as received. No parsing is needed.

### 6.2 Quiz prompt (`app/prompts/quiz_prompt.md`): JSON only, background

Must tell the model to return **only** JSON, no fences and no commentary, JSON keys in English,
values in `{language}`:

```json
{
  "mcqs": [
    {
      "question": "string",
      "options": ["A text", "B text", "C text", "D text"],
      "correct_index": 0,
      "explanation": "one short sentence"
    }
  ],
  "short_questions": ["string", "... 2 to 3 items"]
}
```

Validated by Pydantic (`QuizResult` in `schemas.py`):
- Target is **5** MCQs, exactly **4** options each, `correct_index` 0 to 3. Accept **3 to 5**:
  drop any single MCQ that is invalid and fail only if fewer than 3 valid ones remain. Private chat
  plays however many valid MCQs came back. Groups play `min(GROUP_QUIZ_LENGTH, count)`.
- Every MCQ must fit a Telegram poll: question at most 250 characters, each option at most 80,
  explanation at most 180. Ask for this in the prompt, then **truncate first and validate second**
  so a slightly long option never causes a pointless retry.
- If unreadable: `{"error": "unreadable"}`.
- If the provider reports the output was cut off (finish reason `length`), that is `GemmaTruncated`,
  not bad JSON.
- The quiz call gets at most **one** retry in total, whatever the cause: truncation retries once with
  the cap raised by 50%, invalid JSON retries once with a stricter reminder. After that, a friendly
  error. Never crash.
- `json_utils.py` must handle fenced code blocks, leading or trailing prose and trailing commas.

### 6.3 `GemmaClient` interface

```python
class GemmaClient:
    async def stream_summary(self, image_b64: str, language: str) -> AsyncIterator[str]: ...
    async def get_summary(self, image_b64: str, language: str) -> str: ...  # non-streaming fallback
    async def get_quiz(self, image_b64: str, language: str) -> str: ...     # raw JSON text
```

The image is base64-encoded once by the service and passed to both calls. No parsing inside the
client. Log latency for every call, and log the token counts and finish reason when the provider returns
them. Pick the `max_tokens` cap from the language. Apply timeouts. Raise typed errors
(`GemmaTimeout`, `GemmaAPIError`, `GemmaTruncated`) that the service converts into friendly
messages.

### 6.4 Background quiz job

`StudyService` starts the quiz call with `asyncio.create_task` right after the summary call
starts, and keeps the task in an in-memory dict keyed by `note_id`. The quiz handler awaits that
task. If the task failed, retry it once on demand when the user taps Quiz. A second dict keyed by cache
key (see 4.4 rule 6) makes sure two identical requests never start two model runs. Remove finished jobs
after about 30 minutes so memory does not grow.

---

## 7. Database (sqlite3, created on startup if missing)

```sql
CREATE TABLE IF NOT EXISTS users (
  telegram_id INTEGER PRIMARY KEY,
  name        TEXT,
  language    TEXT NOT NULL DEFAULT 'en',      -- 'en' | 'bn'
  created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS notes (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  telegram_id INTEGER NOT NULL,
  language    TEXT NOT NULL,
  style       TEXT NOT NULL DEFAULT 'full',    -- 'full' | 'compact'
  image_hash  TEXT NOT NULL,                   -- sha256(resized JPEG bytes + language + style), the cache key
  file_id     TEXT,                            -- Telegram file_id (an identifier, not image data): re-fetch for F6
  file_unique_id TEXT,                         -- Telegram file_unique_id: pre-download cache lookup (G3)
  summary_text TEXT NOT NULL,
  quiz_json   TEXT,                            -- validated QuizResult, NULL until the quiz call finishes
  created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_notes_hash ON notes(image_hash);

CREATE TABLE IF NOT EXISTS quiz_attempts (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  note_id     INTEGER NOT NULL,
  telegram_id INTEGER NOT NULL,
  score       INTEGER NOT NULL,
  total       INTEGER NOT NULL,
  created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
```

- **Do not store the photo** (privacy and simplicity). Store only the result JSON.
- In-progress quiz state (current index, score so far) lives in `context.user_data`. Losing it on restart is acceptable. Mention this in "What's not done yet".
- Use parameterized queries only.
- **Threading:** one short-lived connection per call (`sqlite3.connect(path, timeout=5)`), called
  through `asyncio.to_thread`. Run `PRAGMA journal_mode=WAL` once at startup.
- **Cache rows:** a cache hit inserts a **new** `notes` row for the requesting user, copying
  `summary_text` and `quiz_json`, so quiz attempts link to that user's note. A lookup returns the
  newest row for an `image_hash` that has a `summary_text`.
- `file_id` and `file_unique_id` are Telegram identifiers, not photos. They let a note be re-fetched
  for the language toggle (F6) and let groups skip the download on repeats (G3).

---

## 8. Telegram UX rules

- **Callback data** is limited to 64 bytes. Use short ids, e.g. `qa:{note_id}:{q_index}:{option_index}`, `lang:bn`, `lang:bn:{note_id}` (toggle under a summary), `act:quiz:{note_id}`, `act:regen:{note_id}`. Never put quiz text in callback data.
- **Parse mode: HTML.** Escape user and model text with `html.escape`. Do **not** use MarkdownV2.
- **Message limit** is 4096 characters. Split long replies at paragraph boundaries.
- Always send a "⏳ Reading your notes…" message first, then edit or replace it with the result.
- Always answer callback queries (`await query.answer()`) so the button spinner stops.
- When editing messages, treat `BadRequest: message is not modified` as a no-op and `RetryAfter` as
  "skip this edit". Never let either reach the global error handler as a user-visible failure.
- All user-facing text lives in `i18n.py` as `en` and `bn` dicts. No hardcoded strings in handlers.
- Friendly errors only. The user never sees a stack trace or raw JSON.
- Ignore or politely reject non-photo, non-command messages ("Send me a photo of your notes 📷").
- If the user sends a photo as a **document** (uncompressed file), accept it too if it is an image MIME type.

---

## 9. Feature list (build in this order, one at a time)

**Order:** F0 → F7, then G1 → G3 (group mode), then stretch (G4, F8, F9). F10 is always last.

**All features stay in scope.** If time runs short, drop work from the bottom of this list, in this
order: G4, F9, F8, G3, then G2 and G1. F0 → F7 plus F10 is always the minimum to submit. Right after
F3 works, ask the agent for a README skeleton and commit it, and take screenshots of each working
feature as you go, so the final hour is not spent on documentation.

Each feature has **acceptance criteria** and a **"Human test"**. Do not mark a feature done until
its acceptance criteria hold and you have told the human exactly how to test it.

### F0 — Project skeleton
- Create folders (each with an `__init__.py`), `requirements.txt`, `.gitignore` (must include `.env`, `*.db`, `*.db-*`, `__pycache__/`, `.venv/`), `.env.example`, `config.py`, `logging_setup.py`.
- `python -m app.main` starts without crashing and logs "SnapStudy starting".
- **Human test:** create venv, `pip install -r requirements.txt`, run the command, see the log line.

### F1 — Gemma smoke test and speed test (standalone, no Telegram)
- `python -m scripts.test_gemma <image_path> [en|bn] [--max-side 1024]` (run from the project root, so `app.*` imports work) resizes the image, then runs the
  **summary call and the quiz call in parallel** using `ai/gemma_client.py` and the real prompt files.
- Prints: the summary text, the validated quiz JSON, the time to first summary token, the total
  summary time, the quiz time and the **total wall-clock time**.
- Implement `gemma_client.py`, `json_utils.py`, `schemas.py` and both prompt files here.
- Prints a clear error for timeout, auth failure, bad JSON, truncated output and `UNREADABLE`.
- Prints token counts and the finish reason for each call when the provider returns them, and warns
  loudly if any call stopped because of the length cap. Use this to set the per-language caps
  (4.4 rule 1). Bangla is the case most likely to be cut off.
- **Human test:** run it on a handwritten photo and on a slide photo, in `en` and `bn`. Then run the
  same photo with `--max-side 768`, `1024` and `1280`. Compare readability against time.
  Check that the summary is correct, the quiz JSON is valid and Bangla reads naturally.
  Also try one slide that mixes Bangla and English (and one with Arabic text if you have it).
- Report the timings to the agent and decide: image size, whether a smaller model for the summary
  helps, and whether streaming works on your provider.
- **This is the riskiest feature. Do not start F2 until the human confirms F1 works and is fast enough.**

### F2 — Bot receives a photo
- `/start` sends a welcome message. Sending a photo replies "⏳ Reading your notes…" and then "✅ Got your photo (WxH, N KB)". No AI yet.
- Implements `main.py`, `handlers/start.py`, `handlers/photo.py`, `utils/image.py` (the handler downloads the bytes; `utils/image.py` resizes and compresses them).
- **Human test:** talk to the bot, send a photo, see the confirmation with size info.

### F3 — Summary reply (streamed)
- Photo → `StudyService` → starts the quiz call in the background and the summary call at once.
- The summary text streams into the Telegram message (edit at most once per second). When it is
  complete, attach the buttons `📝 Quiz` and `🔁 Regenerate`.
- Fall back to a normal non-streaming call if streaming is not supported, and tell the human.
- Apply the edit-error rules from 4.4 rule 3 (ignore "not modified", skip on `RetryAfter`, always finish with a full-text edit).
- `UNREADABLE` and timeouts get friendly messages.
- Implements `study_service.py`, `utils/formatting.py` (escape and split text).
- **Human test:** send a real note photo. The first text should appear in about 10–15 seconds.
  Send a blurry or irrelevant photo and get a friendly error.

### F4 — Quiz flow (uses the background job)
- Pressing `📝 Quiz`: if the quiz task is done, send question 1 immediately. If not, show
  "⏳ Preparing your quiz…" and await the same task. If the task failed, retry it once.
- Each question has A–D buttons. After an answer show ✅/❌, the explanation and `Next ➡️`.
  After question 5 show the score (e.g. 4/5) and `🔁 Retry quiz`, `📷 New note`.
- Implements `quiz_service.py`, `handlers/quiz.py`, `keyboards.py`.
- Guard against double-taps (per-user `KeyedLocks` plus the index check) and stale buttons (after a restart): reply "This quiz expired, send the note again."
- **Human test:** tap Quiz right after the summary appears (quiz may still be loading), and tap it
  again later (should be instant). Finish a full quiz with right and wrong answers and see the score.

### F5 — SQLite persistence and image cache
- Create the schema on startup. Save users, notes and quiz attempts. Language is read from the DB.
- **Cache:** key is `sha256(resized JPEG bytes + language + style)`. Before calling Gemma, look it up
  (unless `force=True`). On a hit, insert a **new** `notes` row for the requesting user (copying the
  stored summary and quiz), send the stored summary immediately and log "cache hit". If the hit has
  `quiz_json` NULL, attach to the in-flight quiz task for that key if one exists, otherwise start one
  quiz call. Save the quiz JSON when the background task finishes.
- **Regenerate:** `🔁 Regenerate` runs the pipeline with `force=True` (no cache read). The new row is
  the newest for that key, so later lookups return it.
- Save the Telegram `file_id` and `file_unique_id` on every note (identifiers only, not the photo).
- Implements `db.py`. Add `tests/test_quiz_service.py` for scoring logic.
- **Human test:** restart the bot and confirm the user record persists. Send the **same photo twice**:
  the second reply should be near-instant. Open `snapstudy.db` and see rows in all three tables.

### F6 — Bangla / English toggle
- `/language` and an inline `🇧🇩 বাংলা / 🇬🇧 English` toggle. The choice is saved. It controls the AI output language **and** the bot's own UI text (`i18n.py`).
- Pressing the toggle under an existing summary regenerates it in the other language **without** asking the user to resend the photo. Decision: the handler re-downloads the image with `bot.get_file(file_id)` using the `file_id` stored on the note, then runs the normal pipeline for the new language (cache lookup first, so a photo already seen in that language is instant). If the re-download fails, tell the user to resend the photo. A plain `/language` with no summary on screen only changes the saved preference.
- **Human test:** switch to Bangla, send a photo, read the Bangla output. Switch back.

### F7 — Reliability and UX polish
- Timeouts, retry once on transient API errors, friendly messages for every failure listed in Section 10. Typing indicator (`send_chat_action`) while waiting. Reject files that are too large (check `MAX_DOWNLOAD_MB` before downloading) or are not images. Add the per-user guard from 4.4 rule 13 and the truncation retry from 6.2. Make sure `BadRequest` "not modified" and `RetryAfter` never surface to the user.
- **Human test:** disconnect the internet or set a wrong API key and see friendly messages. The bot keeps running.

### G1 — Group mode: reply to a photo and call the bot
- Works in groups and supergroups. Triggers and rules are in Section 4.5.
- A request is a message that **replies to a photo** (or an image document) and is a command or mention
  for this bot. A photo whose own caption mentions the bot also counts.
- Bot replies **to the original photo message**: "⏳ Reading…", then **one edit** with the compact
  summary and a single `📝 Quiz` button. No streaming in groups.
- If the replied message has no image, send the short hint from Section 10.
- Implements `handlers/group.py` and `utils/intent.py`
  (`parse_group_request(text, bot_username) -> GroupRequest(action, language)`).
  Add `tests/test_intent.py` covering: bare mention, mention + quiz, `/summary@Bot`, `bn` keyword,
  text addressed to a different bot, plain text with no mention.
  Reuse `StudyService` with `style="compact"`. Get the bot username once at startup (`get_me`).
- Group language for now: `en`, overridable with a keyword in the request.
- **Human test:** create a test group, add the bot, post a photo, then reply to it with
  `/summary@YourBot`, then `@YourBot`, then `@YourBot quiz`, then `@YourBot bn`.
  Tell the agent which forms the bot received. If plain mentions are not delivered, turn privacy
  mode off in BotFather and re-add the bot.

### G2 — Group quiz with native quiz polls
- `📝 Quiz` (button, `/quiz`, or the `quiz` keyword) starts a quiz. Use the quiz from the same
  background job and cache as private chats. If it is still generating, show "⏳ Preparing quiz…".
- Send **one quiz poll at a time** (`type="quiz"`, `correct_option_id`, `explanation`), for the
  first `GROUP_QUIZ_LENGTH` questions. Anonymous polls are fine: Telegram shows live results.
- A `➡️ Next` button lets anyone move on. Try attaching it to the poll with `reply_markup`; if
  Telegram rejects that, send it as a tiny separate message. Tell the human which one you used.
- Keep state in `chat_data` (note id, current index). Guard double-taps with an index check.
  One active quiz per chat. A new quiz replaces the old one. Stale buttons get the expired message.
- Truncate question, option and explanation text to the safe limits from Section 6.2.
- At the end send one short message: "🏁 Quiz done! Send another photo to keep studying."
- **Human test:** run a full 3-question quiz in the group, with two accounts answering if possible.
  Tap Next twice quickly and check that only one question is sent.

### G3 — Group polish
- **Per-chat language:** add a `chats` table (`chat_id`, `language`). `/lang@BotName en|bn` sets the
  group default. Only chat admins may change it.
- **Spam control:** per-chat cooldown (`GROUP_COOLDOWN_SECONDS`) and one in-flight request per chat. Reuse `utils/guards.py` from F7.
  Extra requests get one gentle message, never a stream of them.
- **Welcome:** when the bot is added to a group (`ChatMemberHandler`, `MY_CHAT_MEMBER`), send a
  3-line how-to: reply to a photo with `/summary@BotName`, or mention me with `quiz`.
- **Add-to-group button:** the private `/start` message gets `➕ Add me to a group`, a URL button to
  `https://t.me/<bot_username>?startgroup=true`.
- **Faster repeats:** also look up the cache by `file_unique_id + language + style` before
  downloading the image. The `file_unique_id` column already exists from F5, so fill it from F5 onward.
- Handle the error rows for groups in Section 10. Check that replies stay in the right topic in forum groups.
- **Human test:** call the bot twice in a row (the second should get the gentle message), change
  the language as an admin and as a non-admin, add the bot to a fresh group and see the welcome,
  and post the same photo twice to see the cache make the second reply near-instant.

### G4 — Stretch: group leaderboard
- Use non-anonymous polls (`is_anonymous=False`) and a `PollAnswerHandler`. Keep a dict
  `poll_id → (chat_id, question_index, correct_option)` and tally correct answers per user.
- After the last question post the top 3 with names and scores.
- **Human test:** two accounts answer differently and the final scores match.

### F8 — Stretch: short questions and flashcards (only if time remains)
- Add a `📚 Short questions` button that shows `short_questions`. Optional flashcards from `difficult_terms` (tap to reveal meaning).
- **Human test:** press the buttons and see sensible output.

### F9 — Stretch: weak topics (only if time remains)
- Track wrong answers by note topic and offer a `🎯 Practice weak topics` quiz. Add a `weak_topics` table at that point and not before.

### F10 — README, screenshots and submission prep
- Write `README.md` using the hackathon template:
  Project name, The problem, The solution, How it works (**model: Gemma 4 + link, provider, tech stack**), How to run, Screenshots/demo, What's not done yet (be honest), Credits. Add a short "Group mode" section: how to add the bot,
  the BotFather privacy setting, and the example commands.
- Confirm: no secrets in git history, `.env.example` exists, `.gitignore` is correct, the repo runs from a fresh clone.
- README must also contain: the "Who it is for and why it is different" answer from Section 1 in the
  "The problem" part, the corrected privacy wording (photos are not stored; summaries and quizzes are),
  a short "Why Telegram" line (free bot API, no app review, buttons and quiz polls built in), a
  Credits note about the AI coding agent and the pre-event planning files, a note that the bot only
  runs while the process runs, and a link to a 60-second demo video or GIF.
- Give the human a 2-minute demo script and a final submission checklist.
- **Human test:** clone the repo into a fresh folder and follow only the README.

---

## 10. Error handling (never crash, always reply)

| Situation | What the user sees | What is logged |
|---|---|---|
| Gemma timeout | "That took too long. Please try again, or send a clearer photo." | warning + latency |
| Gemma API error / bad key | "I'm having trouble reading notes right now. Try again in a minute." | error + status code (never the key) |
| Invalid JSON twice | "I couldn't understand that photo. Try a clearer, closer shot." | error + truncated raw text |
| `{"error": "unreadable"}` | "I couldn't read this. Make sure the text is clear and well lit." | info |
| Not an image / too big | "Please send a photo of your notes." | info |
| Telegram send failure | retry once, then log | error |
| DB failure | "Something went wrong. Please try again." | error + traceback |
| Stale quiz button | "This quiz expired. Send the note again." | info |
| Output cut off by the length cap | retry the call once with a 50% higher cap, otherwise the "couldn't understand" message | warning + token counts |
| Telegram "message is not modified" | nothing (ignored) | debug |
| Telegram `RetryAfter` on an edit | nothing; skip that edit and send the full text at the end | warning |
| User already has a photo in progress | "⏳ Still working on your last photo." (once) | info |
| Group: replied message has no image | "Reply to a photo of your notes and call me, e.g. /summary@BotName" | info |
| Group: cooldown or a request already running | one short "⏳ Still working on the last one" (at most once per request) | info |
| Group: no permission to send polls or messages | "I need permission to send polls here." (if even text fails, only log) | warning |

Add a global error handler on the `Application` that logs the exception and sends a generic friendly message.

---

## 11. Logging

Use Python `logging` with one config in `logging_setup.py`. Never `print()` in `app/`
(`scripts/` may print). Log: incoming update type, Gemma latency, errors with tracebacks,
warnings. **Never log API keys, the bot token or full image data.**

---

## 12. Coding standards

- Type hints everywhere. `async` for anything that does I/O. No blocking calls on the event loop:
  Pillow and `sqlite3` run through `asyncio.to_thread`.
- Small functions that do one thing. Descriptive names. Short docstrings.
- No dead code, no commented-out blocks, no TODOs without a reason.
- Pure logic (JSON extraction, scoring, message splitting) gets simple pytest tests. Do not test Telegram or the network.
- Prefer the simplest solution that meets the acceptance criteria.
- Do not add dependencies without saying why. Pin versions in `requirements.txt`.

---

## 13. Git rules

- Commit after each approved feature: `feat(F3): summary reply`, `fix(F4): stale button crash`.
- Never commit `.env`, `*.db`, model weights, or large images. Keep `samples/` small and self-made.
- If a secret is ever committed, tell the human immediately and say it must be rotated.

---

## 14. Definition of done

A user can open Telegram, send a photo of notes, receive a summary, take a 5-question quiz,
see the score, and switch between Bangla and English, with the summary starting to appear in about 10–15 seconds and the quiz ready within about
30 seconds, with no crashes.

**Second demo (group mode):** in a Telegram group, reply to a photo of notes with
`/summary@BotName`, get a compact summary, tap Quiz, and play a short poll quiz. Never flood the chat.

If this works, the project is successful. Everything else is a bonus. The bot must be running
whenever judges may try it, and the README links a 60-second demo video as a backup.

---

## 15. Final reminder to the agent

**One feature. Test instructions. Stop. Wait.**
Do not build ahead. Do not refactor unasked. Do not add features that are not listed.
Ask when unsure.
