# FocusPing

FocusPing is a Python Discord bot with focus timers, motivational quotes, and in-memory study tracking.

## Run & Operate

- `cd FocusPing && python -m focusping` — start a default 25-minute focus session
- `cd FocusPing && python -m unittest discover -s tests -v` — run the test suite
- `python main.py` — start the Discord bot

- `pnpm --filter @workspace/api-server run dev` — run the API server (port 5000)
- `pnpm run typecheck` — full typecheck across all packages
- `pnpm run build` — typecheck + build all packages
- `pnpm --filter @workspace/api-spec run codegen` — regenerate API hooks and Zod schemas from the OpenAPI spec
- `pnpm --filter @workspace/db run push` — push DB schema changes (dev only)
- Required env: `DATABASE_URL` — Postgres connection string

## Stack

- FocusPing bot: Python 3.13 and `discord.py`
- pnpm workspaces, Node.js 24, TypeScript 5.9
- API: Express 5
- DB: PostgreSQL + Drizzle ORM
- Validation: Zod (`zod/v4`), `drizzle-zod`
- API codegen: Orval (from OpenAPI spec)
- Build: esbuild (CJS bundle)

## Where things live

- `main.py` — Discord bot entry point and commands
- `FocusPing/focusping/timer.py` — original phase planning, countdown timing, and formatting
- `FocusPing/focusping/cli.py` — original command-line interface
- `FocusPing/tests/` — standard-library unit tests

## Architecture decisions

- The Discord token is loaded only from the `DISCORD_TOKEN` secret and is never stored in source code.
- Timer and Pomodoro sessions run as background tasks so the bot can continue serving commands.
- Study totals are intentionally stored in memory and reset when the bot restarts.

## Product

- Respond to `!ping` with a health check.
- Start and cancel per-user timers with `!timer`.
- Run a 25-minute focus session followed by a five-minute break with `!pomodoro`.
- Send a random motivational quote with `!quote`.
- Track study minutes with `!logstudy` and rank totals with `!leaderboard`.
- Announce timer completion in the channel where the timer was started.

## User preferences

The bot token must remain in Replit Secrets under `DISCORD_TOKEN`.

## Gotchas

- Run the Discord bot from the repository root with `python main.py`.
- Enable Discord's Message Content Intent for the bot application.

## Pointers

- See the `pnpm-workspace` skill for workspace structure, TypeScript setup, and package details