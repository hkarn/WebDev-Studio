# Security

- **Follows:** moneyworks, vocabulary-training
- **Checked:** 2026-11-06 (moneyworks `f31e49b`, vocabulary-training `95f3d8a`)
- **Reference files:** `next.config.ts` (headers), vocabulary-training `docs/security.md`,
  moneyworks `SECURITY.md` and `AUTH.md`

## Headers (site-wide, every route)

`Content-Security-Policy` starting from
`default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; font-src 'self'; img-src 'self' data: blob:; connect-src 'self'; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'`
(add `'unsafe-eval'` to `script-src` in development only), plus `X-Content-Type-Options: nosniff`,
`Referrer-Policy: same-origin`, `X-Frame-Options: DENY`, a `Permissions-Policy`, and
`poweredByHeader: false`.

**Self-host fonts** (`next/font`), never Google Fonts at runtime: loading them sends visitors' IP
addresses to Google, which EU courts have treated as a GDPR issue.

## Server side

- Validate untrusted input on the server (schemas such as Zod), with allowlists where possible.
- Parameterized queries only; every query on user data filters on the user's id.
- Mutating routes check the request origin, then the session, then per-account write limits
  (vocabulary-training: `requireOrigin`, `requireUser`, `limitWrites`).
- Errors go through one helper (vocabulary-training: `HttpError`/`fail`).

## Secrets

- Never in source, images, docs or a `NEXT_PUBLIC_` variable. `.env` is gitignored; dev uses
  separate `DEV_*` values.
- Keys an admin enters are stored encrypted (an app-level encryption key from the environment) and
  never sent back to the browser; show only whether one is set and its last four characters.
- Never commit credentials, personal contact details or operator data. The app repos are public.

## Privacy defaults

- A real site starts with registration closed and no privacy details; only dev and test stacks
  seed it open, with `example.test` values that say they aren't a real operator.
- No non-essential cookies or browser storage without a consent decision.
- Send an outside provider (AI, mail) only what its call needs: never account ids or whole lists.

## Verification

Check dependencies (`npm audit` in CI) and running behaviour (integration tests, the database-down
test). Source of the general practices: Microsoft's
[secure development guidance](https://learn.microsoft.com/azure/security/develop/secure-develop#implementation).
