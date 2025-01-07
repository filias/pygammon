from pydantic import PositiveInt
from pydantic_settings import BaseSettings


class PygammonConfig(BaseSettings):
    # Board settings
    board_width: PositiveInt = 800
    board_height: float = board_width * 10 / 14  # Calculated this with a square paper and based on a real board
    point_width: float = board_width / 14  # 12 points + gutters
    point_height: float = point_width * 4
    checker_radius: float = point_width * 0.4

    # Colors
    # Hex colors for the board, triangles, and checkers
    # TODO: make a type for this using Annotated
    color_dark_triangle: str = "#3662cb"
    color_light_triangle: str = "#618dd6"
    color_board: str = "#3e72d8"
    color_dark_checker: str = "#2e2da2"
    color_light_checker: str ="#d2d8f2"


settings = PygammonConfig()
