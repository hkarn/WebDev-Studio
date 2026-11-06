# Starting a new app

- **Follows:** the checklist for any new app that adopts these standards
- **Checked:** 2026-11-06
- **Copy from:** [GothenburgOffice/vocabulary-training](https://github.com/GothenburgOffice/vocabulary-training)
  (app at the repo root; the simplest reference)

## Before code

1. Decide with the owner: name, public or private, and owner (see "Where an app lives" in
   [apps/INDEX.md](../apps/INDEX.md)). Check model or service choices in
   [tech-research FINDINGS.md](https://github.com/hkarn/tech-research/blob/main/FINDINGS.md).
2. Pick the next free host port (see [dev-environment.md](dev-environment.md)).

## Repository setup

3. **Stack** per [nextjs-postgres.md](nextjs-postgres.md). Bootstrap without host Node:
   `docker run --rm -it -v "$PWD":/app -w /app node:22.x-trixie-slim npx create-next-app@<exact> .`
   then pin every dependency exactly ([dependencies.md](dependencies.md)).
4. **Dev environment** per [dev-environment.md](dev-environment.md): `Dockerfile` with all targets,
   the three Compose files, `.devcontainer/`, `.env.example`, `<app>.code-workspace`.
5. **Repo hygiene:** `.editorconfig`, `.gitattributes` (LF), `.prettierrc.json`,
   `.git-blame-ignore-revs`, `.gitignore` with `.env*`, `notes/`, `CLAUDE.local.md`.
6. **Security** per [security.md](security.md): headers in `next.config.ts`, self-hosted fonts,
   `/api/health`.
7. **CI** per [ci.md](ci.md), and Dependabot per [dependencies.md](dependencies.md). Protect `main`
   with `unit` and `containers` as required checks.
8. **Agent files** per [agent-instructions.md](agent-instructions.md), naming the standards it
   follows.
9. **README** with the one-time setup (copy `.env.example`, open in the dev container, the memory
   junction on Windows), `LICENSE`, `CONTRIBUTING.md`, `SECURITY.md` for a public repo.

## Done when

The dev container opens and serves the app, `docker compose -f compose.yaml up` runs the production
build, CI is green on a draft PR, and the app has a row in [apps/INDEX.md](../apps/INDEX.md).
