import secrets

from collections import defaultdict
from enum import StrEnum
from typing import Tuple


def roll() -> Tuple[int, int]:
    return secrets.randbelow(6) + 1, secrets.randbelow(6) + 1


class Checker(StrEnum):
    BLACK = "b"
    WHITE = "w"

    def __str__(self) -> str:
        return self.value


class Board:
    position: dict[int, list[Checker]]
    bar1: list[Checker]
    off1: list[Checker]
    bar2: list[Checker]
    off2: list[Checker]
    main_direction: Checker

    def __init__(self):
        self.position = self.initial_position
        self.bar1 = []
        self.off1 = []
        self.bar2 = []
        self.off2 = []
        self.main_direction = Checker.WHITE

    @property
    def initial_position(self) -> dict[int, list[Checker]]:
        initial_board = defaultdict(list)
        initial_board[1] = [
            Checker.BLACK,
            Checker.BLACK,
        ]
        initial_board[6] = [
            Checker.WHITE,
            Checker.WHITE,
            Checker.WHITE,
            Checker.WHITE,
            Checker.WHITE,
        ]
        initial_board[8] = [
            Checker.WHITE,
            Checker.WHITE,
            Checker.WHITE,
        ]
        initial_board[12] = [
            Checker.BLACK,
            Checker.BLACK,
            Checker.BLACK,
            Checker.BLACK,
            Checker.BLACK,
        ]
        initial_board[13] = [
            Checker.WHITE,
            Checker.WHITE,
            Checker.WHITE,
            Checker.WHITE,
            Checker.WHITE,
        ]
        initial_board[17] = [
            Checker.BLACK,
            Checker.BLACK,
            Checker.BLACK,
        ]
        initial_board[19] = [
            Checker.BLACK,
            Checker.BLACK,
            Checker.BLACK,
            Checker.BLACK,
            Checker.BLACK,
        ]
        initial_board[24] = [
            Checker.WHITE,
            Checker.WHITE,
        ]

        return initial_board

    def __str__(self) -> str:
        points = ""
        for i in range(1, 25):
            checkers = self.position.get(i, [])
            checkers_str = " ".join(str(checker) for checker in checkers)
            points += f"{i}: {checkers_str}\n"
        return (
            f"{points}\n"
            f"Bar 1: {self.bar1}\n"
            f"Off 1: {self.off1}\n"
            f"Bar 2: {self.bar2}\n"
            f"Off 2: {self.off2}"
        )


class Player:
    name: str
    color: str


class Move:
    checker: Checker
    from_position: int
    to_position: int


class Game:
    board: Board
    player1: Player
    player2: Player
    current_player: Player
    moves: dict[int, Move]

    def __init__(self, player1: Player, player2: Player):
        self.board = Board()
        self.player1 = player1
        self.player2 = player2
        self.current_player = player1
        self.board.position = self.board.initial_position

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
