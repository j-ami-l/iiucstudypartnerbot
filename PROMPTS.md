# PROMPTS.md — copy and paste these to your coding agent

Put `AGENT.md` and this file in the root of an empty project folder first, then open the folder in
your agent (Claude Code, Cursor, Copilot, etc.). `AGENT.md` is the source of truth. If this file and
`AGENT.md` ever disagree, `AGENT.md` wins.

---

## Before you start (do these yourself, before and at kickoff)

Planning and setup before kickoff is fine. The application code must be written during the event.

1. Create a bot with **@BotFather** on Telegram and copy the token.
2. Decide how you will access Gemma 4 (check the MLH Gemma links: https://mlh.link/gemma).
   Note the **API key, base URL and model name**. Check that the provider accepts images and,
   if possible, streaming.
3. Take 3–5 photos and save them in `samples/`: one handwritten note, one lecture slide, one
   blurry/bad photo, and if you can, one Bangla or mixed Bangla/English page (and one with Arabic text).
   Use only your own notes. No other students' personal data.
4. Create a new public GitHub repo for the hackathon.
5. Put your keys in `.env` (never commit it).

---

## PROMPT 1 — First prompt (setup + Gemma test only)

```
Read AGENT.md completely before doing anything. It is the source of truth for this project.

Rules for how we work together:
- Work ONE feature at a time, exactly as AGENT.md Section 0 says.
- Do NOT build ahead of the feature I approve.
- After each feature, give me exact test steps and STOP.

Your task now: do ONLY F0 (project skeleton) and F1 (standalone Gemma smoke test).

Details:
- F0: create the folder structure from AGENT.md Section 4.1 (everything under app/, each folder with
  an __init__.py), requirements.txt (pinned), .gitignore, .env.example (all variables from Section 5,
  including the per-language token caps), app/config.py, app/logging_setup.py. Do not create files for
  later features yet except empty packages.
- F1: build app/ai/gemma_client.py, app/ai/json_utils.py, app/schemas.py,
  app/prompts/summary_prompt.md, app/prompts/quiz_prompt.md and scripts/test_gemma.py so I can run,
  from the project root:
      python -m scripts.test_gemma samples/note1.jpg en
      python -m scripts.test_gemma samples/note1.jpg bn
  It must run the summary call and the quiz call IN PARALLEL (see AGENT.md sections 4.3, 4.4, 6)
  and print the summary text, the validated quiz JSON, time to first token, each call's time,
  total wall-clock time, and the token counts and finish reason of each call when the provider
  returns them. Warn loudly if any call was cut off by the length cap. Support a --max-side flag so
  I can compare image sizes.
- My Gemma provider details are: [PASTE: provider name, base URL, model name].
  My API key is in .env as GEMMA_API_KEY. If anything about the provider is unclear
  (image format, endpoint shape, streaming), ask me one short question and stop. Do not guess.

When done, give me:
1. Files created
2. Exact commands to set up and run the test
3. What a good result looks like and what failures to look for
Then stop and wait for me.
```

**What you do next:** run the test script on all your photos in `en` and `bn`. Check:
- Is the JSON valid and complete (5 MCQs, 4 options each)?
- Is the summary actually correct for your note?
- Does Bangla read naturally? Does the Bangla quiz get **cut off**? (Bangla uses many more tokens.)
- How many seconds until the first summary text? Until the quiz is ready? Compare
  `--max-side 768 / 1024 / 1280`.
- What token counts did each call use? Set the caps in `.env` to about 30% above the measured values.

If something is bad (slow, wrong text, broken Bangla, cut-off JSON), fix it **now** with Prompt 3 or
Prompt 4 below. Only continue once F1 is solid.

---

## PROMPT 2 — Approve and continue (reuse for every feature)

```
F[N] works. Commit it with the message "feat(F[N]): [short name]".
Now start F[N+1] only, following AGENT.md Section 0:
announce, short plan, implement, self-check, then give me exact test steps, the 3-line
"how it works" explanation, and STOP.
```

Examples:
- After F1 works → `F1 works. Commit it ... Now start F2 only ...`
- After F4 works → `F4 works. Commit it ... Now start F5 only ...`

After **F3** works, also send Prompt 6 (README skeleton) once, and take a screenshot.

---

## Feature order and group mode setup

Order: F0 → F7, then G1 → G3 (group mode), then stretch (G4, F8, F9), and F10 last.
When you approve a feature use its name, e.g. `F7 works. Commit it ... Now start G1 only ...`.

All features stay in scope. If time runs short, drop from the bottom in this order:
**G4 → F9 → F8 → G3 → G2 → G1**. F0 → F7 plus F10 is the minimum you must submit.

**Before you test groups (do this yourself, 5 minutes):**
1. Make a new Telegram group with one or two friends (or a second account) and add your bot.
2. In @BotFather: `/mybots` → your bot → Bot Settings → Group Privacy. Try with it **on**
   first. If plain `@YourBot` mentions are not delivered, turn it **off**, then remove and
   re-add the bot to the group. (Making the bot an admin also works.)
3. Post a sample note photo in the group so you can reply to it.

Group quiz notes: Telegram quiz polls have length limits, so questions are kept short. Groups play
the first 3 of the 5 questions, set by `GROUP_QUIZ_LENGTH` in `.env`.

---

## PROMPT 3 — Report a bug (reuse anytime)

```
F[N] has a problem. Do not start any new feature.

What I did: [exact steps]
What I expected: [...]
What happened: [paste the error or describe it]

Find the root cause, fix it with the smallest change, tell me what was wrong in 1–2 sentences,
and give me the exact steps to re-test. Then stop.
```

---

## PROMPT 4 — Improve Gemma output quality (use after F1 if results are weak)

```
The Gemma output in F1 has this problem: [e.g. summary misses key points / Bangla is
unnatural / MCQs are too easy / JSON sometimes has extra text / quiz is cut off in Bangla].

Only edit app/prompts/summary_prompt.md, app/prompts/quiz_prompt.md and, if needed,
app/ai/json_utils.py and the token caps in .env.example. Do not touch other files.
Make the change specific to this problem, then give me the same test commands to
re-run on my sample images. Then stop.
```

---

## PROMPT 5 — Final prep (when time is short, about 45 minutes before the deadline)

```
We are close to the deadline. Skip all remaining unfinished stretch features.
Do F10 now:
1. Finish README.md using the hackathon template in AGENT.md. It must include: Gemma 4 model name,
   provider and a link; the "who it is for and why it is different" answer in "The problem"; the
   correct privacy wording (photos are not stored, summaries and quizzes are); a short "Why Telegram"
   line; a Credits note that an AI coding agent was used and that AGENT.md and PROMPTS.md were
   prepared before the event; a note that the bot only runs while the process runs; a link to the
   demo video/GIF; an honest "What's not done yet"; and a short "Group mode" section with the
   BotFather privacy setting and example commands (only if G1 works).
2. Check that no secrets are in the repo or git history, .env.example exists, and
   .gitignore is correct (including *.db and *.db-*).
3. Verify that a fresh clone can run by following only the README. List any gaps.
4. Give me a 2-minute demo script and the final submission checklist.
Then stop.
```

---

## PROMPT 6 — README skeleton (send once, right after F3 works)

```
Do not start a new feature. Create a README.md skeleton using the hackathon template in AGENT.md
with everything that is already true (problem, solution, model and provider, tech stack, how to run
what exists today). Leave clearly marked placeholders for screenshots and for features not built yet.
Commit it as "docs: README skeleton". Then stop.
```

---

## PROMPT 7 — Explain this code so I can answer judges (reuse anytime)

```
Do not change any code. Explain [file or feature] to me as if I must answer a judge's questions:
what it does, why it is built this way, what would break if I removed it, and the 3 hardest
questions a judge could ask about it with short answers. Then stop.
```

---

## PROMPT 8 — Resume after the agent lost context (reuse anytime)

```
Read AGENT.md completely and run `git log --oneline`. Tell me which features (F0–F10, G1–G4) are
already done, which one is in progress, and what you think is next. Do not write any code. Then stop
and wait for my confirmation.
```

---

## Suggested time budget (assume about 6 hours of building)

If the announced event window is shorter, cut from the bottom of the table.

| Time | Work | Checkpoint |
|---|---|---|
| 0:00–0:30 | Plan, setup, BotFather, Gemma access, sample photos | Provider details known |
| 0:30–1:15 | F0 + F1 (Gemma test), **fix quality, timing and token caps here** | Valid `en` and `bn` quiz JSON |
| 1:15–2:15 | F2 + F3 (photo in, streamed summary), then Prompt 6 (README skeleton) | Summary visible in Telegram |
| 2:15–3:15 | F4 (quiz flow) | **Primary demo works end to end** |
| 3:15–3:45 | F5 (database, cache, Regenerate) | Repeat photo is instant |
| 3:45–4:15 | F6 (language toggle) | Toggle works without resending |
| 4:15–4:45 | F7 (error handling, guards, polish) | Bad key / no internet handled |
| 4:45–5:30 | G1 + G2 (group reply and quiz polls) | Second demo works |
| 5:30–5:45 | G3 essentials (cooldown, welcome), only if time remains | |
| Final 45 min | **F10 always**: README, screenshots, demo video, submit 15 min early | |

**Hard rule:** if you are not at the "Primary demo works end to end" checkpoint by 3:30, stop adding
features, fix what is broken, and jump to F10 when the final 45 minutes begin.
F8, F9 and G4 are stretch work for leftover time only.

Commit every 30–45 minutes. Submit at least 15 minutes before the deadline.
