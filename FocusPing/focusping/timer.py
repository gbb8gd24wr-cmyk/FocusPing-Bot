"""Core planning and countdown utilities for FocusPing."""

from __future__ import annotations

import math
import time
from dataclasses import dataclass
from typing import Callable, Iterable


@dataclass(frozen=True)
class Phase:
    """One timed phase in a focus plan."""

    name: str
    duration_seconds: int
    kind: str

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("phase name cannot be empty")
        if self.duration_seconds <= 0:
            raise ValueError("phase duration must be greater than zero")
        if self.kind not in {"focus", "break"}:
            raise ValueError("phase kind must be 'focus' or 'break'")


@dataclass(frozen=True)
class SessionPlan:
    """A sequence of focus and break phases."""

    focus_minutes: int = 25
    break_minutes: int = 5
    cycles: int = 1
    include_breaks: bool = True

    def __post_init__(self) -> None:
        if self.focus_minutes <= 0:
            raise ValueError("focus duration must be greater than zero")
        if self.break_minutes <= 0:
            raise ValueError("break duration must be greater than zero")
        if self.cycles <= 0:
            raise ValueError("cycles must be greater than zero")

    def phases(self) -> tuple[Phase, ...]:
        """Return the phases in the order they should be run."""
        result: list[Phase] = []
        for cycle in range(1, self.cycles + 1):
            result.append(
                Phase(
                    name=f"Focus {cycle}/{self.cycles}",
                    duration_seconds=self.focus_minutes * 60,
                    kind="focus",
                )
            )
            if self.include_breaks and cycle < self.cycles:
                result.append(
                    Phase(
                        name=f"Break after focus {cycle}",
                        duration_seconds=self.break_minutes * 60,
                        kind="break",
                    )
                )
        return tuple(result)


def format_remaining(seconds: int) -> str:
    """Format a non-negative number of seconds as MM:SS."""
    seconds = max(0, seconds)
    minutes, remainder = divmod(seconds, 60)
    return f"{minutes:02d}:{remainder:02d}"


def countdown(
    phase: Phase,
    *,
    on_tick: Callable[[Phase, int], None] | None = None,
    sleep: Callable[[float], None] = time.sleep,
    monotonic: Callable[[], float] = time.monotonic,
    tick_seconds: float = 1.0,
) -> None:
    """Run one phase, calling ``on_tick`` with whole seconds remaining.

    The monotonic clock is used to avoid countdown drift if printing or
    sleeping takes slightly longer than expected.
    """
    if tick_seconds <= 0:
        raise ValueError("tick interval must be greater than zero")

    deadline = monotonic() + phase.duration_seconds
    remaining = phase.duration_seconds
    while remaining > 0:
        if on_tick is not None:
            on_tick(phase, remaining)
        sleep(min(tick_seconds, remaining))
        remaining = max(0, math.ceil(deadline - monotonic()))

    if on_tick is not None:
        on_tick(phase, 0)


def total_seconds(phases: Iterable[Phase]) -> int:
    """Return the total duration of a phase sequence."""
    return sum(phase.duration_seconds for phase in phases)