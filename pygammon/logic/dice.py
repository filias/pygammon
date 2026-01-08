import secrets
from typing import Tuple

from pygammon.logic.models import Die


def roll() -> Tuple[int, int]:
    """Roll two dice and return their values."""
    return secrets.randbelow(6) + 1, secrets.randbelow(6) + 1


__all__ = ["Die", "roll"]