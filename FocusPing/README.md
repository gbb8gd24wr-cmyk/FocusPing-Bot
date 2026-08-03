# FocusPing

FocusPing is a tiny, dependency-free focus timer for the terminal. Start a
focused work block, get a gentle terminal ping when it ends, and take a short
break before the next round.

## Run it

From the repository root:

```bash
cd FocusPing
python -m focusping --focus 25 --break 5 --cycles 2
```

Or, after installing the project in editable mode:

```bash
cd FocusPing
python -m pip install -e .
focusping
```

Useful options:

```text
--focus MINUTES       Focus length (default: 25)
--break MINUTES       Break length (default: 5)
--cycles COUNT        Number of focus sessions (default: 1)
--skip-break          Do not pause between sessions
--quiet               Hide the live countdown and only show phase changes
```

Stop a running timer with `Ctrl+C`.

## Test it

```bash
cd FocusPing
python -m unittest discover -s tests -v
```

FocusPing uses only the Python standard library.