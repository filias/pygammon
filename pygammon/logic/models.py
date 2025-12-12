from pydantic import BaseModel, Field, ConfigDict
from enum import StrEnum
from typing import Annotated, List


class Color(StrEnum):
    DARK = "dark"
    LIGHT = "light"

Checker = Annotated[Color, Field(alias="checker")]
Point = Annotated[int, Field(ge=1, le=24)]
Position = Annotated[dict[Point, list[Checker]], ...]


class Board:
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
    name: str
    color: Color


class Move(BaseModel):
    checker1_from: Point
    checker1_to: Point
    checker2_from: Point
    checker2_to: Point
    # can be 4 checkers to move when we roll a double
    checker3_from: Point | None = None
    checker3_to: Point | None = None
    checker4_from: Point | None = None
    checker4_to: Point | None = None


class Game(BaseModel):
    board: Board = Field(default_factory=Board)
    player1: Player = Field(default_factory=lambda: Player(name="Player 1", color=Color.DARK))
    player2: Player = Field(default_factory=lambda: Player(name="Player 2", color=Color.LIGHT))
    current_player: Player = Field(default=None)
    moves: dict[int, Move] = Field(default_factory=dict)

    model_config = ConfigDict(arbitrary_types_allowed=True)
