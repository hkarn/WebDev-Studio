# Standards

How an app is built when it follows these standards. Each page is short, says who follows it and
when it was last checked against those repositories, and names the app files that are the
working reference. When an app and a standard disagree, the app's files show what is implemented;
fix whichever is wrong, and say which in the commit.

All six were written on 2026-11-06 from the shared setup of moneyworks (`f31e49b`) and
vocabulary-training (`95f3d8a`), which were aligned on 2026-11-01
([the comparison](../history/2026-11-01-ci-and-environment-alignment.md)). **Status: draft until
the owner has reviewed them.**

| Standard | Covers |
|---|---|
| [new-app.md](new-app.md) | Checklist for starting a new app that follows the standards below |
| [nextjs-postgres.md](nextjs-postgres.md) | The stack: Next.js App Router, TypeScript, PostgreSQL 18, Node 22, formatting |
| [dev-environment.md](dev-environment.md) | Docker-first: Compose files, Dockerfile targets, dev container, env names, ports |
| [ci.md](ci.md) | GitHub Actions: the unit / containers / release-image jobs, triggers, timeouts |
| [dependencies.md](dependencies.md) | Exact pins, lockfile, Dependabot holds, npm availability |
| [security.md](security.md) | Security headers, secrets, server-side checks, privacy defaults |
| [agent-instructions.md](agent-instructions.md) | How an app repo instructs coding agents: shared file, Claude file, decisions, notes, shared memory |

Adding a standard: only for something the owner adopted for more than one app. Give it the same
header (follows, checked, reference), add its line here, and add it to the apps' rows in
[apps/INDEX.md](../apps/INDEX.md).
