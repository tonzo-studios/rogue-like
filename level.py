#!/usr/bin/env python
# -*- coding: utf-8 -*-


from random import randint, choice

from tdl.map import Map

from entities import StairsUp, StairsDown
from misc import Vector


class Room:
    """
    Represents a rectangle of walkable space.

    Args:
        x (int): x coordinate of the top-left corner of the room.
        y (int): y coordinate of the top-left corner of the room.
        width (int): Width of the room to be created.
        height (int): Height of the room to be created.
    """

    def __init__(self, x, y, width, height):
        self.x1 = x
        self.y1 = y
        self.x2 = x + width
        self.y2 = y + height

    def center(self):
        """
        Get the center of this room object as a Vector.

        Returns:
            Vector: The center of this room object.
        """
        center_x = int((self.x1 + self.x2) / 2)
        center_y = int((self.y1 + self.y2) / 2)
        return Vector(center_x, center_y)

    def intersect(self, other):
        """
        Get whether or not this room intersects with another room.

        Args:
            other (Room): Room to check for intersections with.

        Returns:
            True if self and other intersect, false otherwise.
        """
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Tilemap:
    """
    A wrapper to access numpy array elements using vectors.

    Args:
        array (list): This can actually be either a native matrix or
            a numpy matrix, depending on which one is passed-in the logic will
            be different, but the result will be the same.
    """

    def __init__(self, array):
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


