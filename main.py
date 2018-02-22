#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tdl
from user_input import handle_key_input
from display_manager import Colors, DisplayManager
from entities import Actor
from behavior import NullBehavior
from misc import Vector


def main():
    # Initialize player, display_manager
    player = Actor("Player", Vector(0, 0), NullBehavior(), '@', Colors.WHITE)
    # XXX: Give player level boost for testing purposes
    player.level = 10
    display_manager = DisplayManager()
    display_manager.gen_map(player)
    display_manager.cur_map.entities.append(player)

    # Game loop
    while not tdl.event.is_window_closed():
        display_manager.display()
        # TODO: Add player and enemy turn states and cycle between both
        # Player turn
        # TODO: Use game states to handle turns
        for event in tdl.event.get():
            if event.type == 'KEYDOWN':
                user_input = event
                break
        else:
            user_input = None

        if not user_input:
            continue

        action = handle_key_input(user_input)

        if not action:
            # Nothing to do
            continue

        # TODO: Encapsulate action manager
        direction = action.get('move')
        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        if direction:
            dest_pos = player.pos + direction
            if display_manager.cur_map.walkable[dest_pos]:
                target = display_manager.cur_map.get_blocking_entity_at_location(dest_pos)
                if target:
                    # Player is moving towards an enemy. Attack it!
                    player.attack(target)
                    pass
                else:
                    player.move(direction)
                    display_manager.fov_recompute = True

        if exit:
            return True

        if fullscreen:
            tdl.set_fullscreen(not tdl.get_fullscreen())

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
