#!/usr/bin/env python
# -*- coding: utf-8 -*-


from abc import ABC, abstractmethod


class Effect(ABC):
    """
    An effect consists of a method which immediately modifies a specific target in some way when activated.

    Effects can have attributes, and are loaded by the registry when the game loads.
    Effects can be used by items or by things like special attacks, activated traps, etc.
    """

    @abstractmethod
    def take_effect(self, target):
        """
        Produces the effect on the specified target. What happens depends on the effect class.
        """
        pass


class HealEffect(Effect):
    """
    Instantly heal the target for a certain amount of hp.

    Args:
        hp (int): Amount of hp to heal the target for when the effect is activated.
    """

    def __init__(self, hp):
        self.hp = hp

    def take_effect(self, target):
        target.hp += self.hp
