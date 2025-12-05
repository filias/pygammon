from pydantic import BaseModel, Field
from enum import StrEnum
from typing import Annotated


class Color(StrEnum):
    DARK = "dark"
    LIGHT = "light"

Checker = Annotated[Color, Field(alias="checker")]
Point = Annotated[int, Field(ge=1, le=24)]
Position = Annotated[dict[Point, list[Checker]], ...]


class Board:
    position: Position
    bar: list[Checker]
    off: list[Checker]
    main_direction: Checker

    class Config:
        arbitrary_types_allowed = True

    def __init__(self):
        self.position = self.initial_position
        self.bar = []
        self.off_dark = []
        self.off_light = []
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
    checker: Checker
    from_position: int
    to_position: int
