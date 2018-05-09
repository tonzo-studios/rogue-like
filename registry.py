#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import json
import sys
from enum import Enum, unique
from functools import partial

import effects
from backpack import Backpack
from entities import Actor, Item
from misc import Singleton


@unique
class Actors(Enum):
    HERO = 0
    ORC = 1
    DRAKE = 2
    POOPY = 3


@unique
class Items(Enum):
    CANDY = 1
    AIR = 2


class RegistryError(NameError):

    def __init__(self, message):
        super().__init__(message)


class RegistryNotInitializedError(RegistryError):

    def __init__(self):
        super().__init__("The registry hasn't been initialized yet.")


class BehaviorNotFoundError(RegistryError):

    def __init__(self, behavior):
        super().__init__(f"The behavior '{behavior}' was not found in the registry.")


class EffectNotFoundError(RegistryError):

    def __init__(self, effect):
        super().__init__(f"The effect '{effect}' was not found in the registry.")


class ActorNotFoundError(RegistryError):

    def __init__(self, actor):
        super().__init__(f"The actor '{actor}' was not found in the registry.")


class ItemNotFoundError(RegistryError):

    def __init__(self, item):
        super().__init__(f"The item '{item}' was not found in the registry.")


class Registry(metaclass=Singleton):
    """
    The registry contains info about most classes in the game, serving as a factory for things like actors and items.

    The registry is a singleton, and loads all the needed information from json files upon creation. All data remains
    loaded in the registry until the game is closed.
    """
    behaviors = {}
    effects = {}
    actors = {}
    items = {}
    loaded = False

    def __init__(cls):
        """
        Load all data upon creation.
        """
        cls.load()
        # Initialize other variables stored in the registry
        cls.backpack = Backpack(cls)
        cls.loaded = True

    @staticmethod
    def _load_module(module_name):
        def predicate(obj):
            return inspect.isclass(obj) and obj.__module__ == module_name

        return inspect.getmembers(sys.modules[module_name], predicate)

    def _load_behaviors(cls):
        cls.behaviors = dict(cls._load_module('behavior'))

    def _load_effects(cls):
        cls.effects = dict(cls._load_module('effects'))

    def _load_actors(cls):
        with open('actors.json', 'r') as f:
            json_actors = json.load(f)

        mob_map = ('name', 'char', 'color')

        for key, mob_vals in json_actors.items():
            json_behavior = mob_vals.pop()
            real_behavior = cls.behaviors.get(json_behavior)

            if real_behavior is None:
                raise BehaviorNotFoundError(json_behavior)

            mob_vals = dict(zip(mob_map, mob_vals))

            cls.actors[Actors(int(key))] = partial(
                Actor, behavior=real_behavior, **mob_vals)

    def _load_items(cls):
        with open('items.json', 'r') as f:
            json_items = json.load(f)

        mob_map = ('name', 'char', 'color')
        item_map = (*mob_map, 'blocks', 'weight')

        for key, item_vals in json_items.items():
            json_effect_args = item_vals.pop()
            json_effect = item_vals.pop()
            real_effect = None
            if json_effect is not None:
                # Create the effect passing the required args
                real_effect = cls.effects.get(json_effect)(*json_effect_args)

            item_vals = dict(zip(item_map, item_vals))

            cls.items[Items(int(key))] = partial(
                Item, effect=real_effect, **item_vals)

    def load(cls):
        cls._load_behaviors()
        cls._load_effects()
        cls._load_actors()
        cls._load_items()

    def _get_behavior(cls, key):
        """
        Retrieve the behavior corresponding to the key in the registry.

        Args:
            key (string): Name of the behavior class to retrieve.

        Returns:
            Behavior: The behavior corresponding to the key, if found.

        Raises:
            BehaviorNotFoundError: If there's no behavior with the given key in the registry.
        """
        if not cls.loaded:
            raise RegistryNotInitializedError
        behavior = cls.behaviors.get(key)
        if behavior is None:
            raise BehaviorNotFoundError(key)
        return behavior

    def _get_effect(cls, key):
        """
        Retrieve the effect corresponding to the key in the registry.

        Args:
            key (string): Name of the effect class to retrieve.

        Returns:
            Effect: The effect corresponding to the key, if found.

        Raises:
            EffectNotFoundError: If there's no effect with the given key in the registry.
        """
        if not cls.loaded:
            raise RegistryNotInitializedError
        effect = cls.effects.get(key)
        if effect is None:
            raise EffectNotFoundError(key)
        return effect

    def get_actor(cls, key):
        """
        Return a new Actor object using the data in the registry corresponding to the given ID.

        Args:
            key (Actors): ID of the actor to get.

        Returns:
            Actor: An Actor with the information corresponding to the ID in the registry.

        Raises:
            ActorNotFoundError: If there's no actor with the given key in the registry.
        """
        if not cls.loaded:
            raise RegistryNotInitializedError
        actor = cls.actors.get(key)
        if actor is None:
            raise ActorNotFoundError(key)
        return actor(key=key)

    def get_item(cls, key):
        """
        Return a new Item object using the data in the registry corresponding to the given ID.

        Args:
            key (Items): ID of the item to get.

        Returns:
            Item: An Item with the information corresponding to the ID in the registry.

        Raises:
            ItemNotFoundError: If there's no item with the given key in the registry.
        """
        if not cls.loaded:
            raise RegistryNotInitializedError
        item = cls.items.get(key)
        if item is None:
            raise ItemNotFoundError(key)
        return item(key=key)
