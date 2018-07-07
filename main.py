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

    player_sprite = pygame.image.load("sprites/potatohead.png")
    cur_pos = (50, 50)
    delta = 10

    # main loop
    while True:
        # event handling
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                break
            elif ev.type == pygame.KEYDOWN:
                if ev.key == pygame.K_LEFT:
                    # move left
                    cur_pos = (cur_pos[0] - delta, cur_pos[1])
                elif ev.key == pygame.K_RIGHT:
                    # move right
                    cur_pos = (cur_pos[0] + delta, cur_pos[1])
                elif ev.key == pygame.K_UP:
                    # move up
                    cur_pos = (cur_pos[0], cur_pos[1] - delta)
                elif ev.key == pygame.K_DOWN:
                    # move down
                    cur_pos = (cur_pos[0], cur_pos[1] + delta)
            screen.fill((0, 0, 0))
            screen.blit(player_sprite, cur_pos)
            pygame.display.flip()


def main():
    # First of all, load the registry
    registry = Registry()

    # Initialize player, display_manager
    player = Actor(Actors.HERO, "Player", '@', Colors.WHITE, behavior=None, registry=registry)
    # XXX: Give player level boost for testing purposes
    player.level = 10

    # Initialize Dungeon
    dungeon = Dungeon()
    dungeon.initialize(player, registry)

    # Initialize Display Manager
    display_manager = DisplayManager(player, dungeon)

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
            entity.take_turn(player)

        # Check for player death
        # TODO: Handle player death as a game state
        if player.dead:
            # TODO: Show death screen
            print("You died!")
            return 0


if __name__ == "__main__":
    if sys.argv[:1] == 'pygame':
        main_pygame()
    else:
        main()
