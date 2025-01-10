import secrets
from typing import Tuple


def roll() -> Tuple[int, int]:
    return secrets.randbelow(6) + 1, secrets.randbelow(6) + 1
