#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tdl
import pygame
import sys

from action_manager import ActionManager
from display_manager import DisplayManager
from dungeon import Dungeon
from entities import Actor
from misc import Colors, message
from registry import Registry, Actors


def main():
    # First of all, load the registry
    registry = Registry()

    # Initialize player, display_manager
    player = registry.player

    # Initialize Dungeon
    dungeon = Dungeon()
    dungeon.initialize(player, registry)

    # Initialize Display Manager
    display_manager = DisplayManager(player, dungeon)

    # Initialize Action Manager
    action_manager = ActionManager(player, dungeon, display_manager)

    clock = pygame.time.Clock()

    # Game loop
    while True:
        display_manager.refresh()
        # TODO: Add player and enemy turn states and cycle between both
        # Player turn
        # TODO: Use game states to handle turns

        action_manager.get_user_input()
        if not action_manager.handle_key_input():
            continue

        # Enemy turn
        for entity in dungeon.current_level.entities:
            entity.take_turn(player)

        # Check for player death
        # TODO: Handle player death as a game state
        if player.dead:
            # TODO: Show death screen
            print("You died!")
            return 0

        # Wait 60 frames before next loop iteration
        clock.tick(60)


if __name__ == "__main__":
    main()
