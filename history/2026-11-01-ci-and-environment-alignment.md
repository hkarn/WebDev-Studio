# CI and environment alignment

- Status: mostly adopted. Both repos merged alignment PRs on 2026-11-01; see [Re-check after alignment](#re-check-after-alignment-2026-11-01) for what is still different.
- Date: 2026-11-01 (first comparison and re-check)
- Apps: [moneyworks](https://github.com/GothenburgOffice/moneyworks), [vocabulary-training](https://github.com/GothenburgOffice/vocabulary-training)

The first comparison below describes the repos **before** the alignment work. The re-check at the end describes them after it.

## What was compared

The default branch of both repos as of 2026-11-01:

- `.github/workflows/ci.yml` (each repo's only workflow)
- Dockerfiles, Compose files (dev, release and image-only), devcontainer config
- `.env.example`, `package.json`, `next.config.ts`, `.gitattributes`, `.dockerignore`, `dependabot.yml`
- The Actions usage report for 2026-11-01

## How

Read the files through the GitHub API and compared them side by side. Nothing was run or changed.

## Result: CI workflows

Both use the same three-stage shape, so they probably came from a shared template:

1. `unit` checks.
2. `containers`: a full Compose stack test.
3. Release job: builds the image once, tests that exact image without source mounts, pushes `sha-<SHA>` and `latest` to GHCR, then checks an anonymous pull.

Shared details:

- Least-privilege permissions, with `packages: write` only on the release job.
- A non-cancelling concurrency group for publishing.
- Logs on failure, cleanup always.

moneyworks has grown into the stricter version of it.

| Aspect | moneyworks | vocabulary-training |
|---|---|---|
| Push trigger | `main` only | every branch (each PR commit runs twice) |
| Cancelling old runs | Only PR runs are cancelled; main always finishes | Everything is cancelled, including main, so a merge can lose its publish |
| Action versions | Exact (`@v7.0.1`) | Major only (`@v7`) |
| Node | Matrix of 22.23.4 and 26.13.0, npm pinned | `22` |
| Required check | Separate `unit` job gives a stable name over the matrix | The job itself |
| Timeouts | On every job | None (6 h default) |
| Unit checks | Line endings, lint, many test suites, typecheck, Prisma validate, build, migrations, account tests against a Postgres service, `npm audit` | `format:check`, lint, typecheck, test, build |
| Container tests | Windows CRLF checkout, compose and devcontainer config validation, English and Swedish smoke tests, database failure handling (503, not cached, recovers) | Integration tests, restart persistence |
| Release job on PRs | Builds and tests the image, publishes only on main | Skipped entirely, so a broken production Dockerfile is only caught after merge |
| Release-image checks | Smoke test, non-root user, no source in the image, cleanup script, restart persistence | Integration tests, restart persistence |

Recommended for vocabulary-training:

- Run the release-image test on PRs.
- Don't cancel main runs.
- Add timeouts.
- Pin exact action versions.
- Limit `push` to `main`.
- Add `npm audit`.

Recommended for moneyworks: add `format:check` (Prettier).

## Result: dev and prod environments

### Align now (cheap while new, expensive later)

1. **PostgreSQL major version and volume path.**
   - moneyworks: `postgres:18.6`, volume at `/var/lib/postgresql`.
   - vocabulary-training: `postgres:17-bookworm`, volume at `/var/lib/postgresql/data`.
   - Postgres 18 images keep data in a different place, and a major upgrade means dump/restore later. Dependabot skips postgres majors, so nothing will prompt it. Move vocabulary-training to 18 with the new mount path before it holds real data.
2. **Version pinning.**
   - moneyworks pins exactly: `node:22.23.4-trixie-slim`, npm 12.2.1, exact dependency and action versions.
   - vocabulary-training floats: `node:22-bookworm-slim`, `^` ranges, `@v7`.
   - Pick one policy (proposed: exact pins) and one Debian base.
3. **Security headers.**
   - vocabulary-training sets a full CSP and security headers on every route.
   - moneyworks sets them only on `/:locale/account`, and that CSP is only `frame-ancestors`.
   - moneyworks should adopt the site-wide set and `poweredByHeader: false`.
4. **Env var and service naming.**

   | Concept | moneyworks | vocabulary-training |
   |---|---|---|
   | Public URL | `AUTH_BASE_URL` | `APP_ORIGIN` |
   | Open signup | `AUTH_PUBLIC_SIGNUP` | `ALLOW_REGISTRATION` |
   | Host port | `MONEYWORKS_WEB_PORT` (3410) | `APP_PORT` (3000) |
   | Image override | `MONEYWORKS_IMAGE` | `VOCABULARY_IMAGE` |
   | App service | `web` | `app` |
   | Health endpoint | `/api/health/db` | `/api/health` |

   Agree on one pattern. Give vocabulary-training an uncommon default host port, because 3000 clashes with other local projects.
5. **Compose and Dockerfile layout.**
   - moneyworks: `docker-compose.dev.yml` and `docker-compose.images.yml`, a separate `Dockerfile.dev`, and the app in `web/`.
   - vocabulary-training: `compose.yaml`, `compose.dev.yaml` and `compose.images.yaml`, and one multi-stage Dockerfile with a `development` target.
   - The vocabulary-training layout is the cleaner, current one.

### Lower stakes

- **Local dev without `.env`:** moneyworks dev runs with built-in defaults. vocabulary-training requires `POSTGRES_PASSWORD` even for dev. Keep the required check only for the image stack.
- **Database user:** moneyworks dev uses the `postgres` superuser but its release stack uses a `moneyworks` user. Use the same dedicated user everywhere.
- **Devcontainer:** vocabulary-training starts the dev server itself and reinstalls only when the lockfile changes. It also mounts Claude memory from outside the repo. moneyworks uses `sleep infinity`. Pick one approach.
- **Repo hygiene:** moneyworks has `.editorconfig` and an explicit LF list in `.gitattributes` with a CI test. vocabulary-training has Prettier. Each should take the other's.
- **Engines:** moneyworks declares Node, npm and `packageManager`. vocabulary-training declares only `node >=22`. TypeScript is 6 vs 5.

### Different on purpose

These don't need aligning unless the apps start sharing code:

- Prisma vs plain `pg` with SQL migrations.
- better-auth with SMTP vs custom auth.
- next-intl, and the AI integration.

## Result: Actions cost

Both repos are public, so standard GitHub-hosted runners are free. The usage report for 2026-11-01:

| Repo | Minutes | Gross | Discount | Net |
|---|---|---|---|---|
| moneyworks | 107 | $0.642 | -$0.642 | $0 |
| vocabulary-training | 105 | $0.63 | -$0.63 | $0 |

`gross_amount` is list price ($0.006/min for Linux). The public-repo exemption shows up as an equal `discount_amount`. Only `net_amount` is billed.

At this volume (about 106 minutes per repo per day), making the repos private would cost roughly $35-40 a month for the two together, before any free quota.

Ways to cut runs anyway:

1. vocabulary-training: `push: branches: [main]`. This removes the duplicate push and PR runs.
2. Both: `paths-ignore` for docs-only changes. moneyworks needs a path filter inside the job instead, so the required `unit` check still reports.
3. Skip draft PRs.
4. moneyworks: optionally run only Node 22 on PRs and the full matrix on main.
5. Add timeouts to vocabulary-training.
6. Dependabot: switch Docker and Actions updates to monthly if the PR volume is noisy.
7. Guard: an org Actions budget of $0 with "stop usage", so a private repo or larger runner fails instead of billing.

## Re-check after alignment (2026-11-01)

### What was compared

The default branches at:

- moneyworks `2380286` (after PRs #40-#48)
- vocabulary-training `1b6cf8b` (after PRs #35-#43)

The same files as before, read through the GitHub API. Nothing was run.

### Now aligned

| Area | Both repos now |
|---|---|
| PostgreSQL | `postgres:18.6`, volume at `/var/lib/postgresql`, dedicated app user (`moneyworks` / `vocabulary`) in every stack |
| Node and npm | `node:22.23.4-trixie-slim`, npm `12.2.1`, `engines` and `packageManager` declared |
| Dependencies | Exact versions, no `^` ranges |
| Actions | Exact versions (`checkout@v7.0.1`, `setup-node@v7.1.0`, `login-action@v4.7.0`) |
| CI triggers | `push` to `main` only, PRs, manual. Only PR runs are cancelled, so every merge publishes |
| CI jobs | Timeouts on every job. Unit runs once on Node 22 (moneyworks dropped its Node 26 matrix). `format:check` and `npm audit --audit-level=high` in both |
| Release image | Built and tested on every PR; login, push and the anonymous-pull check only on `main` |
| Compose files | `compose.yaml` (production build from source) + `compose.dev.yaml` (dev override) + `compose.images.yaml` (published image), with a one-shot `migrate` service |
| Dockerfile | One multi-stage file with `development`, `migration`, `builder` and `production` targets (moneyworks dropped `Dockerfile.dev`) |
| Service and health | Service `app`, health endpoint `/api/health`, returns 503 when the database is down |
| Env names | `POSTGRES_PASSWORD` (required in every stack), `APP_PORT`, `APP_ORIGIN`, new `APP_ORIGIN_ALIASES`, `ALLOW_REGISTRATION`, `DEV_*` for dev-only secrets |
| Host ports | moneyworks 3410, vocabulary-training 3420 (distinct and uncommon) |
| Security headers | Same site-wide set: CSP, `nosniff`, `same-origin` referrer, `DENY` framing, Permissions-Policy, `poweredByHeader: false` |
| Devcontainer | Runs `db`, `migrate` and `app`; `overrideCommand: false`, so the dev server starts itself and reinstalls only when the lockfile changes; Prettier, ESLint and Actions extensions; Claude config volume; project memory mounted from `~/.claude-memory/<app>` |
| Formatting | Prettier with `printWidth: 100`, `.editorconfig`, `.git-blame-ignore-revs` |

One earlier suggestion went the other way, which is fine. Instead of moneyworks' "dev works without `.env`", both now require a `.env` with `POSTGRES_PASSWORD` for every stack.

### Still different

#### Worth fixing

1. **The vocabulary-training dev command keeps going after a failed install.**
   - Its reinstall line joins the steps with `;`, so `next dev` starts on a broken `node_modules` when `npm ci` fails.
   - moneyworks fixed exactly this in `f9bb1ef` with `(...) && exec npm run dev`. Port that fix.
2. **In vocabulary-training, the dev-only overrides exist only in the devcontainer.**
   - The reinstall command, `ALLOW_REGISTRATION=true` and the `DEV_REQUESTY_*` key swap are all in `.devcontainer/compose.yaml`.
   - So plain `docker compose -f compose.yaml -f compose.dev.yaml up` uses the **production** Requesty keys from `.env`, and doesn't reinstall.
   - moneyworks puts all of this in `compose.dev.yaml`, so every dev stack ignores production secrets. Move vocabulary-training's into `compose.dev.yaml`. Dev should then also read `DEV_APP_ORIGIN` / `DEV_APP_ORIGIN_ALIASES`, as moneyworks does.
3. **The vocabulary-training CSP loads Google Fonts.**
   - Its CSP allows `fonts.googleapis.com` / `fonts.gstatic.com`, so visitors' IP addresses go to Google.
   - EU courts have treated that as a GDPR issue.
   - moneyworks serves fonts from itself (`font-src 'self'`). Self-host the fonts in vocabulary-training, for example with `next/font`, which bundles them at build time, and drop the Google hosts from the CSP.
4. **moneyworks may need `allowedDevOrigins`.**
   - Its dev stack sets `http://127.0.0.1:3410` as an origin alias, but `next.config.ts` has no `allowedDevOrigins`.
   - vocabulary-training sets `allowedDevOrigins: ["127.0.0.1"]`.
   - Recent Next.js versions block dev-only assets requested from origins that aren't allowed, so opening dev on 127.0.0.1 may break hot reload. Not tested; check by opening `http://127.0.0.1:3410` in dev.
5. **The `release` concurrency group in moneyworks also covers PRs.**
   - It is `release-image-<repo>` for every event, so image tests from different PRs queue behind each other and behind a `main` publish.
   - vocabulary-training splits it: a per-ref group on PRs, a repo-wide one on `main`. Copy that.

#### Worth copying, lower stakes

| Item | Has it | Missing in |
|---|---|---|
| `COMPOSE_PROJECT_NAME` per CI job and checks that cleanup left nothing behind | moneyworks | vocabulary-training |
| CI step that validates every Compose combination and the devcontainer file | moneyworks | vocabulary-training |
| CI checkout with Windows `core.autocrlf=true`, explicit LF list in `.gitattributes`, and a line-endings test | moneyworks | vocabulary-training (its `.gitattributes` only has `* text=auto eol=lf` and the binaries) |
| Release-image checks: runs as non-root, no source in the image | moneyworks | vocabulary-training |
| CI test of the database-down path (503, not cached, recovers) | moneyworks | vocabulary-training (the endpoint returns 503, but CI never tests it) |
| `.npmrc` with `save-exact=true`, so a later `npm install x` doesn't bring back `^` | vocabulary-training | moneyworks |
| Fuller `.editorconfig` (2-space indent, trim trailing whitespace except in Markdown) | vocabulary-training | moneyworks |
| `APP_ORIGIN` default derived from `APP_PORT` | moneyworks | vocabulary-training (its default is hard-coded to `http://localhost:3420`) |
| Dependabot holds TypeScript and ESLint majors and groups the majors that must move together | moneyworks | vocabulary-training |

#### Different on purpose, or not worth aligning

- **Layout:** moneyworks keeps the app in `web/`, so its build context is `web/` and the devcontainer opens `/workspace`. vocabulary-training is at the repo root with `/app`.
- **Naming:**
  - Workflow name: `CI` vs `Verify`.
  - Release job: `release` vs `publish`.
  - Postgres volume: `postgres18_data` vs `postgres_data`.
  - Image override: `MONEYWORKS_IMAGE` vs `VOCABULARY_IMAGE`.

  These are cosmetic; rename them only if you want copy-paste parity.
- **TypeScript:** 6.0.3 vs 5.9.3. moneyworks holds TS majors back for the Next.js lint plugin. Move vocabulary-training to 6 when Dependabot offers it and lint passes, or hold it the same way.
- **`NODE_ENV` in dev:** vocabulary-training sets `NODE_ENV=development` in `compose.dev.yaml`. moneyworks leaves it unset on purpose, because `next dev` and `next build` set it themselves. Either works.
- **Release-image migrations:** moneyworks ships a trimmed Prisma CLI; vocabulary-training ships `scripts/migrate.mjs`. This follows from Prisma vs plain SQL.
- **Product-specific:** the moneyworks `Referrer-Policy: strict-origin` on account pages and `logging.incomingRequests: false` (recovery tokens in URLs); the vocabulary-training Requesty AI keys.
