import secrets
from typing import Tuple


def roll() -> Tuple[int, int]:
    """Roll two dice and return their values."""
    return secrets.randbelow(6) + 1, secrets.randbelow(6) + 1
