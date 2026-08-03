# FocusPing

FocusPing is a dependency-free Python terminal timer for focused work sessions and gentle break reminders.

## Run & Operate

- `cd FocusPing && python -m focusping` — start a default 25-minute focus session
- `cd FocusPing && python -m unittest discover -s tests -v` — run the test suite

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- FocusPing: Python 3.10+ and the standard library

- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `FocusPing/focusping/timer.py` — phase planning, countdown timing, and formatting
- `FocusPing/focusping/cli.py` — command-line interface and terminal output
- `FocusPing/tests/` — standard-library unit tests

## Architecture decisions

- FocusPing has no runtime dependencies so it can run immediately in a clean Python environment.
- Countdown timing uses a monotonic clock to avoid drift during longer sessions.

## Product

- Start one or more focus sessions with configurable durations.
- Insert short breaks between focus sessions or run focus phases back-to-back.
- Display a live terminal countdown or a quiet phase-only mode.

## User preferences

No additional preferences recorded.

## Gotchas

- Run FocusPing commands from the `FocusPing` directory.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details
