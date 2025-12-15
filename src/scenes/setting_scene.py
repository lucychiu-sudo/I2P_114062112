# src/scenes/settings_scene.py
import pygame as pg
from src.utils import GameSettings

from src.scenes.scene import Scene
from src.sprites import BackgroundSprite
from src.interface.components import Button
from src.interface.components.slider import Slider
from src.interface.components.checkbox import Checkbox
from src.core.services import sound_manager
from src.core.services import scene_manager, sound_manager, input_manager
from src.utils import Logger


class SettingsScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    back_button: Button
    _checkbox: Checkbox
    volume_slider: Slider
    
    def __init__(self):
        super().__init__()
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 3 // 4
        self.background = BackgroundSprite("backgrounds/background1.png")
        
        self.back_button = Button(
            "UI/button_back.png", "UI/button_back_hover.png",
            px-350, py-80, 100, 100,
            lambda: scene_manager.change_scene("menu")
        )
        
        self.bgm_checkbox = Checkbox(
            px-200, py-300, size=30, checked=sound_manager.bgm_enabled,
            on_toggle=self.toggle_bgm
        )

        
        self.volume_slider = Slider(
            px-300, py-250, width=500, height=20, value=sound_manager.bgm_volume,
            on_change=lambda val: sound_manager.set_bgm_volume(val)
        )
    
    def toggle_bgm(self, state: bool):
        sound_manager.bgm_enabled = state
        sound_manager.play_bgm("RBY 102 Opening (Part 2).ogg")
        """if state:
            if sound_manager.current_bgm is None:
                sound_manager.play_bgm("RBY 102 Opening (Part 2).ogg")
            else:
                sound_manager.resume_all()
        else:
            sound_manager.pause_all()"""
    
    def enter(self) -> None:
        Logger.info("backgrounds/background3.png")
        sound_manager.play_bgm("RBY 102 Opening (Part 2).ogg") 
        self.bgm_checkbox.checked = sound_manager.bgm_enabled
        self.volume_slider.value=sound_manager.get_bgm_volume()
        
    def exit(self) -> None:
        Logger.info("backgrounds/background2.png")
    
    def update(self, dt: float) -> None:
        if input_manager.key_pressed(pg.K_SPACE):
            scene_manager.change_scene("menu")
            return
        self.back_button.update(dt)
        self.bgm_checkbox.update()
        self.volume_slider.update()
    
    def draw(self, screen: pg.Surface) -> None:
        self.background.draw(screen)
        # 中間小視窗
        window_w, window_h = 750, 460
        window_x = (GameSettings.SCREEN_WIDTH - window_w) // 2
        window_y = (GameSettings.SCREEN_HEIGHT - window_h) // 2
        pg.draw.rect(screen, (240, 240, 240), (window_x, window_y, window_w, window_h), border_radius=15)
        pg.draw.rect(screen, (120, 120, 120), (window_x, window_y, window_w, window_h), 5, border_radius=15)

        #字
        font = pg.font.Font(None, 52)
        font_small = pg.font.Font(None, 35)
        text = font.render("SETTINGS", True, (30, 30, 30))
        screen.blit(text, (
            window_x + (window_w - text.get_width()) // 2,
            window_y + 20
        ))
        screen.blit(font_small.render("Volume:", True, (30, 30, 30)),(window_x+70,window_y+115))
        

        self.back_button.draw(screen)
        self.bgm_checkbox.draw(screen)
        self.volume_slider.draw(screen)
