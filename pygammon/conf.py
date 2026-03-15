from typing import Annotated
from pydantic import PositiveInt, Field
from pydantic_settings import BaseSettings

# Hexcolor defined outside the class to avoid being considered a field
HexColor = Annotated[str, Field(pattern=r"^#[0-9A-Fa-f]{6}$")]


class PygammonConfig(BaseSettings):
    # Board settings
    panel_width: float = 100
    board_width: PositiveInt = 900
    board_height: float = (board_width - panel_width) / 1.6  # Golden ratio
    bar_width: float = 50
    tray_width: float = 70
    playing_width: float = board_width - panel_width
    point_width: float = (playing_width - bar_width - tray_width) / 12
    point_height: float = point_width * 4
    checker_radius: float = point_width * 0.4
    die_size: float = point_width * 0.75

    # Colors
    color_dark_triangle: HexColor = "#3662cb"
    color_light_triangle: HexColor = "#618dd6"
    color_board: HexColor = "#3e72d8"
    color_bar: HexColor = "#1e3a6e"
    color_tray: HexColor = "#2a4a80"
    color_panel: HexColor = "#1a2a50"
    color_panel_text: HexColor = "#ffffff"
    color_dark_checker: HexColor = "#2e2da2"
    color_light_checker: HexColor = "#d2d8f2"
    color_highlight_source: HexColor = "#ffff00"
    color_highlight_dest: HexColor = "#00ff00"
    color_selected: HexColor = "#ff8800"
    color_die_bg: HexColor = "#f5f0e1"
    color_die_pip: HexColor = "#1a1a1a"
    color_cube: HexColor = "#f5f0e1"
    color_cube_text: HexColor = "#1a1a1a"
    cube_size: float = bar_width * 0.7


settings = PygammonConfig()
