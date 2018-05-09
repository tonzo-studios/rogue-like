#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tdl

from action_manager import ActionManager
from behavior import NullBehavior
from display_manager import DisplayManager
from dungeon import Dungeon
from entities import Actor
from misc import Colors, message
from registry import Registry, Actors


def main():
    # First of all, load the registry
    registry = Registry()

    # Initialize player, display_manager
    player = Actor(Actors.HERO, "Player", NullBehavior(), '@', Colors.WHITE, registry=registry)
    # XXX: Give player level boost for testing purposes
    player.level = 10

    # Initialize Dungeon
    dungeon = Dungeon()
    dungeon.initialize(player, registry)

    # Initialize Display Manager
    display_manager = DisplayManager(player, dungeon)
    message("Hello world!", Colors.RED)

    # Initialize Action Manager
    action_manager = ActionManager(player, dungeon)

    # Game loop
    while not tdl.event.is_window_closed():
        display_manager.refresh()
        # TODO: Add player and enemy turn states and cycle between both
        # Player turn
        # TODO: Use game states to handle turns

        action_manager.get_user_input()
        if action_manager.handle_key_input() is False:
            continue

        # Enemy turn
        for entity in dungeon.current_level.entities:
            entity.behavior.take_turn(entity, player)

        # Check for player death
        # TODO: Handle player death as a game state
        if player.dead:
            # TODO: Show death screen
            print("You died!")
            return 0


if __name__ == "__main__":
    main()
