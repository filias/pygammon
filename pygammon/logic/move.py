from pygammon.logic.dice import Die
from pygammon.logic.models import Player, Position, Point


def select_checker_to_play(player: Player, position: Position) -> Point:

    # TODO: the numbers of the points change from player to player, think about how to do that
    # Chose the checker more far away
    """
    Select the checker that is the farthest from the player's home.

    LIGHT player: moves from point 1 -> 24
    DARK player: moves from point 24 -> 1

    So:
    - LIGHT should check points in order: 1, 2, 3, ..., 24
    - DARK should check points in order: 24, 23, 22, ..., 1

    We return the first point that contains a checker of the player's color.
    """
    
    # Decide direction based on player color
    if player.color == "light":        # Color.LIGHT
        points_to_check = range(1, 25) # from 1 to 24
    else:                               # Color.DARK
        points_to_check = range(24, 0, -1) # from 24 down to 1
    
    # Look for the first point that has a checker of this player
    for point in points_to_check:
        checkers = position.get(point, [])#chave é ponto e valor lista peças = dicionário
        if checkers != []:#se lista de peças not empty
            if checkers[0] == player.color:#A primeira peça desta lista é da cor deste jogador?
                return point
    # If the player has no checkers on the board
    return None

def checker_can_move(from_point, die_value, player, position):
    """
    Return (True, target) if a checker on from_point can move by die_value.
    Return (False, None) when the destination is blocked.
    Beginner-friendly rules:
      - LIGHT: target = from_point + die_value
      - DARK:  target = from_point - die_value
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

def move_checker(from_point, to_point, player, position):
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
        opponent = dest.pop(0)   # remove opponent checker
        # place player's checker on top
        dest.insert(0, player.color)
        return opponent, False

    # otherwise just place player's checker on top
    dest.insert(0, player.color)
    return None, False

# def move(position: Position, dice: tuple[Die, Die], player: Player) -> Position:
#     # For each dice
#     for die in dice:
#         # Chose the checker more far away from the home
#         checker_to_play = select_checker_to_play()
#
#         # Confirm if the checker can move to the point
#         if checker_can_move(checker_to_play):
#             # Move the checker
#             move_checker(initial_point) -> final_point

