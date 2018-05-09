#!/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest

from dungeon import DungeonException


@pytest.fixture
def dungeon():
    from dungeon import Dungeon
    dungeon = Dungeon()
    dungeon.clear()
    return dungeon


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


class TestDungeon(object):

    def test_initialize_dungeon(self, dungeon, player):
        dungeon.initialize(player, player.registry)
        assert dungeon.levels
        assert dungeon.player is not None
        assert dungeon.registry is not None

    def test_player_placement_upon_initialization(self, dungeon, player):
        dungeon.initialize(player, player.registry)
        assert player.game_map is not None
        assert player in dungeon.current_level.entities

    def test_player_teleport_upon_level_change(self, dungeon, player):
        dungeon.initialize(player, player.registry)
        old_level = dungeon.current_level
        dungeon.go_to_next_level()
        new_level = dungeon.current_level
        assert player in new_level.entities
        assert player not in old_level.entities

    def test_current_level_number(self, dungeon, player):
        dungeon.initialize(player, player.registry)
        assert dungeon.current_level_number == 1
        for _ in range(5):
            dungeon.go_to_next_level()
        assert dungeon.current_level_number == 6
        for _ in range(3):
            dungeon.go_to_previous_level()
        assert dungeon.current_level_number == 3

    def test_uninitialized_dungeon(self, dungeon):
        assert dungeon.player is None
        assert dungeon.registry is None
        assert not dungeon.levels
        with pytest.raises(DungeonException):
            dungeon.current_level
        with pytest.raises(DungeonException):
            dungeon.current_level_number
        with pytest.raises(DungeonException):
            dungeon.recompute_fov()
        with pytest.raises(DungeonException):
            dungeon.go_to_next_level()

    def test_top_level(self, dungeon, player):
        dungeon.initialize(player, player.registry)
        with pytest.raises(DungeonException):
            dungeon.go_to_previous_level()

    def test_reinitialize_dungeon(self, dungeon, player):
        dungeon.initialize(player, player.registry)
        with pytest.raises(DungeonException):
            dungeon.initialize(player, player.registry)
