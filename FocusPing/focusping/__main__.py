"""Allow ``python -m focusping`` to start FocusPing."""

from .cli import main


if __name__ == "__main__":
    raise SystemExit(main())