from pydantic import BaseModel, Field
from enum import StrEnum
from typing import Annotated


class Checker(StrEnum):
    DARK = "dark"
    LIGHT = "light"

    def __str__(self) -> str:
        return self.value


class Point(BaseModel):
    number: Annotated[int, Field(ge=1, le=24)]
    checkers: list[Checker]


class Board:
    position: list[Point]
    bar: list[Checker]
    off_dark: list[Checker.DARK]
    off_light: list[Checker.LIGHT]
    main_direction: Checker

    def __init__(self):
        self.position = self.initial_position
        self.bar = []
        self.off_dark = []
        self.off_light = []
        self.main_direction = Checker.DARK

    @property
    def initial_position(self) -> list[Point]:
        initial_board = [
            Point(number=1, checkers=[Checker.DARK, Checker.DARK]),
            Point(number=6, checkers=[Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT]),
            Point(number=8, checkers=[Checker.LIGHT, Checker.LIGHT, Checker.LIGHT]),
            Point(number=12, checkers=[Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK]),
            Point(number=13, checkers=[Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT]),
            Point(number=17, checkers=[Checker.DARK, Checker.DARK, Checker.DARK]),
            Point(number=19, checkers=[Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK]),
            Point(number=24, checkers=[Checker.LIGHT, Checker.LIGHT]),
        ]
        return initial_board

    def __str__(self) -> str:
        return (
            f"{self.position}\n"
            f"Bar 1: {self.bar}\n"
            f"Off 1: {self.off_dark}\n"
            f"Off 2: {self.off_light}"
        )


class Player(BaseModel):
    name: str
    color: str


class Move(BaseModel):
    checker: Checker
    from_position: int
    to_position: int


class Game(BaseModel):
    board: Board
    player1: Player
    player2: Player
    current_player: Player
    moves: dict[int, Move]

    def make_move(self, move: Move) -> Board:
        # TODO: logic for making a move
        return self.board

    def is_winner(self) -> Player | None:
        if self.board1.off == 15:
            return self.player1
        if self.board2.off == 15:
            return self.player2

        return None

    def toggle_player(self) -> None:
        self.current_player = (
            self.player1 if self.current_player == self.player2 else self.player2
        )
