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
    """

    contents = OrderedDict()
    cur_weight = 0.0
    max_weight = 100.0

    def _search(cls, name):
        for item in cls.contents:
            if item.name == name:
                return item

    def add(cls, item, qty):
        """
        Add the specified qty of item to the backpack's contents.

        Args:
            item (Item): Item object to be added to the contents of the backpack.
            qty (int): Amount of the item to be added to the contents of the backpack.
        """
        c_item = cls._search(item.name)
        if c_item and c_item.weight * qty + cls.cur_weight <= cls.max_weight:
            cls.contents[c_item] += qty
            cls.cur_weight += c_item.weight * qty
        else:
            if item.weight * qty + cls.cur_weight <= cls.max_weight:
                cls.contents[item] = qty
                cls.cur_weight += item.weight * qty

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
        item = list(cls.contents)[i]
        used = item.use(target)

        if used:
            if cls.contents[item] == 1:
                del cls.contents[item]
            else:
                cls.contents[item] -= 1
            cls.cur_weight -= item.weight
