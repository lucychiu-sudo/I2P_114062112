# src/scenes/update_scene.py
import pygame as pg
from src.utils import GameSettings
import os
import random
from src.sprites import Animation
from src.scenes.scene import Scene
from src.sprites import BackgroundSprite
from typing import override

from src.interface.components import Button
from src.interface.components.slider import Slider
from src.interface.components.checkbox import Checkbox
from src.core.services import sound_manager
from src.core.services import scene_manager, sound_manager, input_manager
from src.utils import Logger
from src.core.managers.game_manager import GameManager
ASSET = "assets/images/"

def crop_image(image, x, y, w, h):
        rect = pg.Rect(x, y, w, h)
        return image.subsurface(rect).copy()
    
class UpdateScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    back_button: Button
    _checkbox: Checkbox
    volume_slider: Slider
    
    def __init__(self, monsters_data, items_data):
        super().__init__()
        self.monsters = monsters_data
        self.items = items_data
        self.background = BackgroundSprite("backgrounds/Update_background.png")
        
        self.items_buttons =[]
        self.monsters_buttons =[]
        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2
        start = -115
        
        #怪獸資料
        for i in range(0,len(self.monsters)):
            self.monsters_buttons.append(Button(
                    "UI/raw/UI_Flat_FrameSlot01a.png",
                    "UI/raw/UI_Flat_FrameSlot01a.png",
                    px -600, py+start+80*i,
                    370, 70,
                    lambda i=i : self.switch_midle(i)
                ))
            
        
    
        self.usable_items = []
        
        
        #物品資料
        for item in self.items:
            if item["name"]=="Attack Potion":
                self.attack_potion = item
                self.usable_items.append(item)
                self.items_buttons.append(Button(
                    "UI/raw/UI_Flat_Banner03a.png",
                    "UI/raw/UI_Flat_FrameSlot01c.png",
                    px + 250, py  + start,
                    300, 70,
                    lambda: self.select_item("attack")
                ))
            elif  item["name"]=="Defense Potion":
                self.defense_potion = item
                self.usable_items.append(item)
                self.items_buttons.append(Button(
                    "UI/raw/UI_Flat_Banner03a.png",
                    "UI/raw/UI_Flat_FrameSlot01c.png",
                    px + 250, py  + start+80,
                    300, 70,
                    lambda: self.select_item("defense")
                ))
            elif  item["name"]=="Heal Potion":
                self.heal_potion = item
                self.usable_items.append(item)
                self.items_buttons.append(Button(
                    "UI/raw/UI_Flat_Banner03a.png",
                    "UI/raw/UI_Flat_FrameSlot01c.png",
                    px + 250, py  + start+80*2,
                    300, 70,
                    lambda: self.select_item("heal")
                ))
        self.use_button = Button(
            "UI/raw/UI_Flat_Button01a_3.png",
            "UI/raw/UI_Flat_Button01a_1.png",
            px-50, py+120, 70, 50,
            lambda: self.use_item()    
        )
        self.back_button = Button(
            "UI/button_x.png", 
            "UI/button_x_hover.png",
            px+600, py+400,    
            60, 60,
            lambda: scene_manager.change_scene("game")  
        )
        #選物
        self.selected_item = None
        
        #選怪
        self.midle_monster_index = 0
        monster = self.monsters[self.midle_monster_index]
        image_path = monster["sprite_path"]
        big_img_path=image_path.replace("menu","")
        big_img_path=big_img_path.replace("_","")
        big_img_path=big_img_path.replace(".png","_idle.png")
        self.big_anim=Animation(big_img_path,["idle"],4,(400,400))
        
        #字體和偵測
        
        self.font = pg.font.Font(None, 36)
        
        #提示字
        self.msg = ""
        self.msg_timer = 0
        
        
        #進化
        self.evolution_map={
            "Pikachu":  { "name": "Charizard", "hp": 200, "max_hp": 200, "level": 12,"attack":23,"defense":8,"element":"grass", "sprite_path": "menu_sprites/menusprite2.png" },
            "Charizard":{ "name": "Blastoise", "hp": 180, "max_hp": 180, "level": 33,"attack":25,"defense":9,"element":"grass", "sprite_path": "menu_sprites/menusprite3.png" },
            "Mouse":    { "name": "FireMouse", "hp": 280, "max_hp": 280, "level": 17,"attack":24,"defense":8,"element":"fire", "sprite_path": "menu_sprites/menusprite8.png" },
            "FireMouse":{ "name": "GiantMouse", "hp": 300, "max_hp": 300, "level": 11,"attack":29,"defense":11,"element":"fire", "sprite_path": "menu_sprites/menusprite9.png" },
            "Dophin":   { "name": "BigDophin",   "hp": 230, "max_hp": 230, "level": 19,"attack":26,"defense":9,"element":"water", "sprite_path": "menu_sprites/menusprite13.png" },
            "BigDophin":{ "name": "LargeDophin", "hp": 250, "max_hp": 250, "level": 20,"attack":31,"defense":12,"element":"water", "sprite_path": "menu_sprites/menusprite14.png" },
            "Bug":      { "name": "UglyBug",     "hp": 130, "max_hp": 130, "level": 15,"attack":25,"defense":10,"element":"grass", "sprite_path": "menu_sprites/menusprite16.png" }
        }
        self.evolution=False
        self.evolution_text=""
        
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 5 // 6

        
        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 149 Victory Road.ogg")
        pass
    
    def show_message(self, text, duration=0.8):
        self.msg = text
        self.msg_timer = duration
        
    def select_item(self,item:str):
        if item=="attack":
            if self.selected_item==self.attack_potion:
                self.selected_item = None
            else:
                self.selected_item=self.attack_potion
                
        elif item == "defense":
            if self.selected_item==self.defense_potion:
                self.selected_item = None
            else:
                self.selected_item=self.defense_potion
                
        elif item == "heal":
            if self.selected_item==self.heal_potion:
                self.selected_item = None
            else:
                self.selected_item=self.heal_potion
                
    def switch_midle(self,index):
        self.midle_monster_index = index
        monster = self.monsters[self.midle_monster_index]
        image_path = monster["sprite_path"]
        big_img_path=image_path.replace("menu","")
        big_img_path=big_img_path.replace("_","")
        big_img_path=big_img_path.replace(".png","_idle.png")
        self.big_anim=Animation(big_img_path,["idle"],4,(400,400))
        
        
    def use_item(self):
        if self.selected_item==None:
            return
        elif self.selected_item["name"]=="Attack Potion":
            if self.attack_potion["count"]>0:
                self.monsters[self.midle_monster_index]["attack"] +=10
                self.attack_potion["count"]-=1
            self.selected_item=None
            
        elif self.selected_item["name"]=="Defense Potion":
            if self.defense_potion["count"]>0 :
                self.monsters[self.midle_monster_index]["defense"] +=10
                self.defense_potion["count"]-=1
            self.selected_item=None
            
        elif self.selected_item["name"]=="Heal Potion":
            if self.heal_potion["count"]>0 and self.monsters[self.midle_monster_index]["hp"]<self.monsters[self.midle_monster_index]["max_hp"]:
                self.monsters[self.midle_monster_index]["hp"] =min(self.monsters[self.midle_monster_index]["max_hp"], self.monsters[self.midle_monster_index]["hp"]+30)
                self.heal_potion["count"]-=1
            self.selected_item=None
        
        
        
    '''玩家換怪獸'''
    def player_switch(self):
        #切換到下一隻怪獸，不消耗回合
        self.current_monster_index += 1
        if self.current_monster_index >= len(self.monsters):
            self.current_monster_index = 0  #循環回第一隻
        self.player_monster = self.monsters[self.current_monster_index]
        
    
    
    
    def update(self, dt):
        for button in self.monsters_buttons:
            button.update(dt)
    
        for button in self.items_buttons:
            button.update(dt)
        self.use_button.update(dt)
        self.back_button.update(dt)
        self.big_anim.update(dt)
        
    def draw_monster_area(self, screen: pg.Surface):
        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2
        start = -115
        for i, monster in enumerate(self.monsters):
            #把所有資料叫出來
            name = monster["name"] if isinstance(monster, dict) else monster.name
            hp = monster["hp"] if isinstance(monster, dict) else monster.hp
            max_hp = monster["max_hp"] if isinstance(monster, dict) else monster.max_hp
            level = monster["level"] if isinstance(monster, dict) else monster.level
            image_path = monster["sprite_path"] if isinstance(monster, dict) else monster.sprite_path
            
            # 畫卡片怪獸圖片
            image_path=ASSET+image_path
            i_image =pg.image.load(image_path).convert_alpha()
            i_image = pg.transform.scale(i_image,(60, 60))
            screen.blit(i_image, (px -600+20, py+start+80*i-5))
            
            font_small = pg.font.Font(None, 28)
            name_text = font_small.render(f"{name}   Lv.{level}", True, (0, 0, 0))
            screen.blit(name_text, (px -600 +80, py+start+80*i +10))

            #血條
            bar_x = px -600 + 80
            bar_y = py+start+80*i + 35
            bar_w = 130
            bar_h = 15
            fill_w = int(bar_w * hp / max_hp)
            #背景
            pg.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_w, bar_h))
            #血量
            pg.draw.rect(screen, (150, 0, 0), (bar_x, bar_y, fill_w, bar_h))
            #邊框
            pg.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_w, bar_h), 2)

            #血量數字
            hp_text = font_small.render(f"{hp}/{max_hp}", True, (0, 0, 0))
            screen.blit(hp_text, (bar_x + bar_w + 5, bar_y - 2))
        
    def draw_midle_area(self, screen: pg.Surface):
        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2
        monster = self.monsters[self.midle_monster_index]
        name = monster["name"]
        hp = monster["hp"]
        max_hp = monster["max_hp"]
        level = monster["level"]
        attack = monster["attack"]
        defense = monster["defense"]
        self.big_anim.rect.midbottom=(px-150,py-180)
        self.big_anim.draw(screen,None)
        
        
        button_area_w = GameSettings.SCREEN_WIDTH//2
        button_area_h = 200
        button_area_x = GameSettings.SCREEN_WIDTH//4
        button_area_y = GameSettings.SCREEN_HEIGHT - 200
        
        overlay = pg.Surface((button_area_w, button_area_h), pg.SRCALPHA)
        #填好半透明白色
        overlay.fill((255, 255, 255, 150))
        # 貼到螢幕上
        screen.blit(overlay, (button_area_x, button_area_y))
        border_color = (120, 120, 120)      
        border_rect = pg.Rect(button_area_x, button_area_y, button_area_w, button_area_h)
        pg.draw.rect(screen, border_color, border_rect, width=4) 
        
        #名字與等級
        font = pg.font.Font(None, 28)
        
        name_surf = font.render(f"{name}  Lv.{level}  attack:{attack}  defense:{defense}", True, (0, 0, 0))
        screen.blit(name_surf, (button_area_x + 85,button_area_y+ 10))

        #HP條
        
        hp_bar_width = 140
        hp_bar_height = 15
        hp_x =button_area_x+ 85
        hp_y =button_area_y+ 32
        # 底色
        pg.draw.rect(screen, (150, 150, 150), (hp_x, hp_y, hp_bar_width, hp_bar_height))
        # 實際 HP
        hp_ratio = max(hp / max_hp, 0)
        if hp/max_hp>=0.7:
            pg.draw.rect(screen, (100, 255, 100), (hp_x, hp_y, int(hp_bar_width * hp_ratio), hp_bar_height))
        elif hp/max_hp>=0.3:
            pg.draw.rect(screen, (255, 165, 0), (hp_x, hp_y, int(hp_bar_width * hp_ratio), hp_bar_height))
        else:
            pg.draw.rect(screen, (255, 50, 50), (hp_x, hp_y, int(hp_bar_width * hp_ratio), hp_bar_height))
        pg.draw.rect(screen, (0, 0, 0), (hp_x, hp_y,hp_bar_width, hp_bar_height), 2)
        # 數字顯示
        hp_text = font.render(f"{hp}/{max_hp}", True, (0, 0, 0))
        screen.blit(hp_text, (hp_x + hp_bar_width + 5, hp_y))
        
    def draw_items_area(self,screen: pg.Surface):
        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2
        start = -115
        font_small = pg.font.Font(None, 28)
        
        for item in self.usable_items:
            name = item["name"]
            count = item["count"]
            image_path = item["sprite_path"] 
            
            if name == "Attack Potion":
                i=0
            elif name == "Defense Potion":
                i=1
            else:
                i=2
            image_path=ASSET+image_path
            i_image = pg.image.load(image_path).convert_alpha()
            i_image = pg.transform.scale(i_image, (40, 40))
            screen.blit(i_image, (px + 250+20, py  + start+10+ i*80))
                
            i_text = font_small.render(f"{i+1}. {name} x{count}", True, (0, 0, 0))
            screen.blit(i_text, (px + 250+70, py  + start+20+ i*80))
                
        
    def draw(self, screen):
        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2
        self.background.draw(screen)
        
        
        
        
        
        
        for button in self.monsters_buttons:
            button.draw(screen)
        for button in self.items_buttons:
            button.draw(screen)
        self.use_button.draw(screen)
        self.back_button.draw(screen)
        
        
        self.draw_midle_area(screen)
        self.draw_monster_area(screen)
        self.draw_items_area(screen)
            
        #use文字
        use_text = self.font.render(f"use", True, (0, 0, 0))
        screen.blit(use_text, (px-50+5, py+120+5))
            
        #提示字
        if self.msg:
            font_msg = pg.font.Font(None, 80)
            msg_surf = font_msg.render(self.msg, True, (250, 0, 0))
            screen.blit(
                msg_surf,
                (GameSettings.SCREEN_WIDTH//4,
                GameSettings.SCREEN_HEIGHT//3)
            )
        