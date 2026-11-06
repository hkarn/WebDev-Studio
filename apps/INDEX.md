# Apps

One line per app: its repository and which standards it follows. Each app's code, decisions
(issues labelled `decision`), backlog and state live in its own repository; nothing about them is
kept here. Update a row when an app adopts or drops a standard.

Checked against the repositories on 2026-11-06.

| App | Repository | Follows | Notes |
|---|---|---|---|
| moneyworks | [GothenburgOffice/moneyworks](https://github.com/GothenburgOffice/moneyworks) (public) | [nextjs-postgres](../standards/nextjs-postgres.md), [dev-environment](../standards/dev-environment.md), [ci](../standards/ci.md), [dependencies](../standards/dependencies.md), [security](../standards/security.md), [agent-instructions](../standards/agent-instructions.md) | App in `web/`; Prisma; better-auth. Finance tools hub, EN/SV |
| vocabulary-training | [GothenburgOffice/vocabulary-training](https://github.com/GothenburgOffice/vocabulary-training) (public) | all six, as moneyworks | App at the repo root; plain `pg` with SQL migrations; custom auth; Requesty AI features |
| habbits-nextjs | [hkarn/habbits-nextjs](https://github.com/hkarn/habbits-nextjs) (private) | not checked | Habit tracker, Next.js + PostgreSQL + NextAuth. Last push 2026-10-28; predates the 2026-11-01 alignment |
| reko-tour-booking-system | [HisingeBussAB/reko-tour-booking-system](https://github.com/HisingeBussAB/reko-tour-booking-system) | none | Legacy React/Redux + PHP booking system, inactive since 2021. Listed for reference only |

The owner's GitHub handle is `hkarn`; apps meant to be public go in the
[GothenburgOffice](https://github.com/GothenburgOffice) organisation.
