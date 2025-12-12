# test_move_checker.py
import copy
from pygammon.logic.models import Player, Color
from pygammon.logic.position import initial_position
from pygammon.logic.move import checker_can_move, move_checker

light = Player(name="L", color=Color.LIGHT)
dark = Player(name="D", color=Color.DARK)

# Scenario A: normal move LIGHT from 1 by 3 -> to 4 (empty)
pos1 = copy.deepcopy(initial_position)
print("Initial pos snapshot (1):", pos1.get(4), pos1.get(9), pos1.get(10), pos1.get(11))

ok, target = checker_can_move(1, 3, light, pos1)
print("Scenario A can_move:", ok, target)
res = move_checker(1, target, light, pos1)
print("Scenario A move result (opponent, borne_off):", res)
print("After move: pos1[4] =", pos1.get(4))

# Scenario B: hit move (ensure Dark has a checker at 12 to move)
pos2 = copy.deepcopy(initial_position)
pos2[10] = [Color.LIGHT]   # single opponent to be hit
pos2[12] = [Color.DARK]    # ensure Dark has a checker at 12 to move
print("\nBefore hit: pos2[12] =", pos2.get(12), " pos2[10] =", pos2.get(10))
ok, target = checker_can_move(12, 2, dark, pos2)
print("Scenario B can_move:", ok, target)
res = move_checker(12, target, dark, pos2)
print("Scenario B move result (opponent, borne_off):", res)
print("After hit: pos2[12] =", pos2.get(12), " pos2[10] =", pos2.get(10))

# Scenario C: borne-off (simple)
pos3 = copy.deepcopy(initial_position)
pos3[23] = [Color.LIGHT]   # put a light checker near the end
ok, target = checker_can_move(23, 2, light, pos3)
print("\nScenario C can_move:", ok, target)
res = move_checker(23, target, light, pos3)
print("Scenario C move result (opponent, borne_off):", res)
print("After borne-off pos3[23] =", pos3.get(23))
