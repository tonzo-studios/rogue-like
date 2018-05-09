#!/usr/bin/env python
# -*- coding: utf-8 -*-


import numpy as np
import pytest

from level import Room, Tilemap, Level
from misc import Vector


@pytest.fixture
def native_tilemap():
    """Return a tilemap generated from a 10x10 native matrix of ones."""
    matrix = [[1 for _ in range(10)] for _ in range(10)]
    return Tilemap(matrix)


@pytest.fixture
def numpy_tilemap():
    """Return a tilemap generated from a 10x10 numpy matrix of ones."""
    return Tilemap(np.ones((10, 10)))


@pytest.fixture
def position():
    return Vector(3, 5)


@pytest.fixture
def room():
    return Room(-1, 2, 10, 15)


class TestTilemap(object):

    def test_native_tilemap_access(self, native_tilemap, position):
        assert native_tilemap[position] == 1

    def test_numpy_tilemap_access(self, numpy_tilemap, position):
        assert numpy_tilemap[position] == 1

    def test_native_tilemap_set(self, native_tilemap, position):
        native_tilemap[position] = 3
        assert native_tilemap[position] == 3

    def test_numpy_tilemap_set(self, numpy_tilemap, position):
        numpy_tilemap[position] = 3
        assert numpy_tilemap[position] == 3


class TestRoom(object):

    def test_bottom_down_corner(self, room):
        assert room.x2 == 9
        assert room.y2 == 17

    def test_center(self, room):
        assert room.center() == Vector(4, 9)

    def test_intersect(self, room):
        assert room.intersect(Room(3, 5, 12, 5))
        assert not room.intersect(Room(100, 100, 10, 10))
        assert room.intersect(room)
