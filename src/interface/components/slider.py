import pygame as pg
from typing import Callable
from src.core.services import input_manager

class Slider:
    def __init__(self, x: int, y: int, width: int, height: int,
        value: float, on_change: Callable[[float], None] = None):
        self.rect = pg.Rect(x, y, width, height)         
        self.handle_width = 15                          
        self.value = max(0.0, min(1.0, value))          
        self.handle_rect = pg.Rect(
            x + int(self.value * (width - self.handle_width)),
            y-height*0.1,
            self.handle_width,
            height*1.2
        )
        self.dragging = False
        self.on_change = on_change
        self.offset_x = 0  
        self.font = pg.font.Font(None, self.handle_width+10)
        self.handle_image = pg.image.load("assets/images/UI/raw/UI_Flat_Handle03a.png").convert_alpha()
        self.handle_image = pg.transform.scale(self.handle_image, (self.handle_width,height*1.2))
        self.bar_image = pg.image.load("assets/images/UI/raw/UI_Flat_Bar12a.png").convert_alpha()
        self.bar_image = pg.transform.scale(self.bar_image, (width,height))
        
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
        screen.blit(self.bar_image, self.rect)
        #畫handle
        screen.blit(self.handle_image, self.handle_rect)
        percent = int(self.value * 100)
        text = self.font.render(str(percent)+"%", True, (30, 30, 30))
        screen.blit(text, (self.rect.right + 10, self.rect.y))
