from pygammon.logic.dice import Die
from pygammon.logic.models import Player, Position, Point


def select_checker_to_play(player: Player, position: Position) -> Point:
    # TODO: the numbers of the points change from player to player, think about how to do that
    # Chose the checker more far away
    for point, checkers in reversed(position.items()):
        print(f"{point}: {checkers}")
        if checkers != []:
            if checkers[0] == player.color:
                print(f"Checker color: {checkers[0]}, Player color: {player.color}")
                return point


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

