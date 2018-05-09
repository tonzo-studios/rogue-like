#!/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import OrderedDict

from misc import Singleton


class Backpack(metaclass=Singleton):
    """
    The backpack is a singleton that contains all of the items collected by the player.

    Items can be added, removed and used by the player.

    When adding items it will check if the item already exists in the backpack and will increase
    the quantity counter if it does, it will add the item if it doesn't exist and there's
    enough free space in the backpack.

    Args:
        registry (Registry): A reference to the registry where it resides, so it can access items by key.
    """

    contents = OrderedDict()
    cur_weight = 0.0
    max_weight = 100.0

    def __init__(cls, registry):
        cls.registry = registry

    def _search(cls, key):
        for item_key in cls.contents:
            if item_key == key:
                return True
        return False

    def add(cls, item_key, qty):
        """
        Add the specified qty of item to the backpack's contents.

        Args:
            item_key (Items): ID of the item to be added to the contents of the backpack.
            qty (int): Amount of the item to be added to the contents of the backpack.
        """
        weight = cls.registry.get_item(item_key).weight
        found = cls._search(item_key)
        if found and weight * qty + cls.cur_weight <= cls.max_weight:
            cls.contents[item_key] += qty
            cls.cur_weight += weight * qty
        elif weight * qty + cls.cur_weight <= cls.max_weight:
            cls.contents[item_key] = qty
            cls.cur_weight += weight * qty

    def use(cls, i, target):
        """
        Try to use the item at position i upon the specified target.

        If the usage is valid:
            * The item quantity is decreased by one if there's more than one of the item.
            * The item is deleted from the backpack's contents.
        Else:
            Nothing happens.

        Args:
            i (int): Index of the item to be used.
            target (Actor): Actor upon which to use the item's effect if any.
        """
        item_key = list(cls.contents)[i]
        item_object = cls.registry.get_item(item_key)
        used = item_object.use(target)

        if used:
            if cls.contents[item_key] == 1:
                del cls.contents[item_key]
            else:
                cls.contents[item_key] -= 1
            cls.cur_weight -= item_object.weight

    def clear(cls):
        """
        Remove all the contents from the backpack.
        """
        cls.cur_weight = 0.0
        cls.contents.clear()
