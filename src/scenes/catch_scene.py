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
        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 142 Game Corner.ogg")
        pass
        
    def update(self, dt):
        
        keys = pg.key.get_pressed()
        if keys[pg.K_e]:
            self.catch_pokemon()
            
        if self.finished:
            self.animation.update(dt)
            #結束按空白鍵退出
            if pg.key.get_pressed()[pg.K_SPACE] :
                scene_manager.change_scene("game")
            return
        self.animation.update(dt)
        
    def catch_pokemon(self):
        if self.finished:
            return
        self.game_manager.bag._monsters_data.append(self.monster)
        sound_manager.play_sound("RBY 119 Captured a Pokemon!.ogg")
        for item in self.game_manager.bag._items_data:
            if item["name"]=="Pokeball":
                item["count"]-=1

        # 回主場景
        self.finished=True

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
        
        self.animation.draw(screen,None)
        if self.finished:
            screen.blit(self.font.render("You caught it!", True, (0,0,0)), (900, 600))
            screen.blit(self.font.render("Press SPACE to exit", True, (0,0,0)), (900, 650))
            self.animation.draw(screen,None)
            return
