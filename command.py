#!/usr/bin/env python
# -*- coding: utf-8 -*-


import tdl
from misc import Vector


class Command:

    """
    Encapsulate a request as an object, thereby letting users parameterize clients
    with different requests, queue or log requests, and support undoable operations.

    It lets actions be turned into objects, thus making them first-class.

    The base Command class can also be used as a null command.
    """

    def execute(self):
        pass


class MoveCommand(Command):

    """
    Command to change the position of an entity.

    Args:
        entity (Entity): Entity to move.
        direction (Vector): Direction towards which to move the entity.
        display_manager (DisplayManager): Optional argument which may only be
            passed if the game map's FOV should be recomputed.
    """

    def __init__(self, entity, direction, display_manager=None):
        self.entity = entity
        self.direction = direction
        self.display_manager = display_manager

    def execute(self):
        self.entity.pos += self.direction
        if self.display_manager is not None:
            self.display_manager.fov_recompute = True


class MoveTowardsCommand(Command):

    """
    Command to move an entity towards a target position if there's a clear path.

    Args:
        entity (Entity): Entity to move.
        target (Vector): Position to move to.
        game_map (Dungeon): Current map where movement is registered.
    """
    def __init__(self, entity, target, game_map):
        self.entity = entity
        self.target = target
        self.game_map = game_map

    def execute(self):
        # Use tdl's pathfinding method to find the complete path
        path = self.game_map.compute_path(self.entity.pos, self.target)
        # Take only the next step
        next_tile = Vector(path[0][0], path[0][1])
        direction = next_tile - self.entity.pos

        if (self.game_map.walkable[next_tile] and
           not self.game_map.get_blocking_entity_at_location(next_tile)):
            self.entity.pos += direction


class AttackCommand(Command):

    """
    Command to make an actor attack another actor using the physical damage stat.

    Args:
        actor (Actor): Attacking actor.
        other (Actor): Attacked actor.
    """
    def __init__(self, actor, other):
        self.actor = actor
        self.other = other

    def execute(self):
        # TODO: Work out different types of damage
        self.other.hp -= self.actor.physical_dmg


class FullscreenCommand(Command):

    """
    Command to toggle fullscreen mode.
    """

    def execute(self):
        tdl.set_fullscreen(not tdl.get_fullscreen())


class ExitCommand(Command):

    """
    Command to quit the application.
    """

    def execute(self):
        # TODO: Find more elegant way to terminate the program
        exit()
