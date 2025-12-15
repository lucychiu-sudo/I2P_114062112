from __future__ import annotations
import pygame as pg
from .entity import Entity
from src.core.services import input_manager
from src.utils import Position, PositionCamera, Direction, GameSettings
from src.utils import Position, PositionCamera, GameSettings, Logger
from src.core import GameManager
import math
from typing import override

class Player(Entity):
    speed: float = 4.0 * GameSettings.TILE_SIZE
    game_manager: GameManager

    def __init__(self, x: float, y: float, game_manager: GameManager) -> None:
        super().__init__(x, y, game_manager)
        # teleport cool down
        self.teleport_cool_time = 0.3

    @override
    def update(self, dt: float) -> None:
        dis = Position(0, 0)
        if input_manager.key_down(pg.K_LEFT) or input_manager.key_down(pg.K_a):
            dis.x -= 1
            self.direction=Direction.LEFT
        if input_manager.key_down(pg.K_RIGHT) or input_manager.key_down(pg.K_d):
            dis.x += 1
            self.direction=Direction.RIGHT
        if input_manager.key_down(pg.K_UP) or input_manager.key_down(pg.K_w):
            dis.y -= 1
            self.direction=Direction.UP
        if input_manager.key_down(pg.K_DOWN) or input_manager.key_down(pg.K_s):
            dis.y += 1
            self.direction=Direction.DOWN
        length = math.hypot(dis.x, dis.y)
        if length > 0:
            dis.x = dis.x / length * self.speed * dt
            dis.y = dis.y / length * self.speed * dt

        self.is_moving = (dis.x != 0 or dis.y != 0)
        
        self.position.x += dis.x
        if self.game_manager.check_collision(pg.Rect(self.position.x, self.position.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)):
            self.position.x -= dis.x

    
        self.position.y += dis.y
        if self.game_manager.check_collision(pg.Rect(self.position.x, self.position.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)):
            self.position.y -= dis.y

        # Check teleportation
        self.teleport_cool_time-=dt
        if self.teleport_cool_time<=0:
            tp = self.game_manager.current_map.check_teleport(self.position)
            if tp:
                dest = tp.destination
                self.game_manager.switch_map(dest)
                self.teleport_cool_time=0.3
                
        super().update(dt)

    @override
    def draw(self, screen: pg.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        
    @override
    def to_dict(self) -> dict[str, object]:
        return super().to_dict()
    
    @classmethod
    @override
    def from_dict(cls, data: dict[str, object], game_manager: GameManager) -> Player:
        return cls(data["x"] * GameSettings.TILE_SIZE, data["y"] * GameSettings.TILE_SIZE, game_manager)

