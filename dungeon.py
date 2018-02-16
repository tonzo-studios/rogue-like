#!/usr/bin/env python
# -*- coding: utf-8 -*-


from random import randint
from tdl.map import Map
from misc import Vector


class Room:
    """Represents a rectangle of walkable space."""

    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def center(self):
        """Return the coordinates of the center of the room."""
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return Vector(center_x, center_y)

    def intersect(self, other):
        """Return True if the room intersects with another one."""
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Tilemap:
    """A wrapper to access numpy array elements using vectors."""

    def __init__(self, array):
        """Store a shallow copy of the array to work with."""
        # Check if it's a numpy matrix or a normal matrix
        if isinstance(array, list):
            self.is_numpy_array = False
        else:
            # Assume if it's not a list then it's a numpy array so that we don't
            # have to import numpy and check the type explicitly
            self.is_numpy_array = True
        self._array = array

    def __getitem__(self, pos):
        if self.is_numpy_array:
            return self._array[pos.x, pos.y]
        else:
            return self._array[pos.x][pos.y]

    def __setitem__(self, pos, val):
        if self.is_numpy_array:
            self._array[pos.x, pos.y] = val
        else:
            self._array[pos.x][pos.y] = val


class Dungeon:
    def __init__(self, width, height):
        self._map = Map(width, height)
        self.width = width
        self.height = height
        self.explored = Tilemap([[False for y in range(height)] for x in range(width)])
        self.rooms = []
        self.entities = []
        # Add tilemaps for some Map arrays
        self.walkable = Tilemap(self._map.walkable)
        self.transparent = Tilemap(self._map.transparent)
        self.fov = Tilemap(self._map.fov)

    def init_room(self, room):
        """Make the tiles in the map that correspond to the room walkable."""
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                pos = Vector(x, y)
                self.walkable[pos] = True
                self.transparent[pos] = True

    def create_h_tunnel(self, x1, x2, y):
        """Create an horizontal tunnel from x1 to x2 at a fixed y."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            pos = Vector(x, y)
            self.walkable[pos] = True
            self.transparent[pos] = True

    def create_v_tunnel(self, y1, y2, x):
        """Create a vertical tunnel from y1 to y2 at a fixed x."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            pos = Vector(x, y)
            self.walkable[pos] = True
            self.transparent[pos] = True

    def generate(self, room_max_count, room_min_size, room_max_size, max_entities_per_room,
                 colors, player):
        """Generate a dungeon, place the player and populate it with entities."""
        # Initialize map
        for x in range(self.width):
            for y in range(self.height):
                pos = Vector(x, y)
                self.walkable[pos] = False
                self.transparent[pos] = False

        for r in range(room_max_count):
            # Random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # Random position without going out of the boundaries of the map
            x = randint(0, self.width - w - 1)
            y = randint(0, self.height - h - 1)

            new_room = Room(x, y, w, h)

            # If it intersects with an existent room, start over
            for room in self.rooms:
                if new_room.intersect(room):
                    break
            else:
                # Room is valid
                self.init_room(new_room)

                center = new_room.center()

                if not self.rooms:
                    # First room, position the player
                    player.pos = center
                else:
                    # Connect room to previous room
                    previous = self.rooms[-1].center()

                    # Flip a coin
                    if randint(0, 1) == 1:
                        # First move horizontally, then vertically
                        self.create_h_tunnel(previous.x, center.x, previous.y)
                        self.create_v_tunnel(previous.y, center.y, center.x)
                    else:
                        # First move vertically, then horizontally
                        self.create_v_tunnel(previous.y, center.y, previous.x)
                        self.create_h_tunnel(previous.x, center.x, center.y)

                self.place_entities(new_room, max_entities_per_room, colors)
                self.rooms.append(new_room)

    def compute_fov(self, pos, fov, radius, light_walls):
        self._map.compute_fov(pos.x, pos.y, fov=fov, radius=radius, light_walls=light_walls)

    def compute_path(self, pos1, pos2):
        """Return path from pos1 to pos2 in the map."""
        return self._map.compute_path(pos1.x, pos1.y, pos2.x, pos2.y)

    def place_entities(self, room, max_entities_per_room, colors):
        pass

    def get_blocking_entity_at_location(self, pos):
        pass
