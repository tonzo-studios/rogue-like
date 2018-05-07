#!/usr/bin/env python
# -*- coding: utf-8 -*-


from misc import Singleton


class Behavior(metaclass=Singleton):
    """
    Base class for behaviors.
    """

    def take_turn(self, caller, target, game_map):
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
            game_map (Level): Level in the dungeon where the actions are performed.
        """
        raise NotImplementedError


class NullBehavior(Behavior):
    """
    Do nothing.
    """

    def take_turn(self, caller, target, game_map):
        pass


class BasicMonster(Behavior):
    """
    Follow a target if visible and attack when in melee range.
    """

    def take_turn(self, caller, target, game_map):
        # Check if the monster can see the target
        # TODO: For now, we just check if the player can see the monster and
        # assume the monster can see it too. If we make entities with different
        # visibility radius, this will have to change
        if game_map.fov[caller.pos]:
            if caller.distance_to(target.pos) >= 2:
                # Target is too far to attack, move towards it
                caller.move_towards(target.pos, game_map)
            else:
                # Attack the target
                if target.type == 'actor':
                    caller.attack(target)
