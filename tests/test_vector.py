#!/usr/bin/env python
# -*- coding: utf-8 -*-


from math import sqrt
import pytest
from misc import Vector


def test_vector_operations():
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
def test_vector_norm(x, y, result):
    tol = 1e-5
    norm = Vector(x, y).norm
    assert abs(norm - result) < tol


def test_vector_normalized():
    tol = 1e-5
    assert Vector(1, 0).normalized() == Vector(1, 0)
    assert Vector(0, -0.5).normalized() == Vector(0, -1)
    assert (Vector(-1, 1).normalized() - Vector(-sqrt(2), sqrt(2))).norm - 1. < tol


def test_vector_repr():
    assert repr(Vector(-0.5, 2)) == "(-0.5, 2)"
