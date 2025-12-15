# src/scenes/backpack_overlay.py
import os
import pygame as pg
from src.utils import GameSettings
from src.interface.components import Button
from src.sprites import BackgroundSprite
from src.core.services import input_manager
from src.utils import Logger
from src.scenes.scene import Scene   
from typing import TYPE_CHECKING
ASSET = "assets/images/"
if TYPE_CHECKING:
    from src.core.managers.game_manager import GameManager
    

class BackpackOverlay(Scene):
    game_manager: "GameManager"
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        #Overlay預設不顯示
        self.visible = False   
        
        #視窗位置
        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2

        #返回按鈕
        self.back_button = Button(
            "UI/button_x.png", 
            "UI/button_x_hover.png",
            px+300, py -210,    
            60, 60,
            lambda: self.hide()  
        )

    #讓GameScene呼叫的API
    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    
    def update(self, dt: float):
        if not self.visible:
            return
        
        #按鈕
        self.back_button.update(dt)
        
        
    
    def draw(self, screen: pg.Surface):
        if not self.visible:
            return

        #半透明黑幕
        overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        #中間小視窗
        window_w, window_h = 750, 460
        window_x = (GameSettings.SCREEN_WIDTH - window_w) // 2
        window_y = (GameSettings.SCREEN_HEIGHT - window_h) // 2

        pg.draw.rect(screen, (240, 240, 240), (window_x, window_y, window_w, window_h), border_radius=15)
        pg.draw.rect(screen, (120, 120, 120), (window_x, window_y, window_w, window_h), 5, border_radius=15)

        
        #字
        font = pg.font.Font(None, 52)
        text = font.render("backpack", True, (30, 30, 30))
        screen.blit(text, (
            window_x + (window_w - text.get_width()) // 2,
            window_y + 20
        ))
        font_small = pg.font.Font(None, 36)
        y_offset = 80
        
        #卡片連結
        card_bg_path = ASSET+"UI/raw/UI_Flat_Banner03a.png"
        card_bg_image = pg.image.load(card_bg_path).convert_alpha()
        card_bg_image = pg.transform.scale(card_bg_image, (370, 70))
        
        #畫怪物
        for i, monster in enumerate(self.game_manager.bag._monsters_data):
            #把所有資料叫出來
            name = monster["name"] if isinstance(monster, dict) else monster.name
            hp = monster["hp"] if isinstance(monster, dict) else monster.hp
            max_hp = monster["max_hp"] if isinstance(monster, dict) else monster.max_hp
            level = monster["level"] if isinstance(monster, dict) else monster.level
            image_path = monster["sprite_path"] if isinstance(monster, dict) else monster.sprite_path
            
            #卡片位置
            card_x = window_x + 20
            card_y = window_y + y_offset + i * 80
            

            # 畫卡片背景圖片
            screen.blit(card_bg_image, (card_x, card_y))
            
            
            image_path=ASSET+image_path
            i_image =pg.image.load(image_path).convert_alpha()
            i_image = pg.transform.scale(i_image,(60, 60))
            screen.blit(i_image, (card_x +20, card_y-5))
            
            
            
            font_small = pg.font.Font(None, 28)
            name_text = font_small.render(f"{name}   Lv.{level}", True, (0, 0, 0))
            screen.blit(name_text, (card_x +80, card_y +10))

            #血條
            bar_x = card_x + 80
            bar_y = card_y + 35
            bar_w = 200
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
            
        #畫道具
        i=0
        for item in self.game_manager.bag._items_data:
            
            name = item["name"] if isinstance(item, dict) else item.name
            count = item["count"] if isinstance(item, dict) else item.count
            image_path = item["sprite_path"] if isinstance(item, dict) else item.sprite_path
            
            if count>0:
                image_path=ASSET+image_path
                i_image = pg.image.load(image_path).convert_alpha()
                i_image = pg.transform.scale(i_image, (40, 40))
                screen.blit(i_image, (window_x + 450, window_y + y_offset + i*80))
                
                i_text = font_small.render(f"{i+1}. {name} x{count}", True, (0, 0, 0))
                screen.blit(i_text, (window_x + 500, window_y + y_offset + i*80))
                i+=1
        
        screen.set_clip(None)
        #畫按鈕
        self.back_button.draw(screen)
        
