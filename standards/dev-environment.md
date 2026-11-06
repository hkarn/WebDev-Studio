# Dev environment: Docker-first

- **Follows:** moneyworks, vocabulary-training
- **Checked:** 2026-11-06 (moneyworks `f31e49b`, vocabulary-training `95f3d8a`)
- **Reference files:** `compose.yaml`, `compose.dev.yaml`, `compose.images.yaml`, `Dockerfile`,
  `.devcontainer/devcontainer.json` and `.devcontainer/compose.yaml`, `.env.example` in either app.
  vocabulary-training is the simpler one to copy (app at the repo root).

## Principle

The host needs Docker and nothing else: no Node, no npm, no local PostgreSQL. Every command runs in
the dev container, or from the host through
`docker compose -f compose.yaml -f compose.dev.yaml exec app <command>`. Versions are pinned by the
images, so dev, CI and production run the same Node and PostgreSQL.

## Compose files

| File | Role |
|---|---|
| `compose.yaml` | Base stack: `db`, a one-shot `migrate`, and `app` built from source with the `production` target |
| `compose.dev.yaml` | Dev override: `development` target, source bind-mounted, `node_modules` and `.next` in named volumes, all dev-only settings |
| `compose.images.yaml` | The published GHCR image plus PostgreSQL, no source |
| `.devcontainer/compose.yaml` | Dev-container additions only: `devcontainer` target, agent and `gh` sign-in volumes, shared agent memory |

- **All dev-only settings live in `compose.dev.yaml`,** never only in the dev container, so every
  dev stack ignores production values in `.env`. Dev reads `DEV_*` variables for secrets and
  origins (`DEV_APP_ORIGIN`, `DEV_APP_ORIGIN_ALIASES`, `DEV_*` keys).
- **The dev command reinstalls only when the lockfile changed, and stops if the install fails:**

  ```sh
  (cmp -s package-lock.json node_modules/.installed-lock ||
   (npm ci && cp package-lock.json node_modules/.installed-lock)) && exec npm run dev
  ```

- **No `NODE_ENV` in dev:** `next dev` and `next build` set their own; a container-wide value
  breaks `npm run build`.
- **`WATCHPACK_POLLING=true` by default**, because file events don't cross from a Windows drive
  into the container; that needs webpack (`next dev --webpack`). Set it to `false` in `.env` on
  Linux, macOS or a WSL2 checkout.
- Never `docker compose down -v` on a stack with real data.

## Dockerfile

One multi-stage file: `dependencies` → `development`, `devcontainer` (development plus git, `gh`,
curl), `builder` → `production` (non-root, no source), and `migration`.

## Dev container

- `dockerComposeFile`: `["../compose.yaml", "../compose.dev.yaml", "compose.yaml"]`,
  `service: app`, `runServices: ["db", "migrate", "app"]`.
- `overrideCommand: false`, so the dev server starts itself with the reinstall check above;
  `shutdownAction: stopCompose`.
- Extensions: `anthropic.claude-code`, `dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`,
  `github.vscode-github-actions` (plus `Prisma.prisma` with Prisma). Format on save with Prettier.
- Volumes for Claude Code's config (`CLAUDE_CONFIG_DIR=/root/.claude`) and the `gh` sign-in, so
  both survive rebuilds, and the shared agent memory mount (see
  [agent-instructions.md](agent-instructions.md)).
- Each app keeps a `<app>.code-workspace`; never delete it (VS Code closes with it).

## Environment variables and ports

| Name | Meaning |
|---|---|
| `POSTGRES_PASSWORD` | Required in every stack, dev included; `.env` is gitignored, `.env.example` documents it |
| `APP_PORT` | Host port. Unique and uncommon per app: moneyworks 3410, vocabulary-training 3420. Pick the next free one (3430, …) for a new app |
| `APP_ORIGIN`, `APP_ORIGIN_ALIASES` | Public origin and accepted aliases; default derived from `APP_PORT` |
| `ALLOW_REGISTRATION` | Open sign-up (dev seeds it open; a real site starts closed) |
| `DEV_*` | Dev-only replacements for secrets and origins |
| `<APP>_IMAGE` | Override for the published image in `compose.images.yaml` |

Service names: `db`, `migrate`, `app`. `next.config.ts` sets `allowedDevOrigins` for any alias the
dev stack uses (for example `127.0.0.1`), or hot reload breaks on that origin.

## Why

Background from the old project (2026-08 to 2026-10): the owner prefers no host Node/npm,
"works on my machine" problems disappear when images pin versions, and even `create-next-app`
can run in a throwaway Node container. The two apps converged on this layout on 2026-11-01; see
[the comparison](../history/2026-11-01-ci-and-environment-alignment.md).
