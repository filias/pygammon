from enum import StrEnum

from pygammon.logic.models import Position, Checker, Board, Color


class WinType(StrEnum):
    SINGLE = "single"        # 1x cube value
    GAMMON = "gammon"         # 2x cube value
    BACKGAMMON = "backgammon" # 3x cube value

initial_position = Position(
    {
        1: [Checker.LIGHT, Checker.LIGHT],
        2: [],
        3: [],
        4: [],
        5: [],
        6: [Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK],
        7: [],
        8: [Checker.DARK, Checker.DARK, Checker.DARK],
        9: [],
        10: [],
        11: [],
        12: [Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT],
        13: [Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK, Checker.DARK],
        14: [],
        15: [],
        16: [],
        17: [Checker.LIGHT, Checker.LIGHT, Checker.LIGHT],
        18: [],
        19: [Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT, Checker.LIGHT],
        20: [],
        21: [],
        22: [],
        23: [],
        24: [Checker.DARK, Checker.DARK],
    }
)


def has_winner(board: Board) -> Color | None:
    if len(board.off_dark) == 15:
        return Color.DARK
    if len(board.off_light) == 15:
        return Color.LIGHT

    return None


def get_win_type(board: Board, loser: Color) -> WinType:
    """Determine if the win is single, gammon, or backgammon."""
    loser_off = board.off_dark if loser == Color.DARK else board.off_light
    if loser_off:
        return WinType.SINGLE  # Loser has borne off at least one checker

    # Gammon: loser hasn't borne off any checkers
    # Check for backgammon: loser still has checkers on bar or in winner's home
    loser_on_bar = any(c == loser for c in board.bar)
    if loser_on_bar:
        return WinType.BACKGAMMON

    # Check if loser has checkers in winner's home board
    winner_home = range(19, 25) if loser == Color.LIGHT else range(1, 7)
    for p in winner_home:
        checkers = board.position.get(p, [])
        if checkers and checkers[0] == loser:
            return WinType.BACKGAMMON

    return WinType.GAMMON
