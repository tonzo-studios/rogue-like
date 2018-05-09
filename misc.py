#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

from enum import Enum
from math import sqrt, atan2, pi


# Classes
class Singleton(type):
    """
    Singleton metaclass.

    Any class that specifies this class as its metaclass will become a Singleton,
    i.e. it will only be instantiated once during the lifetime of the program.

    This is useful for information that must be accessed project-wide without
    creating performance issues.
    """
    # from https://stackoverflow.com/q/6760685

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Vector:
    """
    Represents a vector in a 2D Euclidean space.

    Can be used to represent position, distance, direction, etc.
    Overrides the addition and subtraction operators to perform element-wise operations.

    Args:
        x (int): x coordinate of this Vector object.
        y (int): y coordinate of this Vector object.
    """

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        """Perform element-wise addition."""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Perform element-wise subtraction."""
        return Vector(self.x - other.x, self.y - other.y)

    def __repr__(self):
        """Represent the vector as a tuple."""
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        """Two vectors are equal if they have the same components."""
        return self.x == other.x and self.y == other.y

    @property
    def norm(self):
        """Return the norm of the vector."""
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        """Return a unitary vector with the same direction."""
        norm = self.norm
        return Vector(self.x / norm, self.y / norm)

    def snap_to_grid(self):
        """
        Returns a unitary vector after snapping the vector's direction to the closest tile in the grid using the
        8 possible directions: N, W, S, E, NW, SW, NE, SE.
        """
        angle = atan2(self.y, self.x)
        # Map octant index to unit vector, starting from E (0) and going counter-clockwise
        octant_to_direction = {
            0: Vector(1, 0),  # E
            1: Vector(1, 1),  # NE
            2: Vector(0, 1),  # N
            3: Vector(-1, 1),  # NW
            4: Vector(-1, 0),  # W
            5: Vector(-1, -1),  # SW
            6: Vector(0, -1),  # S
            7: Vector(1, -1)  # SE
        }
        # Find out which octant we're in
        octant = round(8 * angle / (2 * pi) + 8) % 8
        # Get direction using the octant to direction map
        return octant_to_direction[octant]


class Colors:
    """
    This class is an interface to colors as RGB tuples.

    This makes colors easily accessible and human-recognizable while being able
    to directly interface with tdl's functions which require colors as tuples
    (bar some pre-determined colors as strings).

    Note:
        If new colors must be used, it is best to add them to this class, do
        not hardcode tuples into the game logic.
        The only cases where not using this class can be understood are those
        which require the color to be generated at runtime.
    """

    def __init__(self):
        raise NotImplementedError("Colors is a static class, it cannot be instantiated")

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    WALL_DARK = (100, 100, 100)
    GROUND_DARK = (120, 120, 120)
    WALL_VISIBLE = (160, 160, 160)
    GROUND_VISIBLE = (190, 190, 190)


class RenderPriority(Enum):
    """
    An enum representing the rendering priority for entities.

    The greater the number assigned to each state, the greater the priority
    when rendering the given entity.

    Example:
        * An Actor will be rendered over any items and any corpses.
        * An Item will be rendered over any corpses, but not over any Actor.
    """
    CORPSE = 1
    ITEM = 2
    ACTOR = 3


# Functions
def message(msg, color=Colors.WHITE):
    """
    Display a message to the message log found within the UI.

    Note:
        For more details, check DisplayManager's add_message

    Args:
        msg (str): Message to be displayed to the message log.
        color (Colors): Color of the text that displays the message.
    """
    import display_manager
    display_manager.DisplayManager.add_message(msg, color)


def get_abs_path(rel_path):
    """
    Generate an absolute path for a path relative to the game root directory.

    Example:
        Given '/home/user/roguelike/' as the root game directory

        get_abs_path('fonts/my_font.png') will yield
        '/home/user/roguelike/fonts/my_font.png' regardless of where the code
        is being called from.

    Args:
        rel_path (str): Path of a resource relative to the game root directory.

    Returns:
        str: Absolute path of a resource within the game root directory.
    """
    cwd = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(cwd, rel_path)
