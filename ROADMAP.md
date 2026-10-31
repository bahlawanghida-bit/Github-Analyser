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

## Stages

### Stage 1: Analysis engine (Python)
The "brain" that every other part uses. It has no website yet and runs in the terminal.
- Clean up the code into functions and modules, with no `input()` inside the logic.
- Fetch all commits (pagination), not only the first 100 per repo.
- Strength and gap analysis: language depth, consistency and streaks, project variety, use of tests, CI and READMEs.
- Suggestions generated from the gaps.
- Automated tests for the analysis.
- A proper `README.md`.

**You learn:** Python functions, modules, classes, pandas, `pytest`.
**Done when:** one command prints a full strengths, gaps and suggestions report for any username, and the tests pass.

### Stage 2: Backend, accounts and roles
Turns the engine into a server that the website and the chatbot can talk to.
- A web API, for example `GET /profiles/{username}`.
- A database for users, roles, cached analyses and HR shortlists.
- Login: GitHub sign-in for programmers, email and password for HR.
- Roles and permissions: what each actor is allowed to do.
- Admin endpoints: manage users, handle removal requests, view stats.

**You learn:** FastAPI, HTTP and REST, SQL (SQLite, later PostgreSQL), OAuth, password hashing, authorization.
**Done when:** each of the 3 actors can sign in and use their features through the API.

### Stage 3: Website
One website with a separate dashboard for each actor.
- Programmer dashboard: charts, strengths, gaps, suggestions, privacy settings.
- HR dashboard: search, candidate summary, shortlist, compare.
- Admin dashboard: users, requests, statistics.

**You learn:** HTML, CSS, JavaScript, then TypeScript and React; charts; calling an API from the browser.
**Done when:** everything from Stage 2 can be done by clicking in the website.

### Stage 4: AI features
- **Job matching (HR):** paste a job description, the AI pulls out the required skills, and the tool compares them to the profile's evidence.
- **Chatbot (Programmer and HR):** answers questions using the real analysis data through tool use, not guessing.
- Admin can see AI usage and cost.

**You learn:** Claude API, structured output, tool use, prompt design, handling cost and limits.
**Done when:** HR gets a match report with evidence, and the chatbot answers profile questions correctly.

### Stage 5: Launch
- Put the website online.
- GitHub Actions run the tests on every push.
- Docker so it runs the same everywhere.
- Privacy page, a polished README with screenshots and a demo link for the CV.

**You learn:** YAML, Docker, deployment, CI/CD.
**Done when:** anyone can open the link and use it.

---

## Status
- [x] Fetch repos, languages and commits from the GitHub API
- [x] Language %, most active repo, commit hours and days, personality tags
- [x] Bug fixes: wrong exception name, `None` commit dates, empty repos
- [ ] **Stage 1: Analysis engine** (current: refactor into functions)
- [ ] Stage 2: Backend, accounts and roles
- [ ] Stage 3: Website
- [ ] Stage 4: AI features
- [ ] Stage 5: Launch
