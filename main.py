"""FocusPing Discord bot.

The bot uses the Discord token from the DISCORD_TOKEN environment variable.
Never hard-code a token in this file.
"""

from __future__ import annotations

import asyncio
import os
from typing import Final

import discord
from discord.ext import commands


COMMAND_PREFIX: Final = "!"
MAX_TIMER_MINUTES: Final = 24 * 60

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=intents)
active_timers: dict[tuple[int, int], asyncio.Task[None]] = {}


@bot.event
async def on_ready() -> None:
    """Log a minimal startup message once Discord has connected."""
    if bot.user is not None:
        print(f"FocusPing connected as {bot.user} (ID: {bot.user.id})")


@bot.command(name="ping")
async def ping(ctx: commands.Context[commands.Bot]) -> None:
    """Check whether the bot is responding."""
    await ctx.send("Pong!")


@bot.command(name="timer")
async def timer(ctx: commands.Context[commands.Bot], minutes: str) -> None:
    """Start a timer with ``!timer <minutes>`` or cancel it with ``!timer cancel``."""
    timer_key = (ctx.guild.id if ctx.guild else 0, ctx.author.id)
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
    task = asyncio.create_task(finish_timer(ctx, timer_key, duration))
    active_timers[timer_key] = task


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
        active_timers.pop(timer_key, None)


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
