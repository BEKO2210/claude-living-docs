"""Sample module used as a known input for extractor tests."""

from __future__ import annotations

import functools

CONSTANT = 42


class Base:
    """A base class so the sample has a real inheritance edge."""


@functools.cache
def add(a: int, b: int = 1) -> int:
    """Add two integers."""
    return a + b


async def fetch(url: str, *args: str, timeout: float = 1.0, **kwargs: int) -> bytes:
    """Fetch bytes from ``url``."""
    return b""


def _private() -> None:
    """Should be excluded from the public API."""


class Greeter(Base):
    """Greets people by name."""

    def greet(self, name: str) -> str:
        """Return a greeting for ``name``."""
        return f"Hi {name}"

    def _secret(self) -> None:
        """Should be excluded from the public API."""


class _Hidden:
    """Should be excluded from the public API."""
