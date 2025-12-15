# src/entity/other_player.py
from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager
from src.utils import Position, PositionCamera, Direction, GameSettings
from src.utils import Position, PositionCamera, GameSettings, Logger
from src.core import GameManager
import math
from typing import override

class OtherPlayer(Entity):
    def __init__(self, x: float, y: float, game_manager, player_id: int):
        super().__init__(x, y, game_manager)
        self.player_id = player_id
        self.is_moving = False
        self.direction = Direction.DOWN
        self.map = ""

    def update_from_data(self, data: dict):
        """更新位置、方向與移動狀態"""
        self.position.x = data["x"]
        self.position.y = data["y"]
        self.direction = Direction[data["direction"]]
        self.is_moving = data["is_moving"]
        self.map = data["map"]

    def update(self, dt: float):
        """更新動畫，僅在移動時播放走路動畫"""
        self.animation.update_pos(self.position)
        if self.is_moving:
            self.animation.update(dt)
        self.self_direction()
