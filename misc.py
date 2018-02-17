#!/usr/bin/env python
# -*- coding: utf-8 -*-

from math import sqrt

class Singleton(type):

    """
    Singleton metaclass.
    """

    _obj = None

    def __init__(self, name, bases, namespace):
        super().__init__(name, bases, namespace)

    def __call__(self):
        if self._obj is None:
            self._obj = type.__call__(self)
        return self._obj


class Vector:
    """Represents a vector in a 2D Euclidean space.

    Can be used to represent position, distance, direction, etc.
    Overrides the addition and subtraction operators to perform element-wise operations.
    """

    def __init__(self, x, y):
        """Initialize the vector's components."""
        self.x = x
        self.y = y

    def __add__(self, other):
        """Perform element-wise addition."""
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        """Perform element-wise subtraction."""
        return Vector(self.x - other.x, self.y - other.y)

    def __repr__(self):
        """Represent the vector as a tuple."""
        return f"({self.x}, {self.y})"

    def __eq__(self, other):
        """Two vectors are equal if they have the same components."""
        return self.x == other.x and self.y == other.y

    @property
    def norm(self):
        """Return the norm of the vector."""
        return sqrt(self.x ** 2 + self.y ** 2)

    def normalized(self):
        """Return a unitary vector with the same direction."""
        norm = self.norm
        return Vector(self.x / norm, self.y / norm)