class Level:
    """
    Represents a level in the dungeon.

    A level is a place that the player explores, it is filled with enemies,
    items, npcs, secrets. It consists of a series of Room objects interconnected
    with narrow corridors. It also has stairs connecting to other levels of the dungeon.

    After initialization, the level is "unexplored", i.e. the player can't
    see the entire level upon spawning. Once the player moves around and
    explores the level, tiles will be revealed and will be "remembered".

    Args:
        width (int): Max width of the level to be generated.
        height (int): Max height of the level to be generated.
        room_max_count (int): Max amount of rooms to be generated for this
                particular level.
        room_min_size (int): Min amount of tiles per room.
        room_max_size (int): Max amount of tiles per room.
        max_entities_per_room (int): Max amount of entities to be spawned
            per room.
        registry (Registry): Reference to the game's registry.
    """

    def __init__(self, width, height, room_max_count, room_min_size, room_max_size, max_entities_per_room, dungeon,
                 registry):
        # TODO: Instead of using so many variables, use a context which contains them all and depends on the theme
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

        # Up and down stairs. These get updated when the level is generated.
        self.up_stairs = StairsUp(dungeon)
        self.down_stairs = StairsDown(dungeon)

        # Get info relative to the level generation
        self.room_max_count = room_max_count
        self.room_min_size = room_min_size
        self.room_max_size = room_max_size
        self.max_entities_per_room = max_entities_per_room

        # Generate the level
        self.generate()
        # Throw some monsters and items in it
        # TODO: Instead of passing the registry, use a context/theme
        self.populate(registry)

    def _init_room(self, room):
        """Make the tiles in the map that correspond to the room walkable."""
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                pos = Vector(x, y)
                self.walkable[pos] = True
                self.transparent[pos] = True

    def _create_h_tunnel(self, x1, x2, y):
        """Create an horizontal tunnel from x1 to x2 at a fixed y."""
        for x in range(min(x1, x2), max(x1, x2) + 1):
            pos = Vector(x, y)
            self.walkable[pos] = True
            self.transparent[pos] = True

    def _create_v_tunnel(self, y1, y2, x):
        """Create a vertical tunnel from y1 to y2 at a fixed x."""
        for y in range(min(y1, y2), max(y1, y2) + 1):
            pos = Vector(x, y)
            self.walkable[pos] = True
            self.transparent[pos] = True

    def generate(self):
        """
        Generate the level's layout.
        """
        # Initialize map
        for x in range(self.width):
            for y in range(self.height):
                pos = Vector(x, y)
                self.walkable[pos] = False
                self.transparent[pos] = False

        for r in range(self.room_max_count):
            # Random width and height
            w = randint(self.room_min_size, self.room_max_size)
            h = randint(self.room_min_size, self.room_max_size)
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
                self._init_room(new_room)

                center = new_room.center()

                if not self.rooms:
                    # First room, place up stairs
                    self.up_stairs.place(self, center)

                else:
                    # Connect room to previous room
                    previous = self.rooms[-1].center()

                    # Flip a coin
                    if randint(0, 1) == 1:
                        # First move horizontally, then vertically
                        self._create_h_tunnel(previous.x, center.x, previous.y)
                        self._create_v_tunnel(previous.y, center.y, center.x)
                    else:
                        # First move vertically, then horizontally
                        self._create_v_tunnel(previous.y, center.y, previous.x)
                        self._create_h_tunnel(previous.x, center.x, center.y)

                self.rooms.append(new_room)

        # Place down stairs
        random_room = choice(self.rooms)
        self.place_entity_randomly(self.down_stairs, random_room)

    def populate(self, registry):
        """
        Populate the level's rooms with entities.
        """
        for room in self.rooms:
            self._place_entities(room, registry)

    def compute_fov(self, pos, fov, radius, light_walls):
        """
        Compute a FOV field from the passed-in position.

        The FOV field represents how many tiles ahead can a certain actor see,
        this can affect behavior such as following, attacking, etc.

        Args:
            pos (Vector): The position vector from which the FOV should be
                calculated, usually this position is occuppied by an Actor.
            fov (str): Type of FOV algorithm to be used, usually supplied by
                tdl itself.
            radius (int): How far away should the actor be able to see.
            light_walls (bool): Whether or not walls within the FOV of the
                actor should be lit up or not.
        """
        self._map.compute_fov(pos.x, pos.y, fov=fov, radius=radius, light_walls=light_walls)

    def compute_path(self, pos1, pos2):
        """
        Calculate a path between pos1 and pos2 in the game map.

        Args:
            pos1 (Vector): Vector representing the starting point.
            pos2 (Vector): Vector representing the destination.

        Returns:
            list(Vector): A list of vectors, where each vector represents the position of the next tile in the path.
                The list goes up to the pos2.
        """
        # Get current walkable state
        pos1_walkable = self.walkable[pos1]
        pos2_walkable = self.walkable[pos2]
        # Set origin and destination to walkable for the actual computation to work
        self.walkable[pos1] = self.walkable[pos2] = True
        # Compute path
        path = self._map.compute_path(pos1.x, pos1.y, pos2.x, pos2.y)
        # Convert path to vectors
        path = [Vector(x, y) for x, y in [tile for tile in path]]
        # Revert origin and destination walkable state to its original state
        self.walkable[pos1] = pos1_walkable
        self.walkable[pos2] = pos2_walkable
        return path

    def _place_entities(self, room, registry):
        """
        Spawn and place entities in a single room.

        Args:
            room (Room): Room in which to spawn the entities.
            registry (Registry): Reference to the game's registry.
        """
        from registry import Actors, Items

        entity_number = randint(0, self.max_entities_per_room)

        for _ in range(entity_number):
            dice = randint(0, 2)
            if dice == 0:
                ent = registry.get_actor(Actors.ORC)
            elif dice == 1:
                ent = registry.get_actor(Actors.POOPY)
            else:
                ent = registry.get_item(Items.CANDY)

            self.place_entity_randomly(ent, room)

    def get_blocking_entity_at_location(self, pos):
        """
        Check if there's a blocking entity at the specified location.

        A blocking entity is one that turns the tile in which it resides into
        non-walkable, effectively blocking any other entities from accessing
        and or placing themselves into that same tile.

        Args:
            pos (Vector): Vector of the position to check for blocking entities.

        Returns:
            Entity: The blocking entity if any, None otherwise.
        """
        for entity in self.entities:
            if entity.pos == pos and entity.blocks:
                return entity
        return None

    def place_entity_randomly(self, entity, room, allow_overlap=False):
        """
        Places the given entity randomly in a given room.
        """
        # For now, naively assume that there's a free spot
        while True:
            # Get a random position inside the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)
            position = Vector(x, y)

            # Check if there's already an entity in this spot
            if not allow_overlap and [entity for entity in self.entities if entity.pos == position]:
                continue

            # We found a valid spot, place the entity
            entity.place(self, position)
            return
