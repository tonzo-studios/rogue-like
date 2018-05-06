#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tdl

from misc import Singleton, Vector


class ActionManager(metaclass=Singleton):
    """
    Handles user input and the requests it produces in the form of actions.

    This class is a Singleton, and as such can be called from anywhere, its
    members and functions/methods can be accessed from anywhere.

    Args:
        player (Actor): A reference to the player actor.
        dungeon (Dungeon): A reference to the game's dungeon.
        display_manager (DisplayManager): A reference to the game's display manager.
            It is needed because some player actions may trigger a FOV recompute.
        user_input (tdl.event.KeyDown): An Event object from the tdl library
            that contains information about the type and nature of the event.

    """

    player = dungeon = user_input = display_manager = None

    def __init__(cls, player, dungeon):
        cls.player = player
        cls.dungeon = dungeon

    def get_user_input(cls):
        """
        Detect and register user input.
        """
        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                cls.user_input = event
                return
        else:
            cls.user_input = None

    def handle_key_input(cls):
        """
        Use tdl's user input features to react to keyborad input.

        Returns:
            True if an action that consumes a turn was performed by the player, False otherwise.
        """
        if not cls.user_input:
            return False

        key_char = cls.user_input.char

        move_direction = None
        # Vertical and horizontal movement
        if cls.user_input.key == 'UP' or key_char == 'k':
            move_direction = Vector(0, -1)
        elif cls.user_input.key == 'DOWN' or key_char == 'j':
            move_direction = Vector(0, 1)
        elif cls.user_input.key == 'LEFT' or key_char == 'h':
            move_direction = Vector(-1, 0)
        elif cls.user_input.key == 'RIGHT' or key_char == 'l':
            move_direction = Vector(1, 0)

        # Diagonal movement
        elif key_char == 'y':
            move_direction = Vector(-1, -1)
        elif key_char == 'u':
            move_direction = Vector(1, -1)
        elif key_char == 'b':
            move_direction = Vector(-1, 1)
        elif key_char == 'n':
            move_direction = Vector(1, 1)

        # Check if the action is a movement action
        if move_direction is not None:
            return cls.movement_action(move_direction)

        if cls.user_input.key == 'ENTER' and cls.user_input.alt:
            # Alt+Enter: toggle fullscreen
            tdl.set_fullscreen(not tdl.get_fullscreen())
            return False

        elif cls.user_input.key == 'ESCAPE':
            # Exit game
            # TODO: Find more elegant way to terminate the program
            exit()

        elif cls.user_input.char == 'g':
            return cls.pickup_action()

        else:
            return False

    def movement_action(cls, move_direction):
        """
        Player tries to perform a movement action in the given direction.
        If the tile he's moving to is unoccupied, he will move to it.
        If it's occupied by another actor, the player will attack it instead.

        Args:
            move_direction (Vector): Direction the player is moving to. Should be a unit vector representing a
                horizontal, vertical or diagonal direction.

        Returns:
            True, since movement and attack actions always consume a turn.
        """
        dest_pos = cls.player.pos + move_direction
        if cls.dungeon.current_level.walkable[dest_pos]:
            target = cls.dungeon.current_level.get_blocking_entity_at_location(dest_pos)
            # If the player is moving towards an enemy, attack it
            if target:
                cls.player.attack(target)
            else:
                cls.player.move(move_direction)
                # Player moved, recompute FOV
                cls.dungeon.recompute_fov()
        return True

    def pickup_action(cls):
        """
        The player attempts to grab an item at the position he's currently at.
        If successful, the loot will be added to the player's backpack.

        Returns:
            True if the player picked something up, False otherwise.
        """
        loot = [e for e in cls.dungeon.current_level.entities if e.pos == cls.player.pos and e.type == 'item']

        if loot:
            cls.player.backpack.add(loot[0], 1)
            cls.dungeon.current_level.entities.remove(loot[0])
            return True
        return False
