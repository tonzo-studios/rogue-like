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


def main_pygame():
    # init
    pygame.init()
    pygame.display.set_caption("Project Sea")
    screen = pygame.display.set_mode((240, 180))

    cur_pos = (50, 50)
    delta = 16

    # main loop
    while True:
        # event handling
            screen.fill((0, 0, 0))
            screen.blit(player_sprite, cur_pos)
            pygame.display.flip()


def main():
    # First of all, load the registry
    registry = Registry()

    # Initialize player, display_manager
    player = Actor(Actors.HERO, "Player", "sprites/potatohead.png", Colors.WHITE, behavior=None, registry=registry)
    # XXX: Give player level boost for testing purposes
    player.level = 10

    # Initialize Dungeon
    dungeon = Dungeon()
    dungeon.initialize(player, registry)

    # Initialize Display Manager
    display_manager = DisplayManager(player, dungeon)

    # Initialize Action Manager
    action_manager = ActionManager(player, dungeon)

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

        clock.tick(60)


if __name__ == "__main__":
    if sys.argv[:1] == 'pygame':
        main_pygame()
    else:
        main()
