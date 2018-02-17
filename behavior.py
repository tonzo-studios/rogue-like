#!/usr/bin/env python
# -*- coding: utf-8 -*-


from misc import Singleton


class Behavior(metaclass=Singleton):

    """
    Base class for behaviors.
    """

    def take_turn(self, target, game_map):
        raise NotImplementedError


class NullBehavior(Behavior):

    """
    Do nothing.
    """

    def take_turn(self, target, game_map):
        pass


class BasicMonster(Behavior):

    """
    Follow a target if visible and attack when in melee range.
    """

    def take_turn(self, target, game_map):
        monster = self.owner

        # Check if the monster can see the target
        # TODO: For now, we just check if the player can see the monster and
        # assume the monster can see it too. If we make entities with different
        # visibility radius, this will have to change
        if game_map.fov[monster.pos]:
            if monster.distance_to(target.pos) >= 2:
                # Target is too far to attack, move towards it
                monster.move_towards(target.pos, game_map)
            else:
                # Attack the target
                if target.type == 'actor':
                    monster.attack(target)


class PlayerBehavior(Behavior):

    def take_turn(self, target, game_map):
        # FIXME Placeholder
        print(f"Player {actor.name} is taking its turn...")
