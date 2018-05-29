#!/usr/bin/env python
# -*- coding: utf-8 -*-

import inspect
import sys
from ast import literal_eval
from csv import DictReader
from enum import Enum, unique
from functools import partial

import effects
import behavior
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
    effect = {}
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
            return (inspect.isclass(obj) or inspect.isfunction(obj)) and obj.__module__ == module_name

        return inspect.getmembers(sys.modules[module_name], predicate)

    def _load_behaviors(cls):
        cls.behaviors = dict(cls._load_module('behavior'))

    def _load_effects(cls):
        cls.effect = dict(cls._load_module('effects'))

    def _load_actors(cls):
        with open('actors.csv', 'r') as f:
            reader = DictReader(f, delimiter=';')

            for actor in reader:
                str_behavior = actor.get('behavior')
                # If no behavior is specified, default to null behavior
                real_behavior = None
                if str_behavior != '':
                    real_behavior = cls.behaviors.get(str_behavior)

                # Convert datatypes to the right ones
                actor['key'] = Actors(int(actor.get('key')))
                actor['behavior'] = real_behavior
                to_literal = ['color']
                for arg in to_literal:
                    actor[arg] = literal_eval(actor.get(arg))

                cls.actors[actor['key']] = partial(Actor, **actor)

    def _load_items(cls):
        with open('items.csv', 'r') as f:
            reader = DictReader(f, delimiter=';')

            for item in reader:
                str_effect = item.get('effect')
                real_effect = None
                effect_args = item.pop('effect_args')
                if str_effect != '':
                    # Create the effect passing the required args
                    real_effect = partial(cls.effect.get(str_effect), *literal_eval(effect_args))

                # Convert datatypes to the right ones
                item['key'] = Items(int(item.get('key')))
                item['effect'] = real_effect
                to_literal = ['color', 'blocks', 'weight']
                for arg in to_literal:
                    item[arg] = literal_eval(item.get(arg))

                cls.items[item['key']] = partial(Item, **item)

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
            The behavior corresponding to the key, if found.

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
            The effect corresponding to the key, if found, as a function with no args filled in yet.

        Raises:
            EffectNotFoundError: If there's no effect with the given key in the registry.
        """
        if not cls.loaded:
            raise RegistryNotInitializedError
        effect = cls.effect.get(key)
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
        return actor()

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
        return item()
