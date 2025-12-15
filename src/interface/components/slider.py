import pygame as pg
from typing import Callable
from src.core.services import input_manager

class Slider:
    def __init__(self, x: int, y: int, width: int, height: int,
        value: float, on_change: Callable[[float], None] = None):
        self.rect = pg.Rect(x, y, width, height)         
        self.handle_width = 20                           
        self.value = max(0.0, min(1.0, value))          
        self.handle_rect = pg.Rect(
            x + int(self.value * (width - self.handle_width)),
            y,
            self.handle_width,
            height
        )
        self.dragging = False
        self.on_change = on_change
        self.offset_x = 0  
        self.font = pg.font.Font(None, self.handle_width+10)
        
    def update(self):
        mouse_x, mouse_y = input_manager.mouse_pos

        #開始拖曳
        if input_manager.mouse_pressed(1) and not self.dragging:
            if self.handle_rect.collidepoint((mouse_x, mouse_y)):
                self.dragging = True
                self.offset_x = mouse_x- self.handle_rect.x
            elif self.rect.collidepoint((mouse_x, mouse_y)):
                #點擊滑軌直接跳到該位置
                new_x = max(self.rect.x, min(mouse_x -self.handle_width//2, self.rect.right - self.handle_width))
                self.handle_rect.x = new_x
                self.value= (self.handle_rect.x -self.rect.x)/(self.rect.width - self.handle_width)
                if self.on_change:
                    self.on_change(self.value)
        else:
            self.handle_rect.x = self.rect.x + int(self.value * (self.rect.width - self.handle_width))
            
        

        #停止拖曳
        if not input_manager.mouse_down(1):
            self.dragging = False

        #拖曳過程中更新handle
        if self.dragging:
            new_x = mouse_x - self.offset_x
            new_x = max(self.rect.x, min(new_x, self.rect.right - self.handle_width))
            self.handle_rect.x = new_x
            self.value = (self.handle_rect.x - self.rect.x) / (self.rect.width - self.handle_width)
            if self.on_change:
                self.on_change(self.value)

    def draw(self, screen: pg.Surface):
        #畫滑軌
        pg.draw.rect(screen, (180, 180, 180), self.rect)
        #畫handle
        pg.draw.rect(screen, (100, 100, 255), self.handle_rect)
        percent = int(self.value * 100)
        text = self.font.render(str(percent)+"%", True, (30, 30, 30))
        screen.blit(text, (self.rect.right + 10, self.rect.y))
