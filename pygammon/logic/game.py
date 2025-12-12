from pydantic import BaseModel, Field
from pygammon.logic.models import Board, Player, Move, Color


class Game(BaseModel):
    board: Board = Field(default_factory=Board)
    player1: Player = Field(default_factory=lambda: Player(name="Player 1", color=Color.DARK))
    player2: Player = Field(default_factory=lambda: Player(name="Player 2", color=Color.LIGHT))
    current_player: Player = Field(default=None)
    moves: dict[int, Move] = Field(default_factory=dict)

    class Config:
        arbitrary_types_allowed = True

    def __post_init__(self):
        self.current_player = self.player1  # Set the current player after initialization

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
