from pygammon.logic.models import Player, Color
from pygammon.logic.position import initial_position
from pygammon.logic.move import select_checker_to_play

light = Player(name="L", color=Color.LIGHT)
dark = Player(name="D", color=Color.DARK)

print("LIGHT should pick point 1:", select_checker_to_play(light, initial_position))
print("DARK should pick point 24:", select_checker_to_play(dark, initial_position))

