# FocusPing Discord Bot

FocusPing is a small Discord bot with a command prefix of `!`.

## Commands

- `!ping` — replies with `Pong!`
- `!timer <minutes>` — starts a timer and announces when it finishes
- `!timer cancel` — cancels your active timer
- `!pomodoro` — runs a 25-minute focus session followed by a 5-minute break
- `!quote` — sends a random motivational study quote
- `!logstudy <minutes>` — adds study time to your personal total
- `!leaderboard` — shows the top logged study totals

## Run

The bot reads its token from the `DISCORD_TOKEN` secret:

```bash
python main.py
```

Before running it, enable the **Message Content Intent** for the bot in the
Discord Developer Portal. Never commit or hard-code the bot token.

Study totals are stored in memory and reset whenever the bot restarts.