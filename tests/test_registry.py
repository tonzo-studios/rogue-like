#!/usr/bin/env python
# -*- coding: utf-8 -*-

from registry import Registry


class TestRegistry(object):
    def test_loaded_items(self):
        registry = Registry()
        assert registry.actors
        assert registry.behaviors
        assert registry.effects
        assert registry.items

    def test_get_actor(self):
        from entities import Actor
        from registry import Actors
        orc = Registry().get_actor(Actors.ORC)
        assert isinstance(orc, Actor)

    def test_get_item(self):
        from entities import Item
        from registry import Items
        candy = Registry().get_item(Items.CANDY)
        assert isinstance(candy, Item)

    def test_assert_load_on_creation(self):
        assert Registry().loaded
