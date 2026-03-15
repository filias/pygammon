from typing import List, Optional, Tuple

from pygammon.logic.models import Board, Color, Direction, Player, Position, Point


def select_checker_to_play(player: Player, position: Position) -> Optional[Point]:
    """
    Select the checker that is the farthest from the player's home.

    We return the first point that contains a checker of the player's color.
    """

    # Decide direction based on player color
    if player.color == "light":  # Color.LIGHT
        points_to_check = range(1, 25)  # from 1 to 24
    else:  # Color.DARK
        points_to_check = range(24, 0, -1)  # from 24 down to 1

    # Look for the first point that has a checker of this player
    for point in points_to_check:
        checkers = position.get(
            point, []
        )  # chave é ponto e valor lista peças = dicionário
        if checkers != []:  # se lista de peças not empty
            if (
                checkers[0] == player.color
            ):  # A primeira peça desta lista é da cor deste jogador?
                return point
    # If the player has no checkers on the board
    return None


def checker_can_move(
    from_point: Point, die_value: int, player: Player, position: Position
) -> Tuple[bool, Optional[Point]]:
    """
    Return (True, target) if a checker on from_point can move by die_value.
    Return (False, None) when the destination is blocked.
    Beginner-friendly rules:
      - INCREASING: target = from_point + die_value
      - DECREASING:  target = from_point - die_value
      - empty or same-color -> allowed
      - single opponent -> allowed (hit)
      - two or more opponent -> blocked
    """
    # compute target depending on player color
    if player.color == "light":
        target = from_point + die_value
    else:
        target = from_point - die_value

    # if target is outside 1..24, treat as allowed here (bear-off handled later)
    if target < 1 or target > 24:
        return True, target

    dest_checkers = position.get(target, [])

    # empty or same-color -> allowed
    if not dest_checkers or dest_checkers[0] == player.color:
        return True, target

    # single opponent -> allowed (hit)
    if len(dest_checkers) == 1:
        return True, target

    # two or more opponent checkers -> blocked
    return False, None


def move_checker(
    from_point: Point, to_point: Point, player: Player, position: Position
) -> Tuple[Optional[str], bool]:
    """
    Move a checker in the 'position' dict.
    Returns a tuple: (opponent_color_or_None, borne_off_bool)

    - Removes the player's top checker from from_point.
    - If to_point is within 1..24:
        - If destination has exactly 1 opponent -> remove it and return (opponent_color, False)
        - Else place player's checker on top and return (None, False)
    - If to_point outside 1..24 -> it's a borne-off; remove the checker and return (None, True)
    """
    # ensure there is a checker to move
    checkers_from = position.get(from_point, [])
    if not checkers_from or checkers_from[0] != player.color:
        raise ValueError(f"No {player.color} checker at point {from_point} to move")

    # remove the moving checker
    checkers_from.pop(0)

    # borne-off case
    if to_point < 1 or to_point > 24:
        # checker leaves the board
        return None, True

    # normal destination
    dest = position.setdefault(to_point, [])

    # if single opponent -> hit
    if dest and dest[0] != player.color and len(dest) == 1:
        opponent = dest.pop(0)  # remove opponent checker
        # place player's checker on top
        dest.insert(0, player.color)
        return opponent, False

    # otherwise just place player's checker on top
    dest.insert(0, player.color)
    return None, False


def all_checkers_in_home(player: Player, position: Position, bar: list) -> bool:
    """Check if all of a player's checkers are in their home board (or borne off)."""
    # If player has checkers on the bar, not all in home
    if any(c == player.color for c in bar):
        return False

    for point, checkers in position.items():
        if not checkers or checkers[0] != player.color:
            continue
        if point not in player.home_range:
            return False
    return True


def get_valid_moves(
    player: Player, position: Position, remaining_dice: List[int], bar: list
) -> List[Tuple[int, int, int]]:
    """
    Returns all legal (from_point, to_point, die_value) tuples for the current state.

    Enforces:
    - Bar-first rule: if player has checkers on bar, must enter them first
    - Bearing off: only when all checkers are in home board
    - Blocking: can't land on 2+ opponent checkers
    """
    moves = []
    unique_dice = set(remaining_dice)
    has_checker_on_bar = any(c == player.color for c in bar)

    for die_value in unique_dice:
        if has_checker_on_bar:
            # Must enter from bar first
            from_point = player.bar
            can_move, target = checker_can_move(from_point, die_value, player, position)
            if can_move and target is not None and 1 <= target <= 24:
                moves.append((from_point, target, die_value))
        else:
            # Normal moves from board points
            can_bear_off = all_checkers_in_home(player, position, bar)

            for point, checkers in position.items():
                if not checkers or checkers[0] != player.color:
                    continue
                if point < 1 or point > 24:
                    continue

                can_move, target = checker_can_move(point, die_value, player, position)
                if not can_move or target is None:
                    continue

                if 1 <= target <= 24:
                    moves.append((point, target, die_value))
                elif can_bear_off:
                    # Bearing off — exact or overshoot from highest point
                    if _is_valid_bear_off(point, die_value, player, position):
                        moves.append((point, player.bear_off, die_value))

    return moves


def _is_valid_bear_off(
    from_point: int, die_value: int, player: Player, position: Position
) -> bool:
    """
    Check if bearing off from this point with this die is valid.
    Exact rolls always work. Overshooting only works if no checker is
    farther from bearing off than from_point.
    """
    if player.direction == Direction.INCREASING:
        exact_target = from_point + die_value
        if exact_target == 25:
            return True  # Exact bear-off
        if exact_target > 25:
            # Only valid if no checker is on a lower point in home
            for p in range(19, from_point):
                if position.get(p, []) and position[p][0] == player.color:
                    return False
            return True
    else:
        exact_target = from_point - die_value
        if exact_target == 0:
            return True  # Exact bear-off
        if exact_target < 0:
            # Only valid if no checker is on a higher point in home
            for p in range(from_point + 1, 7):
                if position.get(p, []) and position[p][0] == player.color:
                    return False
            return True
    return False
