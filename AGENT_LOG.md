# Agent log

| Part | Time (min) | Notes |
|------|------------|-------|
| Scaffold + harness skills | ~55 | AGENTS.md, crawl/reason/write/eval skills, `.cursor/rules/qosmic.mdc`, eval code |
| gingerpeople audit | ~50 | Crawl (bot limits on parallel fetch); calibrated offline against human sample — agent never read `target_report.md` |
| eval build + run | ~90 | eval.py, grounded.py, cross_audit.py; PSI 429 handled gracefully |
| zenrojas audit | ~40 | discover_store.py for dynamic URLs; sequential refresh for statuses |
| Docs | ~20 | EVAL_LOOP, WORKFLOWS, AGENT_LOG |
| **Total** | **~4h 15m** | Bit over 4h target |

## How I used Claude vs Cursor on this project

**Claude (web)** — ideation and learning, not coding in the repo.

I started on Claude in the browser before touching Cursor much. I used it to understand what the audit metrics actually mean in practice — pillars, decision rules, confidence scores, what a real CRO audit is trying to measure. I asked it to walk me through those concepts so I wasn’t just copying field names without understanding them.

The bigger question I took to Claude was: how do you get **reliable, verifiable** checks instead of asking an LLM “is this good?” and hoping it doesn’t hallucinate Pass rows on SSL or page speed? That led me to grounded scripts (`eval/grounded.py`), looking at what existing tools already automate (PageSpeed API, HTTP checks), and sketching the harness shape — input contract, phases, where human-only calibration (`target_report.md`) should *not* leak into agent runs. I brought my own architecture ideas into that conversation and used Claude to stress-test them, not to write the final code.

**Cursor (coding agent)** — implementation.

Once the shape was clear, I used Cursor Agent to build module by module. I described what each piece had to do (crawl seven surfaces, parse reports, cross-audit two stores, render HTML from markdown) and let it implement. I used **Plan mode** first on bigger chunks, then **Agent mode** to execute. When the plan was detailed enough, I’d let it run almost on autopilot for that slice.

For the actual storefront audits (gingerpeople, zenrojas), the prompt was basically: read `AGENTS.md` and `skills/`, run the full pipeline for one URL. Same harness, different URL — no store-specific shortcuts in the skills.

## Prompts (representative)

**Claude (web), early:**

- What do the audit fields and pillars actually measure? What would a recruiter care about vs what’s just formatting?
- How do I verify technical checks (PSI, SSL, robots) without the model making up Pass/Fail?
- What tools already exist for storefront checks? How would you structure a harness: one URL in, report out, eval on top?

**Cursor (agent), in repo:**

- "Read AGENTS.md and skills/. Run a complete Qosmic audit for https://gingerpeople.com"
- Same for zenrojas with unchanged skills.
- "Implement `eval/grounded.py` with parallel PSI; never crash on 429 — Warn only."
- "Run eval on both reports, fix flags, re-run until structural score is clean."

## Agent vs human — who drove what

| Task | Driver |
|------|--------|
| Overall harness shape, eval philosophy, EVAL_LOOP story | Me (with Claude for early thinking) |
| `AGENTS.md`, skills, `qosmic.mdc`, Python modules | Cursor agent — I specified behavior, it wrote code |
| Detailed plans for a feature slice | Me — then agent executed in autopilot when the plan was complete |
| Running tests, reading logs, self-improve loops | Agent — I asked it to run checks and iterate on failures |
| When logs weren’t captured or tests missed something | **Me** — had to point at the gap and tell the agent what to fix |
| New features mid-build | **Me** — decided *whether* to add them and if they were requirement vs overkill |
| gingerpeople / zenrojas report prose | Agent from artifacts; I reviewed for eval flags |
| Final submission polish, stale judge cleanup, docs | Me |

**Where I took the wheel:** (1) fixing runs where logging or test output wasn’t right, (2) saying no to scope that felt like overkill, (3) last pass before submit.

**Where the agent drove:** boilerplate, parsers, crawl helpers, HTML template wiring, re-running eval until flags cleared — especially when I gave a full plan upfront.

## Friction

- gingerpeople.com rate-limits parallel crawls; sequential `refresh_manifest.py` + browser User-Agent required.
- PSI public API returned 429 without a key; reports use honest Warn rows; `grounded.py` does not crash.
- Some self-improvement runs didn’t log cleanly the first time — I had to step in and re-run with clearer instructions.
