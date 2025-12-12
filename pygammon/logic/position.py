from pygammon.logic.models import Position, Checker, Board, Player, Color

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
