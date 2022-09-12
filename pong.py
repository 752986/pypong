from typing import TypeAlias
import pygame

Vec2: TypeAlias = tuple[float, float]

class GameObject:
    pos: Vec2
    vel: Vec2

    # TODO: update and draw definitions

class Ball:
    pos: Vec2 = (0, 0)
    vel: Vec2 = (0, 0)
