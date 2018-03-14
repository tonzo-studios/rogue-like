#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tdl
from action_manager import ActionManager
from display_manager import DisplayManager
from entities import Actor
from behavior import NullBehavior
from misc import Vector, Colors, message


def main():
    # Initialize player, display_manager
    player = Actor("Player", Vector(0, 0), NullBehavior(), '@', Colors.WHITE)
    # XXX: Give player level boost for testing purposes
    player.level = 10

    # Initialize Display Manager
    display_manager = DisplayManager()
    display_manager.gen_map(player)
    display_manager.cur_map.entities.append(player)
    message("Hello world!", Colors.RED)

    # Initialize Action Manager
    action_manager = ActionManager()
    action_manager.player = player
    action_manager.display_manager = display_manager
    action_manager.update(display_manager.cur_map)

    # Game loop
    while not tdl.event.is_window_closed():
        display_manager.refresh()
        # TODO: Add player and enemy turn states and cycle between both
        # Player turn
        # TODO: Use game states to handle turns

        action_manager.get_user_input()
        action = action_manager.handle_key_input()

        if not action:
            continue

        action.execute()

        # Enemy turn
        for entity in display_manager.cur_map.entities:
            entity.take_turn(player, display_manager.cur_map)

        # Check for player death
        # TODO: Handle player death as a game state
        if player.dead:
            # TODO: Show death screen
            print("You died!")
            return 0


if __name__ == "__main__":
    main()
