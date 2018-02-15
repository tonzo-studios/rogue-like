#!/usr/bin/env python
# -*- coding: utf-8 -*-


from misc import Vector


def render_all(console, game_map, fov_recompute, root_console, screen_width,
               screen_height, colors):
    """Render all visible and explored tiles, and all visible entities to screen."""
    # Draw map if necessary
    if fov_recompute:
        for x in range(game_map.width):
            for y in range(game_map.height):
                pos = Vector(x, y)
                wall = not game_map.transparent[pos]

                # If position is visible, draw a bright tile
                if game_map.fov[pos]:
                    if wall:
                        console.draw_char(x, y, None, fg=None, bg=colors.get('wall_visible'))
                    else:
                        console.draw_char(x, y, None, fg=None, bg=colors.get('ground_visible'))
                    # Tiles in FOV will be remembered after they get out of sight
                    game_map.explored[pos] = True

                # Position is not visible, but has been explored before
                elif game_map.explored[pos]:
                    if wall:
                        console.draw_char(x, y, None, fg=None, bg=colors.get('wall_dark'))
                    else:
                        console.draw_char(x, y, None, fg=None, bg=colors.get('ground_dark'))

    # Draw visible entities
    for entity in game_map.entities:
        if game_map.fov[entity.pos]:
            entity.draw(console)

    # Blit buffer to root console
    root_console.blit(console, 0, 0, screen_width, screen_height, 0, 0)


def clear_all(console, game_map):
    """Clear all entities from the console."""
    for entity in game_map.entities:
        entity.clear(console)
