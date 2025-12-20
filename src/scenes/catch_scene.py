# src/scenes/catch_scene.py
import pygame as pg
from src.scenes.scene import Scene
from src.core.services import scene_manager,sound_manager
import random
import os
import pygame as pg
from src.utils import GameSettings
from src.interface.components import Button
from src.sprites import BackgroundSprite
from src.core.services import input_manager
from src.utils import Logger
from src.scenes.scene import Scene 
from src.sprites import Animation
from typing import override
ASSET = "assets/images/"
from src.core.managers.game_manager import GameManager

    
def crop_image(image, x, y, w, h):
        rect = pg.Rect(x, y, w, h)
        return image.subsurface(rect).copy()

    
class CatchScene(Scene):
    background: BackgroundSprite
    game_manager: "GameManager"
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.finished=False
        self.monsters_list= [
            { "name": "Pikachu",   "hp": 100, "max_hp": 100, "level": 14,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite1.png" },
            { "name": "Charizard", "hp": 200, "max_hp": 200, "level": 12,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite2.png" },
            { "name": "Blastoise", "hp": 180, "max_hp": 180, "level": 33,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite3.png" },
            { "name": "Venusaur",  "hp": 160, "max_hp": 160, "level": 25,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite4.png" },
            { "name": "Gengar",    "hp": 140, "max_hp": 140, "level": 21,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite5.png" },
            { "name": "Dragonite", "hp": 220, "max_hp": 220, "level": 14,"attack":20,"defense":5,"element":"water", "sprite_path": "menu_sprites/menusprite6.png" },
            { "name": "Mouse",     "hp": 240, "max_hp": 240, "level": 15,"attack":20,"defense":5,"element":"fire", "sprite_path": "menu_sprites/menusprite7.png" },
            { "name": "FireMouse", "hp": 280, "max_hp": 280, "level": 17,"attack":20,"defense":5,"element":"fire", "sprite_path": "menu_sprites/menusprite8.png" },
            { "name": "GiantMouse", "hp": 300, "max_hp": 300, "level": 11,"attack":20,"defense":5,"element":"fire", "sprite_path": "menu_sprites/menusprite9.png" },
            { "name": "PurpleMouse", "hp": 150, "max_hp": 150, "level": 9,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite10.png" },
            { "name": "PurpleSnake", "hp": 200, "max_hp": 200, "level": 22,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite11.png" },
            { "name": "Dophin",      "hp": 220, "max_hp": 220, "level": 18,"attack":20,"defense":5,"element":"water", "sprite_path": "menu_sprites/menusprite12.png" },
            { "name": "BigDophin",   "hp": 230, "max_hp": 230, "level": 19,"attack":20,"defense":5,"element":"water", "sprite_path": "menu_sprites/menusprite13.png" },
            { "name": "LargeDophin", "hp": 250, "max_hp": 250, "level": 20,"attack":20,"defense":5,"element":"water", "sprite_path": "menu_sprites/menusprite14.png" },
            { "name": "Bug",         "hp": 100, "max_hp": 100, "level": 17,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite15.png" },
            { "name": "UglyBug",     "hp": 130, "max_hp": 130, "level": 15,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite16.png" }
            ]
        self.monster=random.choice(self.monsters_list)
        self.background = BackgroundSprite("backgrounds/background3.png")
        self.font = pg.font.Font(None, 36)
        self.image_path=self.monster["sprite_path"] if isinstance(self.monster, dict) else self.monster.sprite_path
        self.animation_path=self.image_path.replace("menu","")
        self.animation_path=self.animation_path.replace("_","")
        self.animation_path=self.animation_path.replace(".png","_idle.png")
        self.animation=Animation(self.animation_path,["idle"],4,(300,300))
        self.animation.rect.x,self.animation.rect.y=(600,200)
        self.state = "idle"

        # 寶可球圖片
        self.ball_img = pg.image.load("assets/images/ingame_ui/ball.png").convert_alpha()
        self.ball_img = pg.transform.scale(self.ball_img, (60, 60))
        self.ball_pos = pg.Vector2(400, 500)  
        self.original_ball_pos = (700,400)
        self.ball_target = pg.Vector2(700, 300) 
        self.ball_speed = 600

        self.ball_visible = False
        self.shake_count = 0
        self.shake_timer = 0
        self.ring_radius = 10
        self.ring_alpha = 180
        self.sparkles = []
        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 142 Game Corner.ogg")
        pass
        
    def update(self, dt):
        
        keys = pg.key.get_pressed()
        if keys[pg.K_e] and self.state == "idle":
            self.start_throw()
            
        if self.finished:
            #結束按空白鍵退出
            if pg.key.get_pressed()[pg.K_SPACE] :
                scene_manager.change_scene("game")
            return
        
        if self.state == "throw":
            direction = self.ball_target - self.ball_pos
            
            if direction.length() < 10:
                self.state = "hit"
                self.ball_pos = self.ball_target
                self.animation = None  # 怪獸消失
                
            else:
                self.ball_pos += direction.normalize() * self.ball_speed * dt
                
        elif self.state == "hit":
            self.state = "fall"
            
        elif self.state == "fall":
            self.ball_pos.y += 300 * dt
            if self.ball_pos.y >= 400:
                self.ball_pos.y = 400
                self.state = "shake"
                self.shake_timer = 1.0
                
        elif self.state == "shake":
            self.turn=True
            self.shake_timer -= dt
            self.shake()

            if self.shake_timer <= 0:
                self.reset_pos()
                self.spawn_sparkles()
                #去緩衝狀態
                self.glow_timer = 0
                self.state = "glow"
        
        elif self.state == "glow":
            self.ring_radius += 200 * dt
            self.ring_alpha -= 300 * dt
            if self.ring_alpha <= 0:
                self.finish_catch()
        
        for s in self.sparkles[:]:
            s["pos"] += s["vel"] * dt
            s["life"] -= dt
            if s["life"] <= 0:
                self.sparkles.remove(s)
                
    def start_throw(self):
        self.state = "throw"
        self.ball_visible = True
        
        
    def spawn_sparkles(self):
        for _ in range(12):
            self.sparkles.append({
                "pos": self.ball_pos.copy(),
                "vel": pg.Vector2(random.uniform(-150,150), random.uniform(-200,-50)),
                "life": 0.5
            })
    
    '''震動'''
    def shake(self):
        offset = random.randint(-5, 5)
        self.ball_pos.x = self.original_ball_pos[0] + offset
        self.ball_pos.y = self.original_ball_pos[1]
            
    '''停止震動'''
    def reset_pos(self):
        self.ball_pos = pg.Vector2(self.original_ball_pos)
            
    def finish_catch(self):
        self.state = "finished"
        self.finished = True
        self.game_manager.bag._monsters_data.append(self.monster)
        sound_manager.pause_all()
        sound_manager.play_sound("RBY 119 Captured a Pokemon!.ogg")
        for item in self.game_manager.bag._items_data:
            if item["name"]=="Pokeball":
                item["count"]-=1
        

    def draw_button_area(self, screen: pg.Surface):
        button_area_w = GameSettings.SCREEN_WIDTH
        button_area_h = 200
        button_area_x = 0
        button_area_y = GameSettings.SCREEN_HEIGHT - 200
        
        overlay = pg.Surface((button_area_w, button_area_h), pg.SRCALPHA)

        #填好半透明白色
        overlay.fill((255, 255, 255, 150))

        #貼到螢幕上
        screen.blit(overlay, (button_area_x, button_area_y))
        border_color = (120, 120, 120)      
        border_rect = pg.Rect(button_area_x, button_area_y, button_area_w, button_area_h)
        pg.draw.rect(screen, border_color, border_rect, width=4) 
    
    

    def draw(self, screen):
        self.background.draw(screen)
        self.draw_button_area(screen)
        text1 = self.font.render(f"Wild {self.monster["name"]} appeared!", True, (0, 0, 0))
        text2 = self.font.render("Press E to catch", True, (0, 0, 0))
        
        
        if not self.finished:
            screen.blit(text1, (20, 580))
            screen.blit(text2, (20, 620))
            
        if self.finished:
            screen.blit(self.font.render("You caught it!", True, (0,0,0)), (900, 600))
            screen.blit(self.font.render("Press SPACE to exit", True, (0,0,0)), (900, 650))
            
        if self.animation:
            self.animation.draw(screen, None)
        
        if self.ball_visible:
            screen.blit(self.ball_img, self.ball_pos)
            
        if self.state == "glow":
            ring = pg.Surface((200, 200), pg.SRCALPHA)
            pg.draw.circle(
                ring,
                (255, 255, 255, int(self.ring_alpha)),
                (100, 100),
                int(self.ring_radius),
                3
            )
            screen.blit(ring, self.ball_pos - pg.Vector2(100, 100))
            for s in self.sparkles:
                pg.draw.circle(screen, (250,250,200), s["pos"], 3)
            
        

