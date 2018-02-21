#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tdl

from misc import Singleton, Vector
from dungeon import Dungeon


class Colors:
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    WALL_DARK = (100, 100, 100)
    GROUND_DARK = (120, 120, 120)
    WALL_VISIBLE = (160, 160, 160)
    GROUND_VISIBLE = (190, 190, 190)


class DisplayManager(metaclass=Singleton):

    """
    Handles the display of entities and objects on the map.
    """
    # Constants
    # A lot of these are just hardcoded values for debugging purposes.
    # Ideally, they would be changeable by in-game settings.
    SCREEN_WIDTH = 80
    SCREEN_HEIGHT = 50
    MAP_WIDTH = 80
    MAP_HEIGHT = 44
    GAME_TITLE = "Tonzo Studios Roguelike"
    MAX_ROOMS = 30
    MIN_ROOM_SIZE = 6
    MAX_ROOM_SIZE = 10
    MAX_ENTITIES_PER_ROOM = 3
    FOV_ALGORITHM = "BASIC"
    FOV_LIGHT_WALLS = True
    FOV_RADIUS = 10

    tdl.set_font('lucida10x10_gs_tc.png', greyscale=True, altLayout=True)
    console = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
    root_console = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title=GAME_TITLE,
                            fullscreen=False)

    cur_map = None
    fov_recompute = True

    def gen_map(cls, player):
        game_map = Dungeon(cls.MAP_WIDTH, cls.MAP_HEIGHT)
        game_map.generate(
            cls.MAX_ROOMS, cls.MIN_ROOM_SIZE, cls.MAX_ROOM_SIZE,
            cls.MAX_ENTITIES_PER_ROOM, Colors, player
        )
        cls.cur_map = game_map
        cls.player = player

    def _recompute_fov(cls):
        if cls.fov_recompute:
            cls.cur_map.compute_fov(
                cls.player.pos, cls.FOV_ALGORITHM, cls.FOV_RADIUS,
                cls.FOV_LIGHT_WALLS
            )

    def _render_all(cls):
        # Draw map if necessary
        if cls.fov_recompute:
            for x in range(cls.cur_map.width):
                for y in range(cls.cur_map.height):
                    pos = Vector(x, y)
                    wall = not cls.cur_map.transparent[pos]

                    # If position is visible, draw a bright tile
                    if cls.cur_map.fov[pos]:
                        if wall:
                            cls.console.draw_char(
                                x, y, None, fg=None, bg=Colors.WALL_VISIBLE
                            )
                        else:
                            cls.console.draw_char(
                                x, y, None, fg=None, bg=Colors.GROUND_VISIBLE
                            )
                        # Tiles in FOV will be remembered after they get out
                        # of sight, out of mind :^)
                        cls.cur_map.explored[pos] = True

                    # Position is not visible, but has been explored before
                    elif cls.cur_map.explored[pos]:
                        if wall:
                            cls.console.draw_char(
                                x, y, None, fg=None, bg=Colors.WALL_DARK
                            )
                        else:
                            cls.console.draw_char(
                                x, y, None, fg=None, bg=Colors.GROUND_DARK
                            )

        # Draw visible entities
        for entity in cls.cur_map.entities:
            if cls.cur_map.fov[entity.pos]:
                cls.console.draw_char(
                    entity.pos.x, entity.pos.y, entity.char, entity.color,
                    bg=None
                )

        # Blit buffer to root console
        cls.root_console.blit(
            cls.console, 0, 0, cls.SCREEN_WIDTH, cls.SCREEN_HEIGHT, 0, 0
        )

    def _clear_all(cls):
        for entity in cls.cur_map.entities:
            cls.console.draw_char(
                entity.pos.x, entity.pos.y, ' ', entity.color, bg=None
            )

    def display(cls):
        cls._recompute_fov()
        cls._render_all()
        tdl.flush()
        cls._clear_all()
        cls.fov_recompute = False
