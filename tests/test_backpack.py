#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pytest


@pytest.fixture
def player():
    from registry import Registry, Actors
    from entities import Actor
    from behavior import NullBehavior
    # Player needs the registry to manage the backpack
    registry = Registry()
    player = Actor(Actors.HERO, 'Player', NullBehavior(), '@', (255, 255, 255), registry=registry)
    player.backpack.clear()
    return player


@pytest.fixture
def air():
    from registry import Items, Registry
    registry = Registry()
    return registry.get_item(Items.AIR)


@pytest.fixture
def candy():
    from registry import Items, Registry
    registry = Registry()
    return registry.get_item(Items.CANDY)


class TestBackpackItem(object):

    def test_add_to_backpack(self, player, air, candy):
        player.backpack.add(air.key, 100)
        assert air.key in player.backpack.contents
        assert player.backpack.contents[air.key] == 100
        assert player.backpack.cur_weight == 0.0
        player.backpack.add(candy.key)
        assert player.backpack.contents[candy.key] == 1

    def test_use_unusable_item(self, player, air):
        player.backpack.add(air.key)
        player.backpack.use(air.key, player)
        assert player.backpack.contents[air.key] == 1

    def test_add_existing_item(self, player, air):
        player.backpack.add(air.key, 100)
        player.backpack.add(air.key, 100)
        assert len(player.backpack.contents) == 1
        assert player.backpack.contents[air.key] == 200

    def test_add_new_item(self, player, air, candy):
        player.backpack.add(air.key, 100)
        player.backpack.add(candy.key, 5)
        assert len(player.backpack.contents) == 2

    def test_add_over_limit_weight(self, player, air, candy):
        player.backpack.add(candy.key, 100)
        player.backpack.add(candy.key, 100)
        player.backpack.add(air.key, 500)
        assert player.backpack.contents[candy.key] == 100
        assert player.backpack.contents[air.key] == 500
        assert player.backpack.cur_weight == 100.0

    def test_use_item(self, player, candy):
        player.backpack.add(candy.key, 2)
        player.hp -= 100
        player.backpack.use(candy.key, player)
        assert player.backpack.contents[candy.key] == 1
        assert player.hp == 52.5

    def test_exhaust_item(self, player, candy):
        player.backpack.add(candy.key, 1)
        player.backpack.use(candy.key, player)
        assert len(player.backpack.contents) == 0

    def test_exists(self, player, candy):
        assert not player.backpack.exists(candy.key)
        player.backpack.add(candy.key)
        assert player.backpack.exists(candy.key)
        player.backpack.use(candy.key, player)
        assert not player.backpack.exists(candy.key)

    def test_use_nonexistent_item(self, player, candy):
        with pytest.raises(ValueError):
            player.backpack.use(candy.key, player)
