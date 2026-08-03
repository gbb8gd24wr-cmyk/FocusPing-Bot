"""FocusPing Discord bot.

The bot uses the Discord token from the DISCORD_TOKEN environment variable.
Never hard-code a token in this file.
"""

from __future__ import annotations

import asyncio
import os
import random
from typing import Final

import discord
from discord.ext import commands


COMMAND_PREFIX: Final = "!"
MAX_TIMER_MINUTES: Final = 24 * 60
POMODORO_FOCUS_MINUTES: Final = 25
POMODORO_BREAK_MINUTES: Final = 5
MOTIVATIONAL_QUOTES: Final = (
    "Small progress is still progress.",
    "The secret of getting ahead is getting started.",
    "You do not have to be perfect to make meaningful progress.",
    "One focused hour can change the shape of your whole day.",
    "Start where you are. Use what you have. Do what you can.",
    "Your future self will thank you for the work you do today.",
)

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
active_timers: dict[tuple[int, int], asyncio.Task[None]] = {}
study_minutes: dict[int, int] = {}


def timer_key_for(ctx: commands.Context[commands.Bot]) -> tuple[int, int]:
    """Identify a user's timer separately in each server."""
    return (ctx.guild.id if ctx.guild else 0, ctx.author.id)


@bot.event
async def on_ready() -> None:
    """Log a minimal startup message once Discord has connected."""
    if bot.user is not None:
        print(f"FocusPing connected as {bot.user} (ID: {bot.user.id})")


@bot.command(name="ping")
async def ping(ctx: commands.Context[commands.Bot]) -> None:
    """Check whether the bot is responding."""
    await ctx.send("Pong!")


@bot.command(name="quote")
async def quote(ctx: commands.Context[commands.Bot]) -> None:
    """Send a random motivational study quote."""
    await ctx.send(f"“{random.choice(MOTIVATIONAL_QUOTES)}”")


@bot.command(name="timer")
async def timer(ctx: commands.Context[commands.Bot], minutes: str) -> None:
    """Start a timer or cancel it with ``!timer cancel``."""
    timer_key = timer_key_for(ctx)
    existing = active_timers.get(timer_key)

    if minutes.lower() == "cancel":
        if existing is None or existing.done():
            await ctx.send("You do not have an active timer.")
            return
        existing.cancel()
        active_timers.pop(timer_key, None)
        await ctx.send("Timer cancelled.")
        return

    try:
        duration = int(minutes)
    except ValueError:
        await ctx.send("Usage: `!timer <minutes>` or `!timer cancel`.")
        return

    if not 1 <= duration <= MAX_TIMER_MINUTES:
        await ctx.send(f"Choose a timer between 1 and {MAX_TIMER_MINUTES} minutes.")
        return

    if existing is not None and not existing.done():
        await ctx.send("You already have a timer running. Use `!timer cancel` first.")
        return

    await ctx.send(f"Timer started for {duration} minute{'s' if duration != 1 else ''}.")
    active_timers[timer_key] = asyncio.create_task(
        finish_timer(ctx, timer_key, duration)
    )


@bot.command(name="pomodoro")
async def pomodoro(ctx: commands.Context[commands.Bot]) -> None:
    """Run a 25-minute focus session followed by a five-minute break."""
    timer_key = timer_key_for(ctx)
    existing = active_timers.get(timer_key)
    if existing is not None and not existing.done():
        await ctx.send("You already have a timer running. Use `!timer cancel` first.")
        return

    await ctx.send(
        "Pomodoro started: 25 minutes of focus. "
        "I’ll remind you when it’s time for a 5-minute break."
    )
    active_timers[timer_key] = asyncio.create_task(
        finish_pomodoro(ctx, timer_key)
    )


async def finish_timer(
    ctx: commands.Context[commands.Bot],
    timer_key: tuple[int, int],
    minutes: int,
) -> None:
    """Wait in the background and announce when a timer finishes."""
    try:
        await asyncio.sleep(minutes * 60)
        await ctx.send(f"Time's up, {ctx.author.mention}. Nice work!")
    except asyncio.CancelledError:
        raise
    finally:
        if active_timers.get(timer_key) is asyncio.current_task():
            active_timers.pop(timer_key, None)


async def finish_pomodoro(
    ctx: commands.Context[commands.Bot],
    timer_key: tuple[int, int],
) -> None:
    """Finish the focus phase, announce the break, and finish the break."""
    try:
        await asyncio.sleep(POMODORO_FOCUS_MINUTES * 60)
        await ctx.send(
            f"Focus session complete, {ctx.author.mention}! "
            "Your 5-minute break starts now."
        )
        await asyncio.sleep(POMODORO_BREAK_MINUTES * 60)
        await ctx.send(
            f"Break complete, {ctx.author.mention}. "
            "Ready for your next focused session?"
        )
    except asyncio.CancelledError:
        raise
    finally:
        if active_timers.get(timer_key) is asyncio.current_task():
            active_timers.pop(timer_key, None)


@bot.command(name="logstudy")
async def logstudy(ctx: commands.Context[commands.Bot], minutes: str) -> None:
    """Add study minutes to the calling user's total."""
    try:
        amount = int(minutes)
    except ValueError:
        await ctx.send("Usage: `!logstudy <minutes>` with a whole number of minutes.")
        return

    if amount <= 0:
        await ctx.send("Study minutes must be greater than zero.")
        return

    study_minutes[ctx.author.id] = study_minutes.get(ctx.author.id, 0) + amount
    total = study_minutes[ctx.author.id]
    await ctx.send(
        f"Logged {amount} minute{'s' if amount != 1 else ''} of study. "
        f"Your total is now {total} minute{'s' if total != 1 else ''}."
    )


@bot.command(name="leaderboard")
async def leaderboard(ctx: commands.Context[commands.Bot]) -> None:
    """Show users ranked by their total logged study minutes."""
    if not study_minutes:
        await ctx.send("No study minutes have been logged yet. Use `!logstudy <minutes>`.")
        return

    lines = ["**FocusPing Study Leaderboard**"]
    for rank, (user_id, minutes) in enumerate(
        sorted(study_minutes.items(), key=lambda entry: entry[1], reverse=True)[:10],
        start=1,
    ):
        member = ctx.guild.get_member(user_id) if ctx.guild else None
        user = member or bot.get_user(user_id)
        name = getattr(user, "display_name", None) or getattr(
            user, "name", f"User {user_id}"
        )
        lines.append(f"{rank}. **{name}** — {minutes} minutes")

    await ctx.send("\n".join(lines))


@timer.error
async def timer_error(
    ctx: commands.Context[commands.Bot],
    error: commands.CommandError,
) -> None:
    """Give a useful message when !timer is missing its argument."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!timer <minutes>` or `!timer cancel`.")
        return
    raise error


@logstudy.error
async def logstudy_error(
    ctx: commands.Context[commands.Bot],
    error: commands.CommandError,
) -> None:
    """Give a useful message when !logstudy is missing its argument."""
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Usage: `!logstudy <minutes>` with a whole number of minutes.")
        return
    raise error


def main() -> None:
    """Start the bot using the securely stored Discord token."""
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise RuntimeError(
            "DISCORD_TOKEN is not set. Add it as a Replit Secret before starting the bot."
        )
    bot.run(token)


if __name__ == "__main__":
    main()