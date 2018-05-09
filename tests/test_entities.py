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
def orc():
    from registry import Actors, Registry
    registry = Registry()
    return registry.get_actor(Actors.ORC)


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


@pytest.fixture
def game_map(player, air, candy):
    """Create a level and place other objects in it."""
    from misc import Vector
    from dungeon import Dungeon
    from registry import Registry
    registry = Registry()
    dungeon = Dungeon()
    dungeon.clear()
    dungeon.initialize(player, registry)
    level = dungeon.current_level
    # Place player and orc in this level
    player.place(level, Vector(0, 0))
    candy.place(level, Vector(1, 0))
    air.place(level, Vector(0, 1))
    return level


class TestEntity(object):

    def test_distance_to(self, player, air, candy):
        assert player.distance_to(air.pos) == player.distance_to(candy.pos)

    def test_stat_recompute(self, player):
        player.strength += 1
        assert player.physical_dmg == 3.96

    def test_actor_death(self, player):
        player.hp -= 200
        assert player.hp == 0
        assert player.dead

    def test_actor_level_up_standard(self, player):
        player.exp += 83
        assert player.level == 2
        assert player.exp == 0

    def test_actor_level_up_overshoot(self, player):
        player.exp += 166
        assert player.level == 3
        assert player.exp == 0

    def test_actor_level_up_extra(self, player):
        player.exp += 100
        assert player.level == 2
        assert player.exp == 17

    def test_entity_placement(self, game_map, orc):
        from misc import Vector
        assert orc.game_map is None
        assert orc.pos == Vector(0, 0)
        orc.place(game_map, Vector(5, -2))
        assert orc.game_map == game_map
        assert orc.pos == Vector(5, -2)
        assert orc in game_map.entities

    def test_blocking_entity_in_map(self, game_map, orc):
        from misc import Vector
        # Force set walkable on origin
        game_map.walkable[Vector(0, 0)] = True
        orc.place(game_map, Vector(0, 0))
        assert not game_map.walkable[Vector(0, 0)]
        orc.place(game_map, Vector(1, 1))
        assert game_map.walkable[Vector(0, 0)]

    def test_unblocking_entity_in_map(self, game_map, air):
        from misc import Vector
        # Force set walkable on origin
        game_map.walkable[Vector(0, 0)] = True
        air.place(game_map, Vector(0, 0))
        assert game_map.walkable[Vector(0, 0)]
        air.place(game_map, Vector(1, 1))
        assert game_map.walkable[Vector(0, 0)]

    def test_item_interaction_exhaust(self, game_map, player, candy):
        assert candy in game_map.entities
        candy.use(player)
        assert candy not in game_map.entities


class TestBackpackItem(object):

    def test_add_to_backpack(self, player, air):
        player.backpack.add(air.key, 100)
        assert air.key in player.backpack.contents
        assert player.backpack.contents[air.key] == 100
        assert player.backpack.cur_weight == 0.0

    def test_use_unusable_item(self, player, air):
        player.backpack.add(air.key, 1)
        player.backpack.use(0, player)
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
        player.backpack.use(0, player)
        assert player.backpack.contents[candy.key] == 1
        assert player.hp == 52.5

    def test_exhaust_item(self, player, candy):
        player.backpack.add(candy.key, 1)
        player.backpack.use(0, player)
        assert len(player.backpack.contents) == 0
