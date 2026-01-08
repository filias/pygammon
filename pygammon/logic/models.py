import secrets

from pydantic import BaseModel, Field, ConfigDict
from enum import StrEnum
from typing import Annotated, List


class Color(StrEnum):
    """Represents the two player colors in backgammon."""
    DARK = "dark"
    LIGHT = "light"


class Die(BaseModel):
    """Represents a single die with a value between 1 and 6."""
    value: int = Field(..., ge=1, le=6)

    def roll(self) -> int:
        """Roll the die and return the new value."""
        self.value = secrets.randbelow(6) + 1
        return self.value

Checker = Annotated[Color, Field(alias="checker")]
Point = Annotated[int, Field(ge=1, le=24)]
Position = Annotated[dict[Point, list[Checker]], ...]


class Board:
    """Represents the backgammon board with checker positions, bar, and borne-off checkers."""
    position: Position
    bar: list[Checker]
    off_dark: list[Checker]
    off_light: list[Checker]
    main_direction: Checker

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, off_light: list | None = None, off_dark: list | None = None):
        self.position = self.initial_position
        self.bar = []
        self.off_dark = off_dark or []
        self.off_light = off_light or []
        self.main_direction = Checker.DARK

    @property
    def initial_position(self) -> Position:
        position = {
            Point(1): [Checker.DARK, Checker.DARK],
            Point(6): [Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT],
            Point(8): [Checker.LIGHT, Checker.LIGHT, Checker.LIGHT],
            Point(12): [Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK],
            Point(13): [Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT],
            Point(17): [Checker.DARK, Checker.DARK, Checker.DARK],
            Point(19): [Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK],
            Point(24): [Checker.LIGHT, Checker.LIGHT],
        }
        return position

    def __str__(self) -> str:
        return (
            f"{self.position}\n"
            f"Bar 1: {self.bar}\n"
            f"Off 1: {self.off_dark}\n"
            f"Off 2: {self.off_light}"
        )


class Player(BaseModel):
    """Represents a player with a name and assigned color."""
    name: str
    color: Color


class CheckerMove(BaseModel):
    """Represents a single checker move in backgammon."""
    from_point: Point | None = None  # None when entering from bar
    to_point: Point | None = None  # None when bearing off
    die_value: int = Field(..., ge=1, le=6)


class BackgammonMove(BaseModel):
    """Represents a complete move in backgammon, consisting of multiple checker moves."""
    checker_moves: List[CheckerMove] = Field(default_factory=list)
    dice: tuple[int, int] = Field(...)  # The dice roll that enables this move


class Game(BaseModel):
    """Represents a backgammon game with board state, players, and move history."""
    board: Board = Field(default_factory=Board)
    player1: Player = Field(default_factory=lambda: Player(name="Player 1", color=Color.DARK))
    player2: Player = Field(default_factory=lambda: Player(name="Player 2", color=Color.LIGHT))
    current_player: Player = Field(default=None)
    moves: dict[int, BackgammonMove] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)
