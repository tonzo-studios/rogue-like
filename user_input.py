#!/usr/bin/env python
# -*- coding: utf-8 -*-


from misc import Vector


def handle_key_input(user_input):
    """Use tdl's user input features to react to keyborad input.

    Returns a dictionary containing an action key and a value to be parsed by the game logic.
    """
    key_char = user_input.char

    # Vertical and horizontal movement
    if user_input.key == 'UP' or key_char == 'k':
        return {'move': Vector(0, -1)}
    elif user_input.key == 'DOWN' or key_char == 'j':
        return {'move': Vector(0, 1)}
    elif user_input.key == 'LEFT' or key_char == 'h':
        return {'move': Vector(-1, 0)}
    elif user_input.key == 'RIGHT' or key_char == 'l':
        return {'move': Vector(1, 0)}

    # Diagonal movement
    elif key_char == 'y':
        return {'move': Vector(-1, -1)}
    elif key_char == 'u':
        return {'move': Vector(1, -1)}
    elif key_char == 'b':
        return {'move': Vector(-1, 1)}
    elif key_char == 'n':
        return {'move': Vector(1, 1)}

    if user_input.key == 'ENTER' and user_input.alt:
        # Alt+Enter: toggle fullscreen
        return {'fullscreen': True}

    elif user_input.key == 'ESCAPE':
        # Exit game
        return {'exit': True}

    else:
        return {}
