#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from math import floor
from misc import Vector


class Entity(ABC):

    @abstractmethod
    def __init__(self, name, pos, type, char, color):
        self.name = name
        self.pos = pos
        self.type = type
        self.char = char
        self.color = color

    def move(self, direction):
        self.pos += direction

    @abstractmethod
    def attack(self, other): pass

    def __repr__(self):
        return f"{self.name} <{self.type}>@{self.pos}"

    def distance_to(self, dest):
        """Return the distance this entity and the destination position."""
        return (self.pos - dest).norm

    def move_towards(self, dest, game_map):
        """Move towards the destination if there's a clear path."""
        path = game_map.compute_path(self, self.pos, dest)
        next_tile = Vector(path[0][0], path[0][1])
        direction = next_tile - self.pos

        if (game_map.walkable[next_tile] and
           not game_map.get_blocking_entity_at_location(next_tile)):
            self.move(direction)


class Actor(Entity):

    """
    An actor is an entity that can perform actions.
    """

    def __init__(self, name, pos, behavior, char, color):
        """
        Initialize an actor object

        @param name: str -> Name of the actor
        @param pos: Vector -> Vector representing this actor's position
        @param behavior: Behavior -> A behavior singleton implementing some
            of this actor's actions
        """
        super().__init__(name, pos, 'actor', char, color)
        self.behavior = behavior
        # base stats
        self._strength = 5
        self._constitution = 5
        self._intelligence = 5
        self._dexterity = 5
        self._luck = 5
        # other stats
        self._level = 1
        self._exp = 0
        self._max_exp = floor(1 + 300 * 2 ** (1/7)) / 4
        self._gold = 100
        # computed stats
        self._max_hp = self._compute_max_hp()
        self._max_mp = self._compute_max_mp()
        self._cur_hp = self._max_hp
        self._cur_mp = self._max_mp
        self._physical_dmg = self._compute_physical_damage()
        self._ranged_dmg = self._compute_ranged_damage()
        self._magical_dmg = self._compute_magical_damage()
        self._crit_rate = self._compute_crit_rate()
        self._dodge_rate = self._compute_dodge_rate()

    def _generic_setter(self, attr, val, _min=0):
        if val >= _min:
            setattr(self, attr, val)
        else:
            setattr(self, attr, _min)

    # Actions
    def attack(self, other):
        # TODO: Work out differents types of damage
        other.hp -= self.physical_dmg

    # Stat properties
    @property
    def physical_dmg(self):
        return self._physical_dmg

    @physical_dmg.setter
    def physical_dmg(self, val):
        self._generic_setter('_physical_dmg', val)

    @property
    def magical_dmg(self):
        return self._magical_dmg

    @magical_dmg.setter
    def magical_dmg(self, val):
        self._generic_setter('_magical_dmg', val)

    @property
    def ranged_dmg(self):
        return self._ranged_dmg

    @ranged_dmg.setter
    def ranged_dmg(self, val):
        self._generic_setter('_ranged_dmg', val)

    @property
    def crit_rate(self):
        return self._crit_rate

    @crit_rate.setter
    def crit_rate(self, val):
        self._generic_setter('_crit_rate', val)

    @property
    def dodge_rate(self):
        return self._dodge_rate

    @dodge_rate.setter
    def dodge_rate(self, val):
        self._generic_setter('_dodge_rate', val)

    @property
    def max_hp(self):
        return self._max_hp

    @max_hp.setter
    def max_hp(self, val):
        self._generic_setter('_max_hp', val)

    @property
    def hp(self):
        return self._cur_hp

    @hp.setter
    def hp(self, val):
        self._generic_setter('_cur_hp', val)

    @property
    def max_mp(self):
        return self._max_mp

    @max_mp.setter
    def max_mp(self, val):
        self._generic_setter('_max_mp', val)

    @property
    def mp(self):
        return self._cur_mp

    @mp.setter
    def mp(self, val):
        self._generic_setter('_cur_mp', val)

    @property
    def max_exp(self):
        return self._max_exp

    @max_exp.setter
    def max_exp(self, val):
        self._generic_setter('_max_exp', val, self.max_exp + 1)

    @property
    def exp(self):
        return self._exp

    @exp.setter
    def exp(self, val):
        total = val + self.exp
        if total >= self.max_exp:
            val = total - self.max_exp
            self.level += 1
        self._generic_setter('_exp', val)

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, val):
        self._generic_setter('_level', val, 1)

    @property
    def gold(self):
        return self._gold

    @gold.setter
    def gold(self, val):
        self._generic_setter('_gold', val)

    @property
    def strength(self):
        return self._strength

    @strength.setter
    def strength(self, val):
        self._generic_setter('_strength', val, 1)
        self.physical_dmg = self._compute_physical_damage()
        self.max_hp = self._compute_max_hp()

    @property
    def intelligence(self):
        return self._intelligence

    @intelligence.setter
    def intelligence(self, val):
        self._generic_setter('_intelligence', val, 1)
        self.magical_dmg = self._compute_magical_damage()
        self.max_mp = self._compute_max_mp()

    @property
    def dexterity(self):
        return self._dexterity

    @dexterity.setter
    def dexterity(self, val):
        self._generic_setter('_dexterity', val, 1)
        self.ranged_dmg = self._compute_ranged_damage()
        self.crit_rate = self._compute_crit_rate()
        self.dodge_rate = self._compute_dodge_rate()

    @property
    def constitution(self):
        return self._constitution

    @constitution.setter
    def constitution(self, val):
        self._generic_setter('_constitution', val, 1)
        self.max_hp = self._compute_max_hp()

    @property
    def luck(self):
        return self._luck

    @luck.setter
    def luck(self, val):
        self._generic_setter('_luck', val, 1)

    def _compute_max_hp(self):
        # 25% STR, 75% CON, 100 BASE
        hp_str = self.strength * self.level * 0.25
        hp_con = self.constitution * self.level * 0.25
        self.max_hp = hp_str + hp_con + 100

    def _compute_max_mp(self):
        # 100% INT, 50 BASE
        self.max_mp = self.intelligence * self.level + 50

    def _compute_ranged_damage(self):
        # 100% DEX
        self.ranged_dmg = self.dexterity * self.level * 0.5

    def _compute_magical_damage(self):
        # 100% INT
        self.magical_dmg = self.intelligence * self.level * 0.33

    def _compute_physical_damage(self):
        # 100% STR
        self.physical_dmg = self.strength * self.level * 0.66

    def _compute_dodge_rate(self):
        # 100% DEX, assumed max level = 50
        self.dodge_rate = (self.dexterity * self.level) / 500

    def _compute_crit_rate(self):
        # 100% LCK, assumed max level = 50
        self.crit_rate = (self.luck * self.level) / 500
