import pygame as pg
from typing import Callable
from src.core.services import input_manager

class Checkbox:
    def __init__(self, x: int, y: int, size: int, checked: bool = False, on_toggle: Callable[[bool], None] = None):
        self.rect = pg.Rect(x, y, size, size)
        self.checked = checked
        self.on_toggle = on_toggle
        self.last_mouse_down = False 

    def update(self):
        mouse_down = input_manager.mouse_pressed(1)
        if self.rect.collidepoint(input_manager.mouse_pos):
            if mouse_down and not self.last_mouse_down:  # 只在按下的瞬間切換
                self.checked = not self.checked
                if self.on_toggle:
                    self.on_toggle(self.checked)
        self.last_mouse_down = mouse_down
        
        
    def draw(self, screen: pg.Surface):
        color = (50, 200, 50) if self.checked else (200, 50, 50)
        pg.draw.rect(screen, color, self.rect)
        pg.draw.rect(screen, (0, 0, 0), self.rect, 2)