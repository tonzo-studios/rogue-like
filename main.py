#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tdl
from render import render_all, clear_all
from colors import colors
from user_input import handle_key_input
from entities import Character
from dungeon import Dungeon


def main():
    # Constants
    # A lot of these are just hardcoded values for debugging purposes. Ideally, they would
    # be changeable by in-game settings.
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

    # Initialize console
    tdl.set_font('lucida10x10_gs_tc.png', greyscale=True, altLayout=True)
    console = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)
    root_console = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title=GAME_TITLE, fullscreen=False)

    # Initialize player entity
    # FIXME: Character is an abstract class
    player = Character("Player", None, '@', colors.get('white'), None)

    # Initialize map
    game_map = Dungeon(MAP_WIDTH, MAP_HEIGHT)
    game_map.generate(MAX_ROOMS, MIN_ROOM_SIZE, MAX_ROOM_SIZE, MAX_ENTITIES_PER_ROOM,
                      colors, player)
    game_map.entities.append(player)

    fov_recompute = True

    # Game loop
    while not tdl.event.is_window_closed():
        # Compute FOV if necessary
        if fov_recompute:
            game_map.compute_fov(player.pos, fov=FOV_ALGORITHM, radius=FOV_RADIUS,
                                 light_walls=FOV_LIGHT_WALLS)

        # Draw to the screen
        render_all(console, game_map, fov_recompute, root_console, SCREEN_WIDTH,
                   SCREEN_HEIGHT, colors)
        tdl.flush()
        clear_all(console, game_map)

        fov_recompute = False

        # TODO: Add player and enemy turn states and cycle between both
        # Player turn
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
            if game_map.walkable[dest_pos]:
                target = game_map.get_blocking_entity_at_location(dest_pos)
                if target:
                    # Player is moving towards an enemy. Attack it!
                    # TODO: Implement combat
                    pass
                else:
                    player.move(direction)
                    fov_recompute = True

        if exit:
            return True

        if fullscreen:
            tdl.set_fullscreen(not tdl.get_fullscreen())


if __name__ == "__main__":
    main()
