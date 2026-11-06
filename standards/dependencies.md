# Dependencies

- **Follows:** moneyworks, vocabulary-training
- **Checked:** 2026-11-06 (moneyworks `f31e49b`, vocabulary-training `95f3d8a`)
- **Reference files:** `package.json`, `.npmrc`, `.github/dependabot.yml`

## Rules

- **Exact versions** for every direct dependency (no `^` or `~`), a committed `package-lock.json`,
  and `.npmrc` with `save-exact=true` so a later `npm install x` doesn't bring a range back.
- `engines` (Node and npm) and `packageManager` declared; npm pinned in the image.
- Compatible stable releases only: no prereleases, no forced peer overrides.
- **Qualify every extra package.** Frameworks are fine; for ordinary UI and utilities prefer native
  HTML, Node APIs and small maintained code. An established security or protocol library may
  justify a dependency; say why in the PR.
- **Dependabot** weekly for npm (minor and patch grouped), Docker and Actions. Hold majors that
  need a decision: Node and `@types/node` (Node 22 floor), PostgreSQL (a major needs dump/restore
  or `pg_upgrade`), and TypeScript/ESLint until the lint plugins support them. Group majors that
  must move together.
- `npm audit --audit-level=high` in CI.

## Package availability (not adopted)

Lockfiles fix versions but don't protect against a package being unpublished, which has broken
the owner's installs before. The old project's options, in increasing cost: lockfile only (now);
a Verdaccio cache in Docker that keeps every installed package (worth it at 3+ active projects);
vendored tarballs for critical dependencies. Neither of the last two is adopted.
