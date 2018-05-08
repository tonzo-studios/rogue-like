#!/usr/bin/env python
# -*- coding: utf-8 -*-


from misc import Singleton


class Behavior(metaclass=Singleton):
    """
    Base class for behaviors.
    """

    @staticmethod
    def take_turn(caller, target):
        """
        Let the current entity take a turn.

        A turn is defined by the usual actions that an entity can perform
        before other entities can take a turn.

        Examples:
            * Moving
            * Attacking
            * Consuming / using items
            * Activating mechanisms
            * Picking up items
            * Catching fire

        Args:
            caller (Entity): Entity that performs the action.
            target (Entity): Entity to perform actions on, can be None.
        """
        raise NotImplementedError


class NullBehavior(Behavior):
    """
    Do nothing.
    """

    @staticmethod
    def take_turn(caller, target):
        pass


class BasicMonster(Behavior):
    """
    Follow a target if visible and attack when in melee range.
    """

    @staticmethod
    def take_turn(caller, target):
        # Check if the monster can see the target
        # TODO: For now, we just check if the player can see the monster and
        # assume the monster can see it too. If we make entities with different
        # visibility radius, this will have to change
        # TODO: Add patrol mode if the player is not visible
        assert caller.game_map is not None and caller.game_map == target.game_map
        game_map = caller.game_map
        if game_map.fov[caller.pos]:
            if caller.distance_to(target.pos) >= 2:
                # Target is too far to attack, try moving towards it
                path = game_map.compute_path(caller.pos, target.pos)
                if not path:
                    # Can't reach the target, don't do anything
                    return
                # Only try to move closer to the target if the monster doesn't have to lose vision of the target to do
                # so. In this case, don't do anything
                for tile in path:
                    if not game_map.fov[tile]:
                        # Try to move closer taking one step in the direction of the target
                        direction = (target.pos - caller.pos).snap_to_grid()
                        if game_map.walkable[caller.pos + direction]:
                            caller.move(direction)
                            return
                # The path is clear and the monster doesn't have to lose sight of the target, so follow the path
                direction = path[0] - caller.pos
                caller.move(direction)
            else:
                # Attack the target
                if target.type == 'actor':
                    caller.attack(target)
