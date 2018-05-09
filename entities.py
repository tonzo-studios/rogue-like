#!/usr/bin/env python
# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from math import floor

from behavior import NullBehavior
from misc import Colors, RenderPriority, message, Vector


class Entity(ABC):
    """
    An entity is any object that can be visually represented in the game map.

    Entities are represented by a character that is displayed to the screen,
    and a color that is applied to said character.

    Note:
        This is an abstract class and cannot be instanciated directly, it must be
        sub-classed in order for it to be usable.

    Examples:
        * A chest containing items, traps, etc.
        * The player character.
        * Enemies.

    Args:
        key (Enum): An identifier for the entity in the registry.
        name (str): A name for the entity, doesn't have to be unique.
        type (str): Pseudo-type of this entity, can be one of 'player', 'npc',
            'enemy', 'item', ...
        char (str): How the entity will be visually displayed.
        color (Colors): Color of the character that visually represents this entity.
        blocks (bool): Whether this entity is blocking or not.
        render_priority (RenderPriority): At what layer should this entity be
            rendered.
    """

    pos = Vector(0, 0)
    game_map = None

    @abstractmethod
    def __init__(self, key, name, type, char, color, blocks, render_priority):
        self.key = key
        self.name = name
        self.type = type
        self.char = char
        self.color = color
        self.blocks = blocks
        self.render_priority = render_priority

    def __repr__(self):
        return f"{self.key.name} '{self.name}' <{self.type}>@{self.pos}"

    def move(self, direction):
        """
        Move this entity in the specified direction in the given map.

        Args:
            direction (Vector): Direction towards which to move this entity.
       """

        old_pos = self.pos
        self.pos += direction
        if self.blocks:
            # Update blocked tile in the map
            self.game_map.walkable[old_pos] = True
            self.game_map.walkable[self.pos] = False

    def distance_to(self, dest):
        """
        Calculate the distance between this entity and the destination position.

        Args:
            dest (Vector): Vector to calculate the distance to.

        Returns:
            float: The relative distance between this entity and the destination
                position.
        """
        return (self.pos - dest).norm

    def move_towards(self, dest):
        """
        Move towards the destination if there's a clear path.

        Args:
            dest (Vector): Position to move to.
        """

        path = self.game_map.compute_path(self.pos, dest)
        if not path:
            # Don't do anything
            return
        next_tile = path[0]
        direction = next_tile - self.pos

        if self.game_map.walkable[next_tile] and not self.game_map.get_blocking_entity_at_location(next_tile):
            self.move(direction)

    def place(self, game_map, position):
        """
        Place the entity at a certain position in the given map.

        Args:
            game_map (Level): Level in which to place the entity.
            position (Vector): Position in the level where the entity should be placed.
        """
        # If the entity was on another map, first remove it from there
        if self.game_map:
            self.game_map.entities.remove(self)
            self.game_map.walkable[self.pos] = True
        self.game_map = game_map
        self.pos = position
        game_map.entities.append(self)
        if self.blocks:
            game_map.walkable[position] = False


class Item(Entity):
    """
    Represents an item in the game world and/or in the backpack.

    An item can be dropped by a monster, found randomly from the game world,
    can be picked up and/or given to the player.

    Args:
        effect (Effect): Triggered on item use, defaults to None for items with no effect.
        weight (float): Weight of the item, defaults to 1.0
    """

    def __init__(self, key, name, char, color, blocks=False, effect=None, weight=1.0):
        super().__init__(key, name, 'item', char, color, blocks, RenderPriority.ITEM)
        self.behavior = NullBehavior()
        self.effect = effect
        self.weight = weight

    def use(self, target):
        """
        Use the item upon the specified target, activating its effect. See Effect for more info.

        Args:
            target (Actor): The actor that will be affected by the item's effect.

        Returns:
            bool: True if the effect was successfully used, False otherwise.
        """
        if self.effect is not None:
            self.effect.take_effect(target)
            return True
        else:
            message("Nothing happened...")
        return False

    def take_turn(self, target):
        self.behavior.take_turn(None, None)


