import secrets

from pydantic import BaseModel, Field, ConfigDict, model_validator
from enum import StrEnum
from typing import Annotated, List, Self


class Color(StrEnum):
    """Represents the two player colors in backgammon."""

    DARK = "dark"
    LIGHT = "light"


class Direction(StrEnum):
    """Represents the direction a player moves on the board."""

    INCREASING = "increasing"  # 1 → 24 (bar=0, bear_off=25)
    DECREASING = "decreasing"  # 24 → 1 (bar=25, bear_off=0)


class Die(BaseModel):
    """Represents a single die with a value between 1 and 6."""

    value: int = Field(..., ge=1, le=6)

    def roll(self) -> int:
        """Roll the die and return the new value."""
        self.value = secrets.randbelow(6) + 1
        return self.value


Checker = Annotated[Color, Field(alias="checker")]

BAR_INCREASING = 0
BEAR_OFF_INCREASING = 25
BAR_DECREASING = 25
BEAR_OFF_DECREASING = 0
Point = Annotated[int, Field(ge=0, le=25)]

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
            Point(6): [
                Checker.LIGHT,
                Checker.LIGHT,
                Checker.LIGHT,
                Checker.LIGHT,
                Checker.LIGHT,
            ],
            Point(8): [Checker.LIGHT, Checker.LIGHT, Checker.LIGHT],
            Point(12): [
                Checker.DARK,
                Checker.DARK,
                Checker.DARK,
                Checker.DARK,
                Checker.DARK,
            ],
            Point(13): [
                Checker.LIGHT,
                Checker.LIGHT,
                Checker.LIGHT,
                Checker.LIGHT,
                Checker.LIGHT,
            ],
            Point(17): [Checker.DARK, Checker.DARK, Checker.DARK],
            Point(19): [
                Checker.DARK,
                Checker.DARK,
                Checker.DARK,
                Checker.DARK,
                Checker.DARK,
            ],
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
    """Represents a player with a name, color, and movement direction."""

    name: str
    color: Color
    direction: Direction

    @property
    def bar(self) -> int:
        """Returns the bar point for this player's direction."""
        return (
            BAR_INCREASING if self.direction == Direction.INCREASING else BAR_DECREASING
        )

    @property
    def bear_off(self) -> int:
        """Returns the bear off point for this player's direction."""
        return (
            BEAR_OFF_INCREASING
            if self.direction == Direction.INCREASING
            else BEAR_OFF_DECREASING
        )

    @property
    def home_range(self) -> range:
        """Returns the home board range for this player."""
        return range(19, 25) if self.direction == Direction.INCREASING else range(1, 7)


class CheckerMove(BaseModel):
    """Represents a single checker move in backgammon."""

    from_point: Point
    to_point: Point
    die_value: int = Field(..., ge=1, le=6)

    @model_validator(mode="after")
    def check_valid_move(self) -> Self:
        if abs(self.from_point - self.to_point) != self.die_value:
            raise ValueError("Invalid move")
        return self


class BackgammonMove(BaseModel):
    """Represents a complete move in backgammon, consisting of multiple checker moves."""

    checker_moves: List[CheckerMove] = Field(default_factory=list)
    dice: tuple[int, int] = Field(...)  # The dice roll that enables this move

    @model_validator(mode="after")  # Pydantic, depois da jogada ter sido iniciada
    def validate(self) -> Self:
        if self.dice[0] == self.dice[1] and len(self.checker_moves) != 4:
            raise ValueError("With double 4 moves are needed")
        if self.dice[0] != self.dice[1] and len(self.checker_moves) != 2:
            raise ValueError("only 2 moves allowed")
        return self


class Game(BaseModel):
    """Represents a backgammon game with board state, players, and move history."""

    board: Board = Field(default_factory=Board)
    player1: Player = Field(
        default_factory=lambda: Player(
            name="Player 1", color=Color.DARK, direction=Direction.DECREASING
        )
    )
    player2: Player = Field(
        default_factory=lambda: Player(
            name="Player 2", color=Color.LIGHT, direction=Direction.INCREASING
        )
    )
    current_player: Player = Field(default=None)
    moves: dict[int, BackgammonMove] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)
