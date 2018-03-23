#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tdl
import command as cmd
from misc import Singleton, Vector


class ActionManager(metaclass=Singleton):

    """
    Handles user input and the requests it produces in the form of actions.

    This class is a Singleton, and as such can be called from anywhere, its
    members and functions/methods can be accessed from anywhere.

    Args:
        player (Actor): A reference to the player actor.
        game_map (Dungeon): A reference to the current map.
        display_manager (DisplayManager): A reference to the game's display manager.
            It is needed because some player actions may trigger a FOV recompute.
        user_input (tdl.event.KeyDown): An Event object from the tdl library
            that contains information about the type and nature of the event.

    """

    player = game_map = user_input = display_manager = None

    # TODO: use observer pattern to call this when game map changes
    def update(cls, game_map):
        cls.game_map = game_map

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
            A command representing the action that the user is going to
            perform, or False if there was no valid input.
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
            dest_pos = cls.player.pos + move_direction
            if cls.game_map.walkable[dest_pos]:
                target = cls.game_map.get_blocking_entity_at_location(dest_pos)
                # If the player is moving towards an enemy, attack it
                if target:
                    return cmd.AttackCommand(cls.player, target)
                else:
                    return cmd.MoveCommand(cls.player, move_direction, cls.display_manager)

        if cls.user_input.key == 'ENTER' and cls.user_input.alt:
            # Alt+Enter: toggle fullscreen
            return cmd.FullscreenCommand()

        elif cls.user_input.key == 'ESCAPE':
            # Exit game
            return cmd.ExitCommand()

        elif cls.user_input.char == 'g':
            # Pickup item
            return cmd.PickupCommand(cls.player, cls.display_manager.cur_map)

        else:
            return False
