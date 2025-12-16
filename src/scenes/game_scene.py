import pygame as pg
import threading
import time
import math
from src.scenes.scene import Scene
from src.maps.map import Map
from src.scenes.battle_scene import BattleScene
from src.scenes.navigation_overlay import NavigationOverlay
from src.scenes.setting_overlay import SettingOverlay
from src.scenes.backpack_overlay import BackpackOverlay
from src.scenes.shop_overlay import ShopOverlay
from src.interface.components import Button
from src.interface.components.chat_overlay import ChatOverlay
from src.core import GameManager, OnlineManager
from src.utils import load_tmx, Position, Direction, GameSettings, PositionCamera, Teleport
from src.utils import Logger, PositionCamera, GameSettings, Position
from src.core.services import sound_manager
from src.core.services import scene_manager, sound_manager, input_manager
from src.sprites import Sprite,Animation
from typing import override, Dict, Tuple
from src.scenes.catch_scene import CatchScene
from src.entities.other_player import OtherPlayer
class GameScene(Scene):
    game_manager: GameManager
    online_manager: OnlineManager | None
    sprite_online: Sprite
    navigation_button:Button
    setting_button:Button
    backpack_button:Button
    map:Map
    
    def __init__(self):
        super().__init__()
        
        self.font = pg.font.Font("assets/fonts/Minecraft.ttf", 20)
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        
        #遇到bush的提醒圖片
        self.on_bush=False
        self.bush_icon = pg.image.load("assets/images/exclamation.png").convert_alpha()
        self.bush_icon = pg.transform.scale(self.bush_icon, (32, 32))

        #遇到god的提醒圖片
        self.on_god=False
        self.god_icon = pg.image.load("assets/images/ingame_ui/baricon3.png").convert_alpha()
        self.god_icon = pg.transform.scale(self.god_icon, (32, 32))
        
        #傳送
        self.navigation_path = []
        self.is_navigating = False
        self.pending_navigation_target: Position | None = None
        
        
        self.shop_button = Button(
        "UI/button_shop.png","UI/button_shop_hover.png",
        px+230, py-500, 70, 70,
        lambda: self.shop_overlay.show()    
        )
        self.navigation_button = Button(
        "UI/button_play.png", "UI/button_play_hover.png",
        px+330, py-500, 70, 70,
        lambda: self.navigation_overlay.show()    
        )
        self.setting_button = Button(
        "UI/button_setting.png", "UI/button_setting_hover.png",
        px+430, py-500, 70, 70,
        lambda: self.setting_overlay.show()     
        )
        self.backpack_button = Button(
        "UI/button_backpack.png", "UI/button_backpack_hover.png",
        px+530, py-500, 70, 70,
        lambda: self.backpack_overlay.show()     
        )
        
        # Game Manager
        manager = GameManager.load("saves/backup.json")
        if manager is None:
            Logger.error("Failed to load game manager")
            exit(1)
        self.game_manager = manager
        self.backpack_overlay = BackpackOverlay(self.game_manager)
        self.shop_overlay = ShopOverlay(self.game_manager)
        self.setting_overlay = SettingOverlay(self.game_manager)
        # Online Manager
        if GameSettings.IS_ONLINE:
            self.online_manager = OnlineManager()
            self.chat_overlay = ChatOverlay(
                send_callback=self.online_manager.send_chat,
                get_messages=self.online_manager.get_recent_chat
            )
        else:
            self.online_manager = None
        self.online_players: dict[int, OtherPlayer] = {}
        self.sprite_online = Sprite("ingame_ui/options1.png", (GameSettings.TILE_SIZE, GameSettings.TILE_SIZE))
        self._chat_bubbles: Dict[int, Tuple[str, str]] = {}
        self._last_chat_id_seen = 0
        
        #navigation
        places = {
            "Gym": Position(24,25),
            "Home": Position(16,30),
            "House":Position(54,16)
        }
        self.arrow_image = pg.image.load("assets/images/UI/raw/UI_Flat_IconArrow01a.png").convert_alpha()
        self.arrow_image = pg.transform.scale(self.arrow_image, (25, 25))
        self.nav_target_image = pg.image.load("assets/images/UI/raw/UI_Flat_IconCross01a.png").convert_alpha()
        self.nav_target_image = pg.transform.scale(self.nav_target_image, (25, 25))
        self.navigation_overlay = NavigationOverlay(self, places,self.game_manager)
        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 103 Pallet Town.ogg")
        self.backpack_overlay.hide()
        self.shop_overlay.hide()
        self.setting_overlay.hide()
        self.navigation_overlay.hide()
        if self.online_manager:
            self.online_manager.enter()
        
    def enter_bush(self):
        scene_manager.change_scene(CatchScene(self.game_manager.player))

    @override
    def exit(self) -> None:
        if self.online_manager:
            self.online_manager.exit()
    
    def bfs_path(self, game_map,start: Position, goal: Position):
        
        start_tile = (start.x // GameSettings.TILE_SIZE, start.y // GameSettings.TILE_SIZE)
        goal_tile = (goal.x, goal.y)

        from collections import deque
        queue = deque([start_tile])
        came_from = {start_tile: None}

        directions = [(0,1),(1,0),(0,-1),(-1,0)]  # 下、右、上、左

        while queue:
            current = queue.popleft()
            if current == goal_tile:
                break

            for dx, dy in directions:
                nx, ny = current[0]+dx, current[1]+dy
                width = self.game_manager.current_map.tmxdata.width 
                height = self.game_manager.current_map.tmxdata.height 
                if 0 <= nx < width and 0 <= ny < height and  self.game_manager.current_map.is_walkable(nx, ny,self.game_manager):
                    next_tile = (nx, ny)
                    if next_tile not in came_from:
                        queue.append(next_tile)
                        came_from[next_tile] = current

        # 重建路徑
        path = []
        current = goal_tile
        while current != start_tile:
            path.append(current)
            current = came_from.get(current)
            if current is None:
                return []
        path.reverse()
        return path
    
    def start_navigation(self, target_pos: Position):
        if target_pos is None or self.game_manager.player is None:
            return
        path_tiles = self.bfs_path(self.game_manager.current_map, self.game_manager.player.position, target_pos)
        # 將 tile 轉回 pixel
        self.navigation_path = [
            Position(x*GameSettings.TILE_SIZE, y*GameSettings.TILE_SIZE) for x,y in path_tiles
        ]
        self.navigation_index = 0
        self.is_navigating = True

    
    @override
    def update(self, dt: float):
        # Check if there is assigned next scene
        
        self.game_manager.try_switch_map()
        '''if not self.is_navigating and hasattr(self, "pending_navigation_target"):
            self.start_navigation(self.pending_navigation_target)
            del self.pending_navigation_target
        if self.is_navigating and self.navigation_path == []:
            if hasattr(self, "pending_navigation_target"):
                self.game_manager.switch_map("map.tmx")'''
                
        # Update player and other data
        if self.game_manager.player:
            if not (self.chat_overlay and self.chat_overlay.is_open):
                self.game_manager.player.update(dt)
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.update(dt)
        for shopnpc in self.game_manager.current_shop_npc:
            shopnpc.update(dt)
            
        for npc in self.game_manager.current_enemy_trainers:
            if npc.detected:
                if input_manager.key_down(pg.K_r):
                    battle = BattleScene(self.game_manager.bag._monsters_data,self.game_manager.bag._items_data)
                    scene_manager.set_scene_instance(battle)
                
        for npc in self.game_manager.current_shop_npc:
            if npc.detected:
                if input_manager.key_down(pg.K_e):
                    self.shop_overlay.show()
                
        if self.online_manager and self.game_manager.player:
            list_online = self.online_manager.get_list_players()
            for data in list_online:
                pid = data["id"]
                # 若還沒有這個玩家的實例，建立新的 OtherPlayer
                if pid not in self.online_players:
                    self.online_players[pid] = OtherPlayer(
                        data["x"], data["y"], self.game_manager, pid
                    )
                # 更新玩家資料（位置、方向、移動狀態）
                self.online_players[pid].update_from_data(data)

            # 同步更新所有線上玩家動畫
            for player in self.online_players.values():
                player.update(dt)

        if self.game_manager.check_bush(pg.Rect(self.game_manager.player.position.x, 
                                                self.game_manager.player.position.y, 
                                                GameSettings.TILE_SIZE, 
                                                GameSettings.TILE_SIZE)):
            self.on_bush=True
            if input_manager.key_down(pg.K_q):
                catch = CatchScene(self.game_manager)
                scene_manager.set_scene_instance(catch)
        else:
            self.on_bush=False
        
        if self.game_manager.check_god(pg.Rect(self.game_manager.player.position.x, 
                                                self.game_manager.player.position.y, 
                                                GameSettings.TILE_SIZE, 
                                                GameSettings.TILE_SIZE)):
            self.on_god=True
            if input_manager.key_down(pg.K_e):
                catch = CatchScene(self.game_manager)
                scene_manager.set_scene_instance(catch)
        else:
            self.on_god=False
        
        # Update others
        self.game_manager.bag.update(dt)
        
        #TODO: UPDATE CHAT OVERLAY:

        if self.chat_overlay:
            if input_manager.key_pressed(pg.K_e):
                self.chat_overlay.open()
            self.chat_overlay.update(dt)
        # Update chat bubbles from recent messages

        # This part's for the chatting feature, we've made it for you.
        if self.online_manager:
            try:
                msgs = self.online_manager.get_recent_chat(50)
                max_id = self._last_chat_id_seen
                now = time.monotonic()
                for m in msgs:
                    mid = int(m.get("id", 0))
                    if mid <= self._last_chat_id_seen:
                        continue
                    sender = int(m.get("from", -1))
                    text = str(m.get("text", ""))
                    if sender >= 0 and text:
                        self._chat_bubbles[sender] = (text, now + 5.0)
                    if mid > max_id:
                        max_id = mid
                self._last_chat_id_seen = max_id
            except Exception:
                pass
        
        if self.game_manager.player is not None and self.online_manager is not None:
            _ = self.online_manager.update(
                self.game_manager.player.position.x, 
                self.game_manager.player.position.y,
                self.game_manager.current_map.path_name,
                self.game_manager.player.direction.name, 
                self.game_manager.player.is_moving
            )
        if self.shop_overlay.visible==False and self.navigation_overlay.visible==False and self.setting_overlay.visible==False and self.backpack_overlay.visible==False:
            self.shop_button.update(dt)
            self.navigation_button.update(dt)
            self.setting_button.update(dt)
            self.backpack_button.update(dt)
        if self.shop_overlay.visible==True:
            self.shop_button.img_button=self.shop_button.img_button_default
        if self.navigation_overlay.visible==True:
            self.navigation_button.img_button=self.navigation_button.img_button_default
        if self.setting_overlay.visible==True:
            self.setting_button.img_button=self.setting_button.img_button_default
        if self.backpack_overlay.visible==True:
            self.backpack_button.img_button=self.backpack_button.img_button_default
        
        self.shop_overlay.update(dt)
        self.navigation_overlay.update(dt)
        self.setting_overlay.update(dt)
        self.backpack_overlay.update(dt)
        
            
        if getattr(self, "is_navigating", False) and self.navigation_index < len(self.navigation_path):
            target = self.navigation_path[self.navigation_index]
            player_pos = self.game_manager.player.position

            dx = target.x - player_pos.x
            dy = target.y - player_pos.y
            speed = 200
            dist = (dx**2 + dy**2)**0.5

            if dist < 2:
                self.navigation_index += 1
            else:
                self.game_manager.player.position.x += dx / dist * speed * dt
                self.game_manager.player.position.y += dy / dist * speed * dt
            
            if abs(dx) > abs(dy):
                if dx > 0:
                    self.game_manager.player.direction=Direction.RIGHT
                else:
                    self.game_manager.player.direction=Direction.LEFT
            else:
                if dy > 0:
                    self.game_manager.player.direction=Direction.DOWN
                else:
                    self.game_manager.player.direction=Direction.UP
            self.game_manager.player.update(dt)
            self.game_manager.player.animation.update(dt)
            #到達
            if self.navigation_index >= len(self.navigation_path):
                self.is_navigating = False
                
        '''if self.is_navigating == False:
            self.is_navigating = False
            # 如果有 pending_navigation_target，表示剛到門口
            if getattr(self, "pending_navigation_target", None) is not None:
                # 切換地圖
                print(223456789)
                #self.game_manager.switch_map("map.tmx") 
                self.game_manager.player.position.y-=4
                # 導航到最終目的地
                self.start_navigation(self.pending_navigation_target)
                self.pending_navigation_target = None'''
            
    def _draw_chat_bubbles(self, screen: pg.Surface, camera: PositionCamera) -> None:
        now = time.monotonic()

        expired = [pid for pid, (_, ts) in self._chat_bubbles.items() if ts <= now]
        for pid in expired:
            self._chat_bubbles.pop(pid, None)

        if not self._chat_bubbles:
            return

        font = pg.font.SysFont("arial", 14)

        # local player
        if self.game_manager.player:
            local_pid = self.online_manager.player_id
            if local_pid in self._chat_bubbles:
                text, _ = self._chat_bubbles[local_pid]
                self._draw_chat_bubble_for_pos(
                    screen,
                    camera,
                    self.game_manager.player.position,
                    text,
                    font
                )

        # other players
        players = self.online_manager.get_list_players()
        for p in players:
            pid = p["id"]
            if pid not in self._chat_bubbles:
                continue
            if p["map"] != self.game_manager.current_map.path_name:
                continue

            world_pos = Position(p["x"], p["y"])
            text, _ = self._chat_bubbles[pid]
            self._draw_chat_bubble_for_pos(screen, camera, world_pos, text, font)

    def _draw_chat_bubble_for_pos(self,screen: pg.Surface,camera: PositionCamera,
                                world_pos: Position,text: str,font: pg.font.Font):
        screen_pos = camera.transform_position_as_position(world_pos)
        text_surf = font.render(text, True, (0, 0, 0))

        padding = 6
        w = text_surf.get_width() + padding * 2
        h = text_surf.get_height() + padding * 2

        bubble_x = screen_pos.x - w // 2
        bubble_y = screen_pos.y - 40

        bg = pg.Surface((w, h), pg.SRCALPHA)
        bg.fill((255, 255, 255, 230))

        screen.blit(bg, (bubble_x, bubble_y))
        screen.blit(text_surf, (bubble_x + padding, bubble_y + padding))

    
    @override
    def draw(self, screen: pg.Surface):    
        
            
        if self.game_manager.player:
            
            '''
            [TODO HACKATHON 3]
            Implement the camera algorithm logic here
            Right now it's hard coded, you need to follow the player's positions
            you may use the below example, but the function still incorrect, you may trace the entity.py
            
            camera = self.game_manager.player.camera
            '''
            camera = self.game_manager.player.camera
            self.game_manager.current_map.draw(screen, camera)
            if self.is_navigating:        
                for i in range(len(self.navigation_path) - 1):
                    cur = self.navigation_path[i]
                    nex = self.navigation_path[i + 1]
                    px = cur.x - camera.x
                    py = cur.y - camera.y
                    # 箭頭指向下一個 tile
                    dx = nex.x - cur.x
                    dy = nex.y - cur.y
                    angle = math.degrees(math.atan2(-dy, dx))  # pygame 角度是反向的
                    # 旋轉箭頭
                    rotated = pg.transform.rotate(self.arrow_image, angle)
                    rect = rotated.get_rect(center = (px + GameSettings.TILE_SIZE//2,
                                                    py + GameSettings.TILE_SIZE//2))
                    screen.blit(rotated, rect)
                if self.navigation_path != []:
                    target = self.navigation_path[len(self.navigation_path) - 1]
                    px = target.x - camera.x
                    py = target.y - camera.y
                    screen.blit(self.nav_target_image, (px + GameSettings.TILE_SIZE//2-12, py + GameSettings.TILE_SIZE//2-12))
            self.game_manager.player.draw(screen, camera)
            
            minimap_pos = (10, 10)
            
            if self.game_manager.current_map_key=="map.tmx":
                self.game_manager.current_map.draw_minimap(screen, minimap_pos,scale=0.08)
            elif self.game_manager.current_map_key=="home.tmx":
                self.game_manager.current_map.draw_minimap(screen, minimap_pos,scale=0.2)
            elif self.game_manager.current_map_key=="gym.tmx":
                self.game_manager.current_map.draw_minimap(screen, minimap_pos,scale=0.2)
            elif self.game_manager.current_map_key=="god.tmx":
                self.game_manager.current_map.draw_minimap(screen, minimap_pos,scale=0.1)
            
            player_pos = self.game_manager.player.position
            map_obj = self.game_manager.current_map

            scale_x = map_obj._minimap_surface.get_width() / (map_obj.tmxdata.width * GameSettings.TILE_SIZE)
            scale_y = map_obj._minimap_surface.get_height() / (map_obj.tmxdata.height * GameSettings.TILE_SIZE)
            mini_x = minimap_pos[0] + round(player_pos.x * scale_x)
            mini_y = minimap_pos[1] + round(player_pos.y * scale_y)

            pg.draw.circle(screen, (255,0,0), (mini_x, mini_y), 5)
            
        else:
            camera = PositionCamera(0, 0)
            self.game_manager.current_map.draw(screen, camera)
        
        for enemy in self.game_manager.current_enemy_trainers:
            enemy.draw(screen, camera)

        for shopnpc in self.game_manager.current_shop_npc:
            shopnpc.draw(screen, camera)
            
        self.game_manager.bag.draw(screen)
        
        if self.chat_overlay:
            self.chat_overlay.draw(screen)
                    
        if self.online_manager and self.game_manager.player:
            for player in self.online_players.values():
                # 只顯示在當前地圖的玩家
                if player.map == self.game_manager.current_map.path_name:
                    player.draw(screen, self.game_manager.player.camera)
                    
        # try:
            #     self._draw_chat_bubbles(...)
            # except Exception:
            #     pass
                    
        if self.on_bush:
            icon_x = self.game_manager.player.position.x - camera.x+5
            icon_y = self.game_manager.player.position.y - camera.y - 20 
            screen.blit(self.bush_icon, (icon_x, icon_y))
            screen.blit(self.font.render("Press Q to catch monster!", True, (255,55,55)), (self.game_manager.player.position.x - camera.x, self.game_manager.player.position.y - camera.y+80 ))


        if self.on_god:
            icon_x = self.game_manager.player.position.x - camera.x+5
            icon_y = self.game_manager.player.position.y - camera.y - 20 
            screen.blit(self.god_icon, (icon_x, icon_y))
            screen.blit(self.font.render("Press E", True, (255,55,55)), (self.game_manager.player.position.x - camera.x, self.game_manager.player.position.y - camera.y+80 ))

                    
        for npc in self.game_manager.current_enemy_trainers:
            if npc.detected:
                screen.blit(self.font.render("Press E to battle!", True, (255,55,55)), (self.game_manager.player.position.x - camera.x, self.game_manager.player.position.y - camera.y+80 ))
                
        for npc in self.game_manager.current_shop_npc:
            if npc.detected:
                screen.blit(self.font.render("Press E to shop!", True, (255,55,55)), (self.game_manager.player.position.x - camera.x, self.game_manager.player.position.y - camera.y+80 ))
        
        


        self.navigation_button.draw(screen)
        self.setting_button.draw(screen)
        self.backpack_button.draw(screen)
        self.shop_button.draw(screen)
        
        self.navigation_overlay.draw(screen)
        self.setting_overlay.draw(screen)
        self.backpack_overlay.draw(screen)
        self.shop_overlay.draw(screen)
        
