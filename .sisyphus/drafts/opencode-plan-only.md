# Draft: Enable Plan Mode Only (Oh My OpenCode / OpenCode)

## Requirements (confirmed)
- User wants to "only enable plan mode" when launching OpenCode via `opencode`.
 - User choice: only switch to Plan for the current session (no config change).

## Technical Decisions
- Decision: do a per-session switch to the Plan primary agent using the built-in agent switcher (Tab).

## Research Findings
- Oh My OpenCode config locations (precedence): `.opencode/oh-my-opencode.json`, then `~/.config/opencode/oh-my-opencode.json`.
- Oh My OpenCode: `planner-sisyphus` is the Plan agent (renamed); other agents (librarian/explore/oracle) can be disabled.
- OpenCode: Plan is a restricted primary agent; can be switched via `Tab`.
- OpenCode config supports agent-level tool gating, and agents can be disabled.

## Open Questions
- If they later want "Plan-only by default", decide whether to disable the Build agent via `opencode.json`.

## Scope Boundaries
- INCLUDE: session switching + config options to default to Plan / restrict tools.
- EXCLUDE: any code changes to the OpenCode project itself.
