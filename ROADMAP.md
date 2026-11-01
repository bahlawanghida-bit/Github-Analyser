# GitHub Judger: Plan

## Goal
A public website that analyzes GitHub profiles. It shows programmers their strengths, their gaps and what to improve; helps HR see whether a candidate fits a job; and has a chatbot that answers questions about a profile.

The project is also a learning path: each stage teaches new languages and skills.

## Design principles
- Only public GitHub data is analyzed.
- Programmers control their own profile: they can hide it or ask for it to be removed.
- GitHub activity is not the whole story, because private and work code is invisible. The tool shows evidence ("0 public repos using SQL"), not verdicts ("bad at SQL").
- Every score explains how it was calculated.

---

## Actors

### 1. Programmer (signs in with their GitHub account)
- See their profile analysis: languages, activity, project types.
- See **strengths**, **gaps** and **concrete suggestions** for improving.
- Track progress over time ("you added tests to 3 repos this month").
- Ask the chatbot things like "What should I learn next to become a backend developer?"
- Choose whether HR can see their profile, or hide it.

### 2. HR / Recruiter (signs in with email and password)
- Look up a programmer by GitHub username (only visible profiles).
- Read a short, plain-language summary of the candidate.
- Paste a **job description** and get a skill match, with evidence for each skill.
- Ask the chatbot things like "Has this person worked with databases?"
- Save candidates to a shortlist and compare them side by side.

### 3. Admin (us)
- Manage accounts: approve HR accounts, change roles, ban misuse.
- Handle programmer removal requests.
- See usage statistics: number of analyses, GitHub API rate limits, AI usage cost.
- Adjust the scoring rules (for example, what counts as "experienced" in a language).
- See errors and logs.

---

## Tech stack
| Part | Tech | You learn |
|---|---|---|
| Data + analysis | Python: `requests`, `pandas`, `python-dotenv` | Python, pandas DataFrames |
| API server | Node.js + Express | JavaScript, async/await, HTTP and REST |
| Frontend | React (Vite) + `recharts` | JSX, components, state, hooks, charts |
| AI | Claude API | structured output, prompts, chatbots |
| Python to Node bridge | subprocess: Express runs `python run_analysis.py <user>` and reads JSON from stdout (could switch to Flask later) | processes, stdout/stderr, exit codes |

## Stages
Each step: the concept is explained first, then the code is written in small pieces and walked through line by line.

### Stage 1: Finish the Python analyzer (pandas)
- Refactor `analyze.py` into functions, with no `input()` inside the logic.
- Save the results as JSON (languages %, most active repo, hour and day patterns, tags) so other programs can read them.

**You learn:** Python functions and modules, pandas, JSON.

### Stage 2: Express API (Node.js)
- `GET /api/analyze/:username` runs the Python layer and returns the results JSON.
- In-memory caching and error handling (bad username, rate limit, network).

**You learn:** Node.js, npm, JavaScript basics, Express routes, async/await, calling Python from Node.

### Stage 3: React dashboard
- React + Vite setup, wired to the API.
- Dashboard: language chart, commit-hour and weekday charts, personality tags.

**You learn:** React components, props, state, `useEffect`, fetching data, `recharts`.

### Stage 4: First deploy
- Put the app online (Render / Railway / Vercel / Netlify; decide here).

**You learn:** environment variables in production, hosting, build steps.

### Stage 5: Recruiter / ML extension (HR features)
- Skill-profile vector: language %, frameworks from `package.json` / `requirements.txt`, repo count, activity, fork ratio.
- Role scoring: a transparent weighted score over Frontend / Backend / Full-stack / Mobile / Data-ML / DevOps. This is not a trained model.
- Job description parser: the Claude API returns `{requiredSkills, niceToHave, seniority}`.
- Fit engine: cosine similarity, giving a fit % and matched and missing skills.
- `POST /api/fit-check`, a recruiter UI and a chatbot for follow-up questions.
- Stretch: compare 2 or 3 candidates; train a small model on hand-labelled profiles and compare it to the scoring.

**You learn:** feature engineering, vectors and cosine similarity, the Claude API, prompt design.

### Stage 6: Accounts, roles and Admin
- Login, the 3 roles and their permissions, a database for users and shortlists.
- Admin: manage accounts, monitor GitHub and Claude API usage, clear the cache.

**You learn:** SQL, authentication, password hashing, authorization. (The auth method and database are still open decisions.)

### Stage 7: Quality and launch
- Tests (`pytest`, then a JS test runner), GitHub Actions CI, Docker, a polished README with a demo link.

**You learn:** testing, YAML, Docker, CI/CD.

---

## Status
- [x] Fetch repos, languages and commits (paginated, rate-limit aware) from the GitHub API
- [x] Language %, most active repo, commit hours and days, personality tags
- [x] Bug fixes: wrong exception name, `None` commit dates, empty repos
- [x] Stage 1: Python analyzer (functions, results saved to `data/<user>_results.json`)
- [x] Stage 2: Express API (`GET /api/analyze/:username`, 1-hour in-memory cache, shared in-flight requests, 404/503/504 errors, timeout)
- [ ] **Stage 3: React dashboard** (D5 done: Vite + React client in `client/`, search form, summary, API proxy; next D6: recharts charts)
- [ ] Stage 4: First deploy
- [ ] Stage 5: Recruiter / ML extension
- [ ] Stage 6: Accounts, roles and Admin
- [ ] Stage 7: Quality and launch
