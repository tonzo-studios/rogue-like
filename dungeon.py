#!/usr/bin/env python
# -*- coding: utf-8 -*-

from level import Level
from misc import Singleton


class DungeonException(Exception):
    pass


class Dungeon(metaclass=Singleton):
    """
    The dungeon is the collection of levels in the game. Initially, the dungeon is empty, and new levels are generated
    as the player moves deeper into the dungeon.
    """
    # TODO: Put constants somewhere else
    FOV_ALGORITHM = "BASIC"
    FOV_LIGHT_WALLS = True
    # TODO: These variables could be theme-dependant, and encapsulated into a context
    LEVEL_WIDTH = 80
    LEVEL_HEIGHT = 44
    MAX_ROOMS = 30
    MIN_ROOM_SIZE = 6
    MAX_ROOM_SIZE = 10
    MAX_ENTITIES_PER_ROOM = 3
    FOV_RADIUS = 10

    levels = []
    _cur_level = -1
    player = None
    registry = None
    fov_recomputed = True

    @property
    def current_level(cls):
        """
        Return the current level the player is at.

        Raises:
            DungeonException: If the dungeon hasn't been initialized yet.
        """
        if not cls.levels:
            raise DungeonException("Dungeon hasn't been initialized yet.")
        return cls.levels[cls._cur_level]

    @property
    def current_level_number(cls):
        """
        Return the index of the current level, starting from 1.

        Raises:
            DungeonException: If the dungeon hasn't been initialized yet.
        """
        if cls._cur_level == -1:
            raise DungeonException("Dungeon hasn't been initialized yet.")
        return cls._cur_level + 1

    def initialize(cls, player, registry):
        """
        Gets the reference to the player object and generates the first level of the dungeon.

        Args:
            player (Actor): Reference to the player object.

        Raises:
            DungeonException: If the dungeon has already been initialized
        """
        if cls.levels:
            # Dungeon has already been initialized
            raise DungeonException("Dungeon has already been initialized.")
        cls.player = player
        cls.registry = registry
        cls.go_to_next_level()

    def clear(cls):
        """
        Removes all levels from the dungeon and the player reference. Useful when resetting the game after a death.
        """
        cls.levels = []
        cls._cur_level = -1
        cls.player = None

    def go_to_next_level(cls):
        """
        Moves the player to the next level. If it's the first time the level is visited,
        it generates it and adds it to the level list.
        """
        cls._cur_level += 1

        if len(cls.levels) < cls.current_level_number:
            # New depth reached, generate new level
            # TODO: Use context instead of constants, see Level
            level = Level(cls.LEVEL_WIDTH, cls.LEVEL_HEIGHT, cls.MAX_ROOMS, cls.MIN_ROOM_SIZE, cls.MAX_ROOM_SIZE,
                          cls.MAX_ENTITIES_PER_ROOM, cls.registry)
            cls.levels.append(level)
        # Place player on the level
        cls.player.place(cls.current_level, cls.current_level.up_stairs)
        # Changing levels triggers a FOV recomputation
        cls.recompute_fov()

    def go_to_previous_level(cls):
        """
        Moves the player to the previous level.

        Raises:
            DungeonException: If the player is at the top of the dungeon, since there is no previous level.
        """
        if cls._cur_level <= 0:
            raise DungeonException("Already at the top level.")
        cls._cur_level -= 1
        # Place player on the level
        cls.player.place(cls.current_level, cls.current_level.down_stairs)
        # Changing levels triggers a FOV recomputation
        cls.recompute_fov()

    def recompute_fov(cls):
        """
        Triggers a recomputation of the FOV at the player's position for the current level.

        Raises:
            DungeonException: If the dungeon hasn't been initialized yet.
        """
        if not cls.levels:
            raise DungeonException("Dungeon hasn't been initialized yet.")

        cls.current_level.compute_fov(
            cls.player.pos, cls.FOV_ALGORITHM, cls.FOV_RADIUS,
            cls.FOV_LIGHT_WALLS
        )
        cls.fov_recomputed = True
