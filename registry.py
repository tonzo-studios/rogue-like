#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import json
import sys
from functools import partial

import effects
from entities import Actor, Item
from misc import Singleton


class RegistryError(NameError):

    def __init__(self, message):
        super().__init__(message)


class BehaviorNotFoundError(RegistryError):

    def __init__(self, behavior):
        super().__init__(f"The behavior '{behavior}' was not found in the registry.")


class EffectNotFoundError(RegistryError):

    def __init__(self, effect):
        super().__init__(f"The effect '{effect}' was not found in the registry.")


class MonsterNotFoundError(RegistryError):

    def __init__(self, monster):
        super().__init__(f"The monster '{monster}' was not found in the registry.")


class ItemNotFoundError(RegistryError):

    def __init__(self, item):
        super().__init__(f"The item '{item}' was not found in the registry.")


class Registry(metaclass=Singleton):
    """
    The registry contains info about most classes in the game, serving as a factory for things like monsters and items.

    The registry is a singleton, and loads all the needed information from json files upon creation. All data remains
    loaded in the registry until the game is closed.
    """
    behaviors = {}
    effect = {}
    monsters = {}
    items = {}

    def __init__(cls):
        """
        Load all data upon creation.
        """
        cls.load()

    @staticmethod
    def _load_module(module_name):
        def predicate(obj):
            return inspect.isclass(obj) and obj.__module__ == module_name

        return inspect.getmembers(sys.modules[module_name], predicate)

    def _load_behaviors(cls):
        cls.behaviors = dict(cls._load_module('behavior'))

    def _load_effects(cls):
        cls.effect = dict(cls._load_module('effects'))

    def _load_monsters(cls):
        with open('monsters.json', 'r') as f:
            json_monsters = json.load(f)

        mob_map = ('name', 'char', 'color')

        for mob_vals in json_monsters.values():
            json_behavior = mob_vals.pop()
            real_behavior = cls.behaviors.get(json_behavior)

            if real_behavior is None:
                raise BehaviorNotFoundError(json_behavior)

            mob_vals = dict(zip(mob_map, mob_vals))

            cls.monsters[mob_vals['name']] = partial(
                Actor, behavior=real_behavior, **mob_vals)

    def _load_items(cls):
        with open('items.json', 'r') as f:
            json_items = json.load(f)

        mob_map = ('name', 'char', 'color')
        item_map = (*mob_map, 'blocks')

        for item_vals in json_items.values():
            json_effect = item_vals.pop()
            real_effect = cls.effect.get(json_effect)

            if real_effect is None:
                raise EffectNotFoundError(json_effect)

            item_vals = dict(zip(item_map, item_vals))

            cls.items[item_vals['name']] = partial(
                Item, effect=real_effect, **item_vals)

    def load(cls):
        cls._load_behaviors()
        cls._load_effects()
        cls._load_monsters()
        cls._load_items()

    def get_behavior(cls, key):
        """
        Retrieve the behavior corresponding to the key in the registry.

        Args:
            key (string): Name of the behavior class to retrieve.

        Returns:
            Behavior: The behavior corresponding to the key, if found.

        Raises:
            BehaviorNotFoundError: If there's no behavior with the given key in the registry.
        """
        behavior = cls.behaviors.get(key)
        if behavior is None:
            raise BehaviorNotFoundError(key)
        return behavior

    def get_effect(cls, key):
        """
        Retrieve the effect corresponding to the key in the registry.

        Args:
            key (string): Name of the effect class to retrieve.

        Returns:
            Effect: The effect corresponding to the key, if found.

        Raises:
            EffectNotFoundError: If there's no effect with the given key in the registry.
        """
        effect = cls.effect.get(key)
        if effect is None:
            raise EffectNotFoundError(key)
        return effect

    def get_monster(cls, key):
        """
        Return a partial for an Actor object with some data filled in:
            * Name
            * Char
            * Color
            * Behavior

        Args:
            key (string): Name of the monster to get.

        Returns:
            functools.partial: A partial for an Actor with most info for the constructor filled in.

        Raises:
            MonsterNotFoundError: If there's no monster with the given key in the registry.
        """
        monster = cls.monsters.get(key)
        if monster is None:
            raise MonsterNotFoundError(key)
        return monster

    def get_item(cls, key):
        """
        Return a partial for an Item object with some data filled in:
            * Name
            * Char
            * Color
            * Behavior
            * Blocks

        Args:
            key (string): Name of the item to get.

        Returns:
            functools.partial: A partial for an Item with most info for the constructor filled in.

        Raises:
            ItemNotFoundError: If there's no item with the given key in the registry.
        """
        item = cls.items.get(key)
        if item is None:
            raise ItemNotFoundError(key)
        return item
