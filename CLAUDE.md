# WebDev Studio: Claude specifics

The entry point for every agent is `AGENTS.md`. It is imported below and applies in full; this file
only adds what is specific to Claude.

@AGENTS.md

## Claude specifics

- **Reading app repos.** Use `gh` (`gh api repos/<owner>/<repo>/contents/<path>`, or a shallow
  `gh repo clone` into the scratchpad). If a local clone exists, pull before trusting it.
- **Checking a standard against an app.** Read the app's real files (`.devcontainer/`, Compose
  files, `Dockerfile`, `.github/workflows/`, `package.json`); don't rely on the standard's own
  description. Record the commit you checked.
- **Documenting the user's setup.** Turn what you see on their machine into the generic pattern
  before writing it here (`AGENTS.md` rule 7). Paths, host names and anything from Claude's memory
  about the user stay out.
- **Subagents** only when the user asks. Give each one the exact standard and repo it needs.
- **Memory.** Standards belong in this repository, app state in the app repo, not in Claude's
  memory. The shared `~/.claude-memory/<app>` folder (see
  [standards/agent-instructions.md](standards/agent-instructions.md)) is for one app's host and
  dev-container sessions, not for this repo.
- **Cloud sessions** commit to `main` here too (`git checkout -B main origin/main` before the first
  commit); don't push a session branch or open a draft PR because the environment does that by
  default.
- **Pull requests.** Assign every pull request you open to `hkarn`, so it shows up in the owner's
  GitHub views: `gh pr create --assignee hkarn`, or `gh pr edit <N> --add-assignee hkarn` for one
  opened another way (a GitHub MCP tool, or a draft the environment opened).
