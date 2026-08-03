"""Command-line interface for FocusPing."""

from __future__ import annotations

import argparse
import sys
from typing import Sequence

from .timer import Phase, SessionPlan, countdown, format_remaining, total_seconds


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="focusping",
        description="A gentle terminal timer for focused work sessions.",
    )
    parser.add_argument(
        "--focus",
        type=positive_int,
        default=25,
        metavar="MINUTES",
        help="length of each focus phase (default: 25)",
    )
    parser.add_argument(
        "--break",
        dest="break_minutes",
        type=positive_int,
        default=5,
        metavar="MINUTES",
        help="length of each break phase (default: 5)",
    )
    parser.add_argument(
        "--cycles",
        type=positive_int,
        default=1,
        metavar="COUNT",
        help="number of focus phases (default: 1)",
    )
    parser.add_argument(
        "--skip-break",
        action="store_true",
        help="run focus phases back-to-back",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="show phase changes without a live countdown",
    )
    return parser


def positive_int(value: str) -> int:
    """Parse a positive integer for argparse."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a whole number") from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def ping() -> None:
    """Make a terminal-friendly completion sound."""
    print("\a", end="", flush=True)


def run(plan: SessionPlan, *, quiet: bool = False) -> int:
    phases = plan.phases()
    total_minutes = total_seconds(phases) // 60
    print(f"FocusPing  |  {len(phases)} phases  |  {total_minutes} minutes total")
    print("Press Ctrl+C to stop.\n")

    try:
        for phase in phases:
            print(f"{phase.name} started.")
            if quiet:
                countdown(phase)
            else:
                countdown(phase, on_tick=render_tick)
            if not quiet:
                print()
            ping()
            if phase.kind == "focus":
                print("Focus complete. Nice work.")
            else:
                print("Break complete. Ready when you are.")
    except KeyboardInterrupt:
        print("\nFocusPing stopped. Your progress is still yours.")
        return 130

    print("\nAll done. Take a moment to notice what you finished.")
    return 0


def render_tick(phase: Phase, remaining: int) -> None:
    print(
        f"\r{phase.name}: {format_remaining(remaining)}",
        end="",
        flush=True,
    )


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    plan = SessionPlan(
        focus_minutes=args.focus,
        break_minutes=args.break_minutes,
        cycles=args.cycles,
        include_breaks=not args.skip_break,
    )
    return run(plan, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())