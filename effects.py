#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""An effect consists of a method which immediately modifies a specific target in some way when activated.

Effects can have attributes, and are loaded by the registry when the game loads.
All arguments of effects are set by the registry except for the last one, which is the target of the effect,
which will be decided at runtime when the effect is executed. Therefore, all effects after being loaded are
functions with a single arg, the target.

Effects can be used by items or by things like special attacks, activated traps, etc.

Note:
    The target arg should always be the last one, since the rest will be filled when reading from the registry,
    producing a partial, and the registry doesn't know about the names of the args so they don't get filled by
    keyword but by order.
"""


def heal(hp, target):
    """
    Instantly heal the target for a certain amount of hp.

    Args:
        target (Actor): Actor that receives the healing effect.
        hp (int): Amount of hp to heal the target for when the effect is activated.
    """
    target.hp += hp
