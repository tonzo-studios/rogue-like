#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import pytest

from math import sqrt
from misc import Singleton, Vector, Colors, RenderPriority, message, get_abs_path


class TestSingleton(object):

    def test_singleton_as_meta(self):
        class Dummy(metaclass=Singleton):

            def __init__(self, a, b):
                self.a = a
                self.b = b

        d1 = Dummy(1, 3)
        d2 = Dummy(5, 3)
        assert d1 == d2
        assert d1.a == 1
        assert d1.b == 3


class TestVector(object):

    def test_vector_operations(self):
        u = Vector(0.3, 2)
        v = Vector(3, -2.5)
        assert u + v == Vector(3.3, -0.5)
        assert u - v == Vector(-2.7, 4.5)

    @pytest.mark.parametrize("x, y, result", [
        (0, 0, 0.),
        (1, 0, 1.),
        (2, -1.5, 2.5),
        (-0.5, -1.5, sqrt(10)/2)
    ])
    def test_vector_norm(self, x, y, result):
        tol = 1e-5
        norm = Vector(x, y).norm
        assert abs(norm - result) < tol

    def test_vector_normalized(self):
        tol = 1e-5
        assert Vector(1, 0).normalized() == Vector(1, 0)
        assert Vector(0, -0.5).normalized() == Vector(0, -1)
        assert (Vector(-1, 1).normalized() - Vector(-sqrt(2), sqrt(2))).norm - 1. < tol

    def test_vector_repr(self):
        assert repr(Vector(-0.5, 2)) == "(-0.5, 2)"


class TestColors(object):

    def test_return_tuple(self):
        assert isinstance(Colors.RED, tuple)

    def test_color(self):
        assert Colors.BLUE == (0, 0, 255)

    def test_static(self):
        with pytest.raises(NotImplementedError):
            Colors()


class TestRenderPriority(object):

    def test_return_value(self):
        assert RenderPriority.CORPSE.value == 1

    def test_precedence(self):
        assert RenderPriority.ACTOR.value > RenderPriority.ITEM.value > RenderPriority.CORPSE.value


class TestMessage(object):

    def test_message_added(self):
        from display_manager import DisplayManager
        message("Hello world!")
        assert ("Hello world!", Colors.WHITE) in DisplayManager.game_msgs

    def test_message_non_default_color(self):
        from display_manager import DisplayManager
        message("Foo", Colors.BLUE)
        assert ("Foo", Colors.BLUE) in DisplayManager.game_msgs


class TestAbsPath(object):

    def test_abs_path(self):
        path = 'lucida10x10_gs_tc.png'
        abs_path = get_abs_path(path)
        assert len(abs_path) > len(path)
        assert os.path.isfile(abs_path)
