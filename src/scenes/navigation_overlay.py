# src/scenes/navigation_overlay.py

import pygame as pg
from src.utils import GameSettings
from src.interface.components import Button
from src.sprites import BackgroundSprite
from src.core.services import input_manager
from src.core import GameManager, OnlineManager
from src.utils import Logger
from src.scenes.scene import Scene  
from src.utils import Position, GameSettings

class NavigationOverlay(Scene):

    def __init__(self, game_scene, places: dict[str, Position],game_manager):
        self.game_scene = game_scene
        self.game_manager = game_manager
        self.places = places 
        self.buttons = []
        self.selected_place = None
        self.visible = False
        window_w, window_h = 550, 460
        window_x = (GameSettings.SCREEN_WIDTH - window_w) // 2
        window_y = (GameSettings.SCREEN_HEIGHT - window_h) // 2
        start_x, start_y = window_x + 50, window_y + 120
        for i, (name, pos) in enumerate(places.items()):
            btn = Button(
                "UI/button_play.png", "UI/button_play_hover.png",
                start_x+i*100, start_y , 70, 70,
                lambda n=pos: self.select_place(n)
            )
            btn.text = name
            self.buttons.append(btn)
            
        #返回按鈕
        self.back_button = Button(
            "UI/button_x.png", 
            "UI/button_x_hover.png",
            window_x+470, window_y+20,    
            60, 60,
            lambda: self.hide()  
        )
    
    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
        
    def select_place(self,pos: Position):
        self.hide()
        self.selected_place = pos
        if self.game_manager.current_map_key == "map.tmx":
            self.game_scene.start_navigation(pos)
        
        '''if self.game_manager.current_map_key == "home.tmx":
            if pos.x == 16 and pos.y == 30:
                pass
            else:
                self.game_scene.start_navigation(Position(12,12))
                self.game_scene.pending_navigation_target = pos'''
            
    
    #覆蓋update
    def update(self, dt):
        if not self.visible:
            return
        self.back_button.update(dt)
        for btn in self.buttons:
            btn.update(dt)

    #畫overlay
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
        font = pg.font.Font(None, 52)
        text = font.render("Navigation", True, (30, 30, 30))
        screen.blit(text, (
            window_x + (window_w - text.get_width()) // 2,
            window_y + 20
        ))
        self.back_button.draw(screen)
        start_x, start_y = window_x + 50, window_y + 120
        i=0
        for btn in self.buttons:
            btn.draw(screen)
            # draw the place name
            font = pg.font.Font(None, 24)
            screen.blit(font.render(btn.text, True, (0,0,0)), (start_x + i*100+15, start_y+80))
            i+=1
