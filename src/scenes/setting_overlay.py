# src/scenes/setting_overlay.py
import os
import json
import pygame as pg
from src.utils import GameSettings
from src.interface.components import Button
from src.interface.components.slider import Slider
from src.interface.components.checkbox import Checkbox
from src.sprites import BackgroundSprite
from src.core.services import sound_manager
from src.core.services import scene_manager, sound_manager, input_manager
from src.core.services import input_manager
from src.core.managers.game_manager import GameManager
from src.utils import Logger
from src.scenes.scene import Scene    

class SettingOverlay(Scene):
    back_button=Button
    save_button=Button
    load_button=Button
    bgm_checkbox: Checkbox
    volume_slider: Slider
    
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        self.visible = False   #Overlay預設不顯示
        self.font = pg.font.Font(None, 25)
        #位置
        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2

        #返回按鈕
        self.back_button = Button(
            "UI/button_x.png", 
            "UI/button_x_hover.png",
            px+195, py-215, 
            60, 60,
            lambda: self.hide()  #點擊後關閉overlay
        )
        
        self.save_button = Button(
            "UI/button_save.png", 
            "UI/button_save_hover.png",
            px-100, py +20,    
            70, 70,
            self.save_game  
        )
        
        self.load_button = Button(
            "UI/button_load.png", 
            "UI/button_load_hover.png",
            px+100, py +20,     
            70, 70,
            self.load_game  
        )
        self.menu_button = Button(
            "UI/button_back.png", 
            "UI/button_back_hover.png",
            px-200, py +20,    
            70, 70,
            lambda: scene_manager.change_scene("menu")
        )
        self.bgm_checkbox = Checkbox(
            px-80, py-100, size=30,  checked=sound_manager.bgm_enabled,
            on_toggle=self.toggle_bgm
        )
        
        self.volume_slider = Slider(
            px-200, py-50, width=300, height=20, value=sound_manager.bgm_volume,
            on_change=lambda val: sound_manager.set_bgm_volume(val)
        )
        
    def toggle_bgm(self,state: bool):
        sound_manager.bgm_enabled = state
        sound_manager.play_bgm("RBY 102 Opening (Part 2).ogg")
        """if state:
            if sound_manager.current_bgm is None:
                sound_manager.play_bgm("RBY 102 Opening (Part 2).ogg")
            else:
                sound_manager.resume_all()
        else:
            sound_manager.pause_all()"""
        
            
    
            
    def save_game(self):
        save_path = "saves/game0.json"
        self.game_manager.save(save_path)
        
    def load_game(self):
        save_path = "saves/game0.json"
        if not os.path.exists(save_path) or os.path.getsize(save_path) == 0:
            Logger.warning(f"No valid save file found at {save_path}")
            return
        loaded_game = GameManager.load(save_path)
        if loaded_game:
            #將當前game instance更新成讀檔的內容
            self.game_manager.player = loaded_game.player
            self.game_manager.enemy_trainers = loaded_game.enemy_trainers
            self.game_manager.maps = loaded_game.maps
            self.game_manager.bag = loaded_game.bag
            self.game_manager.current_map_key = loaded_game.current_map_key
            Logger.info(f"Game loaded from {save_path}")
        
    
    def show(self):
        self.visible = True
        self.bgm_checkbox.checked = sound_manager.bgm_enabled
        self.volume_slider.value = sound_manager.get_bgm_volume()
        self.bgm_checkbox.last_mouse_down = False

    def hide(self):
        self.visible = False

    
    def update(self, dt: float):
        if not self.visible:
            return
        self.bgm_checkbox.update()
        self.volume_slider.update()
        
        #更新按鈕
        self.back_button.update(dt)
        self.save_button.update(dt)
        self.load_button.update(dt)
        self.menu_button.update(dt)

    
    def draw(self, screen: pg.Surface):
        if not self.visible:
            return

        #半透明黑幕
        overlay = pg.Surface(screen.get_size(), pg.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        screen.blit(overlay, (0, 0))

        #中間小視窗
        window_w, window_h = 550, 460
        window_x = (GameSettings.SCREEN_WIDTH - window_w) // 2
        window_y = (GameSettings.SCREEN_HEIGHT - window_h) // 2

        pg.draw.rect(screen, (240, 240, 240), (window_x, window_y, window_w, window_h), border_radius=15)
        pg.draw.rect(screen, (120, 120, 120), (window_x, window_y, window_w, window_h), 5, border_radius=15)

        #字
        font=pg.font.Font(None, 52)
        text=font.render("SETTINGS",True, (30, 30, 30))
        screen.blit(text, (
            window_x + (window_w-text.get_width()) // 2,
            window_y+ 20
        ))
        font_small=pg.font.Font(None, 35)
        text1=font_small.render("Volume:",True, (30, 30, 30))
        screen.blit(text1,(window_x + 80,window_y+130))
        
        # 畫返回按鈕
        self.back_button.draw(screen)
        self.save_button.draw(screen)
        self.load_button.draw(screen)
        self.menu_button.draw(screen)
        self.bgm_checkbox.draw(screen)
        self.volume_slider.draw(screen)
