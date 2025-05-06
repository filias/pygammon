import secrets
from typing import Tuple

from pydantic import BaseModel, Field


def roll() -> Tuple[int, int]:
    return secrets.randbelow(6) + 1, secrets.randbelow(6) + 1


class Die(BaseModel):
    value: int = Field(..., ge=1, le=6)

    def roll(self) -> int:
        self.value = secrets.randbelow(6) + 1
        return self.value