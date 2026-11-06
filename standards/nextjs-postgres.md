# Stack: Next.js + PostgreSQL

- **Follows:** moneyworks, vocabulary-training
- **Checked:** 2026-11-06 (moneyworks `f31e49b`, vocabulary-training `95f3d8a`)
- **Reference files:** each app's `package.json`, `Dockerfile`, `next.config.ts`,
  `.github/copilot-instructions.md`

## The stack

- **Next.js App Router, React, strict TypeScript.** Server-only code is marked
  `import "server-only"` and kept apart from client components.
- **PostgreSQL 18.** The official `postgres:18.x` image, or `pgvector/pgvector:<ver>-pg18-trixie`
  when the app needs vectors. Volume mounted at `/var/lib/postgresql` (the Postgres 18 layout). A
  dedicated app database user in every stack, never the `postgres` superuser.
- **Data access is the app's choice.** Prisma (moneyworks) and plain `pg` with append-only SQL
  migrations (vocabulary-training) are both fine. Either way, migrations are committed and run by a
  one-shot `migrate` service (see [dev-environment.md](dev-environment.md)); never edit an applied
  migration.
- **Auth is the app's choice** (better-auth, custom). Not standardized.
- **Node 22** is the floor and the runtime everywhere (`engines`, Dockerfile, CI). Don't use APIs
  newer than Node 22. Raise the floor in `package.json`, `Dockerfile`, `@types/node`, CI and the
  Dependabot holds together.
- **Debian images** (`node:22.x-trixie-slim`), so system packages come from `apt-get`.
- **Health endpoint** at `/api/health`, returning 503 when the database is down and not cached.

## Formatting and repo hygiene

- Prettier with `printWidth: 100` (one formatting standard across the apps), ESLint flat config
  with `eslint-config-next`. CI runs `format:check`.
- `.editorconfig`: UTF-8, LF, 2-space indent, final newline, trim trailing whitespace except in
  Markdown.
- `.gitattributes` forces LF (`* text=auto eol=lf`, plus an explicit list for scripts). Windows
  checkouts with CRLF have broken container entrypoints before.
- Formatting-only commits go in `.git-blame-ignore-revs`.

## Different on purpose

Layout (`web/` subfolder or repo root), ORM, auth, i18n and AI integrations stay per app.