class Actor(Entity):
    """
    An actor is an entity that can perform actions on its own.

    Args:
        registry (Registry): A reference to the game's registry. Only needed to instantiate the backpack.
    """

    def __init__(self, key, name, behavior, char, color, registry=None):
        super().__init__(key, name, 'actor', char, color, blocks=True, render_priority=RenderPriority.ACTOR)
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
        self._max_exp = floor(1 + 300 * 2 ** (1 / 7)) / 4
        self._gold = 100
        # Access to the game's registry, should be None for all actors except for the player
        self.registry = registry
        # Only the player gets a reference to the backpack
        if registry is not None:
            self.backpack = registry.backpack
        # computed stats
        self._recompute_stats()

    def _generic_setter(self, attr, val, _min=0):
        if val >= _min:
            setattr(self, attr, val)
        else:
            setattr(self, attr, _min)

    def recompute_stats(func):
        """
        Decorator that triggers a stat recomputation after the function call.
        """

        def wrapper(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._recompute_stats()

        return wrapper

    def attack(self, other):
        """
        Attack another actor using this actor's physical damage.

        Args:
            other (Actor): Actor to attack.
        """

        # TODO: Work out differents types of damage
        other.hp -= self.physical_dmg

    def _die(self):
        """Become a corpse."""
        self.char = '%'
        self.behavior = NullBehavior()
        self.color = Colors.RED
        self.name += " corpse"
        self.blocks = False
        self.render_priority = RenderPriority.CORPSE
        # If the actor didn't die in oblivion, corpse becomes walkable
        if self.game_map is not None:
            self.game_map.walkable[self.pos] = True

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
        self._generic_setter('_cur_hp', val, 0)
        # Check if the actor died
        if self.dead:
            self._die()

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
        self._generic_setter('_max_exp', val, 1)

    @property
    def exp(self):
        return self._exp

    @exp.setter
    def exp(self, val):
        while val >= self.max_exp:
            val -= self.max_exp
            self.level += 1
        self._generic_setter('_exp', val)

    @property
    def level(self):
        return self._level

    @level.setter
    @recompute_stats
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
    @recompute_stats
    def strength(self, val):
        self._generic_setter('_strength', val, 1)

    @property
    def intelligence(self):
        return self._intelligence

    @intelligence.setter
    @recompute_stats
    def intelligence(self, val):
        self._generic_setter('_intelligence', val, 1)

    @property
    def dexterity(self):
        return self._dexterity

    @dexterity.setter
    @recompute_stats
    def dexterity(self, val):
        self._generic_setter('_dexterity', val, 1)

    @property
    def constitution(self):
        return self._constitution

    @constitution.setter
    @recompute_stats
    def constitution(self, val):
        self._generic_setter('_constitution', val, 1)

    @property
    def luck(self):
        return self._luck

    @luck.setter
    @recompute_stats
    def luck(self, val):
        self._generic_setter('_luck', val, 1)

    @property
    def dead(self):
        return self.hp == 0

    def _compute_max_hp(self):
        # 25% STR, 75% CON, 100 BASE
        hp_str = self.strength * self.level * 0.25
        hp_con = self.constitution * self.level * 0.25
        return hp_str + hp_con + 100

    def _compute_max_mp(self):
        # 100% INT, 50 BASE
        return self.intelligence * self.level + 50

    def _compute_ranged_damage(self):
        # 100% DEX
        return self.dexterity * self.level * 0.5

    def _compute_magical_damage(self):
        # 100% INT
        return self.intelligence * self.level * 0.33

    def _compute_physical_damage(self):
        # 100% STR
        return self.strength * self.level * 0.66

    def _compute_dodge_rate(self):
        # 100% DEX, assumed max level = 50
        return (self.dexterity * self.level) / 500

    def _compute_crit_rate(self):
        # 100% LCK, assumed max level = 50
        return (self.luck * self.level) / 500

    def _recompute_stats(self):
        """Recompute all stats that depend on other variables."""
        self._max_hp = self._compute_max_hp()
        self._max_mp = self._compute_max_mp()
        self._cur_hp = self._max_hp
        self._cur_mp = self._max_mp
        self._physical_dmg = self._compute_physical_damage()
        self._ranged_dmg = self._compute_ranged_damage()
        self._magical_dmg = self._compute_magical_damage()
        self._crit_rate = self._compute_crit_rate()
        self._dodge_rate = self._compute_dodge_rate()
