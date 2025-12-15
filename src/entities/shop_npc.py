from __future__ import annotations
import pygame
from enum import Enum
from dataclasses import dataclass
from typing import override

from .entity import Entity
from src.sprites import Sprite
from src.sprites import Animation
from src.core import GameManager
from src.core.services import input_manager, scene_manager
from src.utils import GameSettings, Direction, Position, PositionCamera


class EnemyTrainerClassification(Enum):
    STATIONARY = "stationary"


@dataclass
class IdleMovement:
    def update(self, enemy: "ShopNPC", dt: float) -> None:
        return

class ShopNPC(Entity):
    classification: EnemyTrainerClassification
    max_tiles: int | None
    _movement: IdleMovement
    warning_sign: Sprite
    detected: bool
    los_direction: Direction

    @override
    def __init__(
        self,
        x: float,
        y: float,
        game_manager: GameManager,
        classification: EnemyTrainerClassification = EnemyTrainerClassification.STATIONARY,
        max_tiles: int | None = 2,
        facing: Direction | None = None,
    ) -> None:
        super().__init__(x, y, game_manager)
        self.animation = Animation(
            "character/ow2.png", ["down", "left", "right", "up"], 4,
            (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        )
        self.classification = classification

        self.max_tiles = max_tiles
        #如果敵人不會動
        if classification == EnemyTrainerClassification.STATIONARY:
            self._movement = IdleMovement()
            #要有面對一個方向，不然就報錯
            if facing is None:
                raise ValueError("Idle EnemyTrainer requires a 'facing' Direction at instantiation")
            #呼叫_set_direction()來設定動畫和視線方向
            self._set_direction(facing)
        else:
            raise ValueError("Invalid classification")
        #設好驚嘆號圖片和位置
        self.warning_sign = Sprite("exclamation.png", (40, 40))
        self.warning_sign.update_pos(Position(x + GameSettings.TILE_SIZE // 4, y - GameSettings.TILE_SIZE // 2))
        #先預設成沒有感應到
        self.detected = False

    @override
    def update(self, dt: float) -> None:
        self._movement.update(self, dt)
        #檢測玩家有沒有在前面視窗
        self._has_los_to_player()
        
        if self.detected and input_manager.key_pressed(pygame.K_SPACE):
            pass
        #更新位置
        self.animation.update_pos(self.position)

    @override
    def draw(self, screen: pygame.Surface, camera: PositionCamera) -> None:
        super().draw(screen, camera)
        #如果感應到玩家，劃出驚嘆號
        if self.detected:
            self.warning_sign.draw(screen, camera)
        #如果debug模式開啟，視窗畫黃色框框
        if GameSettings.DRAW_HITBOXES:
            los_rect = self._get_los_rect()
            if los_rect is not None:
                pygame.draw.rect(screen, (255, 255, 0), camera.transform_rect(los_rect), 1)

    def _set_direction(self, direction: Direction) -> None:
        self.direction = direction
        if direction == Direction.RIGHT:
            self.animation.switch("right")
        elif direction == Direction.LEFT:
            self.animation.switch("left")
        elif direction == Direction.DOWN:
            self.animation.switch("down")
        else:
            self.animation.switch("up")
        #判斷視窗方向
        self.los_direction = self.direction

    def _get_los_rect(self) -> pygame.Rect | None:
        #計算NPC的視窗框框
        width = 1* GameSettings.TILE_SIZE
        if self.los_direction == Direction.UP:
            return pygame.Rect(self.position.x, self.position.y - width, GameSettings.TILE_SIZE, width)
        elif self.los_direction == Direction.DOWN:
            return pygame.Rect(self.position.x, self.position.y + GameSettings.TILE_SIZE, GameSettings.TILE_SIZE, width)
        elif self.los_direction == Direction.LEFT:
            return pygame.Rect(self.position.x - width, self.position.y, width, GameSettings.TILE_SIZE)
        elif self.los_direction == Direction.RIGHT:
            return pygame.Rect(self.position.x + GameSettings.TILE_SIZE, self.position.y, width, GameSettings.TILE_SIZE)
        return None
    
    def _has_los_to_player(self) -> None:
        player = self.game_manager.player
        if player is None:
            self.detected = False
            return
        #取得視窗框框位置
        los_rect = self._get_los_rect()
        if los_rect is None:
            self.detected = False
            return
        player_rect = pygame.Rect(player.position.x, player.position.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        #如果玩家在視窗框框內
        self.detected = los_rect.colliderect(player_rect)
        #切換成感應到玩家
        if self.detected:
            self.warning_sign.update_pos(Position(self.position.x + GameSettings.TILE_SIZE // 4,
                                                self.position.y - GameSettings.TILE_SIZE // 2))
            

    @classmethod
    @override
    def from_dict(cls, data: dict, game_manager: GameManager) -> "ShopNPC":
        classification = EnemyTrainerClassification(data.get("classification", "stationary"))
        max_tiles = data.get("max_tiles")
        facing_val = data.get("facing")
        facing: Direction | None = None
        if facing_val is not None:
            if isinstance(facing_val, str):
                facing = Direction[facing_val]
            elif isinstance(facing_val, Direction):
                facing = facing_val
        if facing is None and classification == EnemyTrainerClassification.STATIONARY:
            facing = Direction.DOWN
        return cls(
            data["x"] * GameSettings.TILE_SIZE,
            data["y"] * GameSettings.TILE_SIZE,
            game_manager,
            classification,
            max_tiles,
            facing,
        )

    @override
    def to_dict(self) -> dict[str, object]:
        base: dict[str, object] = super().to_dict()
        base["classification"] = self.classification.value
        base["facing"] = self.direction.name
        base["max_tiles"] = self.max_tiles
        return base