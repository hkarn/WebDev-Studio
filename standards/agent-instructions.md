# Agent instructions in an app repo

- **Follows:** moneyworks, vocabulary-training
- **Checked:** 2026-11-06 (moneyworks `f31e49b`, vocabulary-training `95f3d8a`)
- **Reference files:** `.github/copilot-instructions.md`, `CLAUDE.md`, `CONTRIBUTING.md`,
  `.devcontainer/compose.yaml` in either app

## Files

- **`.github/copilot-instructions.md` is the shared reference** for every coding agent: project,
  environment and commands, code map, rules that must not regress, workflow. Copilot reads it
  directly.
- **`CLAUDE.md` imports it** (`@.github/copilot-instructions.md`) and adds only what is specific to
  Claude Code: config and memory volumes, the `@claude` issue workflow, host quirks.
- **Name the standards it follows**, with links, near the top of the shared file:
  `Follows hkarn/WebDev-Studio standards: dev-environment, ci, … Services, models,
  configuration, pricing and business decisions: hkarn/tech-research FINDINGS.md.` Agents read
  those with `gh`, so the setup doesn't need explaining again.

## Workflow rules the apps share

- Decisions and planned work are GitHub issues; open questions carry the `decision` label. Don't
  build on an open one. Record the outcome in the issue before closing it. No decision logs or dated
  verification reports in the repo.
- While iterating run only typecheck and lint; run the full set before a commit or PR. Report only
  checks that actually ran.
- Branch from `main`, open the PR as a draft, mark it ready when done. Push or merge to `main` only
  with the owner's go-ahead (it publishes the image).
- Never apply `good first issue` or `help wanted`; the owner sets those.
- `notes/` and `CLAUDE.local.md` are gitignored, for scratch and session notes.
- The repo files are the authority for versions and commands: `package.json`, the lockfile,
  Docker/Compose files, migrations and `ci.yml`. Update the shared instructions with any change to
  them.

## Shared memory between host and dev container

Claude Code in the dev container and Claude Code on the host can share one memory folder for the
same app:

- `.devcontainer/compose.yaml` bind-mounts
  `${CLAUDE_MEMORY_DIR:-${HOME:-${USERPROFILE}}/.claude-memory/<app>}` at
  `/root/.claude/projects/-<workspace-folder>/memory` (`-app` for `/app`, `-workspace` for
  `/workspace`).
- On a Windows host, replace `.claude\projects\<slug>\memory` with a junction to the same folder
  (one-time step in the app README). Remove or retarget a junction with `cmd /c rmdir "<link>"`;
  in PowerShell 5.1 `Remove-Item -Recurse` on a junction can delete the target's contents.
- The memory is for that app's own sessions. Findings from tech-research and standards from here
  are linked by path, not copied into memory.
