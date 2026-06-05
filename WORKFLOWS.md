# How I use coding agents day-to-day

Not specific to this take-home — my usual setup.

**Tools:** **Cursor** (Plan + Agent) for code and terminal; **Claude (web)** for research and architecture before I open the repo; **terminal** for quick sanity checks myself. I also use agents for routine morning stuff — email summaries, pages I check daily.

**Default pattern:** (1) Define input and output in one sentence. (2) Pick agent + tools if it’s agentic. (3) Mind map; split MVP vs nice-to-have — ship MVP first, styling later. (4) Ask the agent to run tests after each chunk so new code doesn’t break old paths.

**Delegate vs keep:** Agent drives scaffolding, parsers, refactors, and executing a plan I already wrote in detail. I keep the contract, “is this overkill?”, secrets/deploys, and stepping in when logs or tests are wrong. I spend the most time **testing and tightening** — making sure it works, not just looks done.

**Custom skills (outside this repo):** **Hackathon assistant** — find an angle, scaffold to deployment so I focus on the idea. **Screen recording skill** — auto walkthrough for submissions. This Qosmic repo is my first **in-repo** skills folder (`skills/crawl.md`, etc.) the same way.

**Portfolio (in progress):** site agent that chats about my work and researches visitors; optional skills-assessment flow for recruiters.

**Before I call anything done:** run deterministic checks, spot-read one real output, test a second URL if it claims to generalize. I don’t commit agent output without machine checks + a quick human skim.
