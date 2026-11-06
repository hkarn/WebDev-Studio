# CI: GitHub Actions

- **Follows:** moneyworks, vocabulary-training
- **Checked:** 2026-11-06 (moneyworks `f31e49b`, vocabulary-training `95f3d8a`)
- **Reference files:** `.github/workflows/ci.yml` in either app (moneyworks has the most checks)

## Shape

One workflow, three jobs:

1. **`unit`**: format check, lint, typecheck, unit tests, build, `npm audit --audit-level=high`.
   Runs once on Node 22. Its name is the stable required check.
2. **`containers`**: the full Compose stack from source, integration and browser tests against it,
   persistence across an app restart. Logs on failure, cleanup always.
3. **Release image**: build the production image once, test that exact image with
   `compose.images.yaml` (no source mounts), then on `main` only: sign in, push `sha-<SHA>` and
   `latest` to GHCR, and check an anonymous pull. On PRs it builds and tests but doesn't publish,
   so a broken production Dockerfile is caught before merge.

## Rules

- Triggers: `push` to `main` only, pull requests, manual. Skip draft PRs.
- Only PR runs are cancelled by newer pushes; `main` always finishes, so every merge publishes.
  The release concurrency group is per ref on PRs and repo-wide on `main`.
- `timeout-minutes` on every job.
- Least-privilege `permissions`; `packages: write` only on the release job.
- Actions pinned to exact versions (`actions/checkout@v7.0.1`, not `@v7`).
- `main` is protected: changes go through a PR, and `unit` and `containers` must pass. Pushing to
  `main` publishes the image, so agents push or merge only with the owner's go-ahead.

## Worth copying (moneyworks has them)

`COMPOSE_PROJECT_NAME` per job with a check that cleanup left nothing; validating every Compose
combination and the devcontainer file; a Windows `core.autocrlf=true` checkout with a
line-endings test; release-image checks for non-root and no source; a database-down test (503,
not cached, recovers).

## Cost

Public repos run on free standard runners. A private repo at the same volume would cost roughly
$35–40 a month for two apps (measured 2026-11-01), so keep an org Actions budget of $0 with "stop
usage" as a guard.
