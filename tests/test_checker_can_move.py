from pygammon.logic.models import Player, Color
from pygammon.logic.position import initial_position
from pygammon.logic.move import checker_can_move

light = Player(name="L", color=Color.LIGHT)
dark = Player(name="D", color=Color.DARK)

# Scenario 1: LIGHT from 1 with die 3 -> target 4 (initial_position shows 4 empty)
print("LIGHT 1 +3 ->", checker_can_move(1, 3, light, initial_position))

# Scenario 2: DARK from 24 with die 2 -> target 22 (initial_position shows 22 empty)
print("DARK 24 -2 ->", checker_can_move(24, 2, dark, initial_position))

# Scenario 3: an occupied target with one opponent (hit scenario)
# We'll place a temporary single opponent checker at point 10
pos = dict(initial_position)               # shallow copy
pos[10] = [Color.LIGHT] if dark.color == Color.DARK else [Color.DARK]
print("DARK hitting single opponent at 10 from 12 by 2 ->", checker_can_move(12, 2, dark, pos))

# Scenario 4: blocked by two opponent checkers
pos2 = dict(initial_position)
pos2[11] = [Color.LIGHT, Color.LIGHT]
print("LIGHT blocked at 9 -> 11 by two opponents ->", checker_can_move(9, 2, light, pos2))
