import pygame as pg
import pytmx
from src.core import GameManager, OnlineManager
from src.utils import load_tmx, Position, GameSettings, PositionCamera, Teleport

class Map:
    # Map Properties
    path_name: str
    tmxdata: pytmx.TiledMap
    # Position Argument
    spawn: Position
    teleporters: list[Teleport]
    # Rendering Properties
    _surface: pg.Surface
    _collision_map: list[pg.Rect]

    def __init__(self, path: str, tp: list[Teleport], spawn: Position):
        self.path_name = path
        self.tmxdata = load_tmx(path)
        self.spawn = spawn
        self.teleporters = tp
        
        pixel_w = self.tmxdata.width * GameSettings.TILE_SIZE
        pixel_h = self.tmxdata.height * GameSettings.TILE_SIZE

        # Prebake the map
        self._surface = pg.Surface((pixel_w, pixel_h), pg.SRCALPHA)
        self._render_all_layers(self._surface)
        
        # Prebake the collision map
        self._collision_map = self._create_collision_map()
        self._bush_map = self._create_bush_map()
        self._god_map = self._create_god_map()
        
    
        
    def update(self, dt: float):
        return

    def draw(self, screen: pg.Surface, camera: PositionCamera):
        screen.blit(self._surface, camera.transform_position(Position(0, 0)))
        
        
        # Draw the hitboxes collision map
        if GameSettings.DRAW_HITBOXES:
            for rect in self._collision_map:
                pg.draw.rect(screen, (255, 0, 0), camera.transform_rect(rect), 1)
        
        
        
    def draw_minimap(self, screen: pg.Surface, minimap_pos,scale):
        #像畫一般map一樣，只是依scale縮小map大小
        minimap_pixel_w = self.tmxdata.width * GameSettings.TILE_SIZE*scale
        minimap_pixel_h = self.tmxdata.height * GameSettings.TILE_SIZE*scale

        self._minimap_surface = pg.Surface((minimap_pixel_w, minimap_pixel_h), pg.SRCALPHA)
        self._render_all_layers(self._minimap_surface,scale)
        screen.blit(self._minimap_surface, minimap_pos)
        rect = self._minimap_surface.get_rect(topleft= minimap_pos)
        pg.draw.rect(screen, (0, 0, 0), rect, 3)
        
    def check_collision(self, pos: Position) -> bool:
        player_rect = pg.Rect(pos.x, pos.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        for r in self._collision_map:
            if player_rect.colliderect(r):
                return True
        '''
        [TODO HACKATHON 4]
        Return True if collide if rect param collide with self._collision_map
        Hint: use API colliderect and iterate each rectangle to check
        '''
        return False
    
    def is_walkable(self, tile_x, tile_y,game_manager):
        px = tile_x * GameSettings.TILE_SIZE
        py = tile_y * GameSettings.TILE_SIZE
        rect = pg.Rect(px, py, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)

        for r in self._collision_map:
            if rect.colliderect(r):
                return False
        if game_manager:
            for npc in game_manager.current_enemy_trainers + game_manager.current_shop_npc:
                npc_rect = pg.Rect(npc.position.x, npc.position.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
                if rect.colliderect(npc_rect):
                    return False
            
                
                
        return True
        
    def check_bush(self, pos: Position) -> bool:
        player_rect = pg.Rect(pos.x, pos.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        for r in self._bush_map:
            if player_rect.colliderect(r):
                return True
        return False
        
    def check_god(self, pos: Position) -> bool:
        player_rect = pg.Rect(pos.x, pos.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        for r in self._god_map:
            if player_rect.colliderect(r):
                return True
        return False
        
        
    def check_teleport(self, pos: Position) -> Teleport | None:
        '''[TODO HACKATHON 6] 
        Teleportation: Player can enter a building by walking into certain tiles defined inside saves/*.json, and the map will be changed
        Hint: Maybe there is an way to switch the map using something from src/core/managers/game_manager.py called switch_... 
        '''
        player_rect = pg.Rect(pos.x, pos.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
        for tp in self.teleporters:
            tp_rect = pg.Rect(tp.pos.x, tp.pos.y, GameSettings.TILE_SIZE, GameSettings.TILE_SIZE)
            if player_rect.colliderect(tp_rect):
                return tp
        return None

    
    
    
    
    def _render_all_layers(self, target: pg.Surface, scale: float = 1.0) -> None:
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                self._render_tile_layer(target, layer, scale)
            

    def _render_tile_layer(self, target: pg.Surface, layer: pytmx.TiledTileLayer, scale: float = 1.0) -> None:
        tile_size = round(GameSettings.TILE_SIZE * scale)
        for x, y, gid in layer:
            if gid == 0:
                continue
            image = self.tmxdata.get_tile_image_by_gid(gid)
            if image is None:
                continue

            image = pg.transform.scale(image, (tile_size, tile_size))
            target.blit(image, (x * tile_size, y * tile_size))
    
    def _create_collision_map(self) -> list[pg.Rect]:
        rects = []
        
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and ("collision" in layer.name.lower() or "house" in layer.name.lower()):
                for x, y, gid in layer:
                    if gid != 0:
                        rects.append(
                            pg.Rect(
                                x * GameSettings.TILE_SIZE,
                                y * GameSettings.TILE_SIZE,
                                GameSettings.TILE_SIZE,
                                GameSettings.TILE_SIZE
                            )
                    )
        return rects

    def _create_bush_map(self) -> list[pg.Rect]:
        rects = []
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and ("PokemonBush" in layer.name):
                for x, y, gid in layer:
                    if gid != 0:
                        rects.append(
                            pg.Rect(
                                x * GameSettings.TILE_SIZE,
                                y * GameSettings.TILE_SIZE,
                                GameSettings.TILE_SIZE,
                                GameSettings.TILE_SIZE
                            )
                    )
        return rects
    
    def _create_god_map(self) -> list[pg.Rect]:
        rects = []
        for layer in self.tmxdata.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer) and ("god" in layer.name):
                for x, y, gid in layer:
                    if gid != 0:
                        rects.append(
                            pg.Rect(
                                x * GameSettings.TILE_SIZE,
                                y * GameSettings.TILE_SIZE,
                                GameSettings.TILE_SIZE,
                                GameSettings.TILE_SIZE
                            )
                    )
        return rects
    
    @classmethod
    def from_dict(cls, data: dict) -> "Map":
        tp = [Teleport.from_dict(t) for t in data["teleport"]]
        pos = Position(data["player"]["x"] * GameSettings.TILE_SIZE, data["player"]["y"] * GameSettings.TILE_SIZE)
        return cls(data["path"], tp, pos)

    def to_dict(self):
        return {
            "path": self.path_name,
            "teleport": [t.to_dict() for t in self.teleporters],
            "player": {
                "x": self.spawn.x // GameSettings.TILE_SIZE,
                "y": self.spawn.y // GameSettings.TILE_SIZE,
            }
        }
