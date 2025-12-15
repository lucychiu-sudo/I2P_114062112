# src/scenes/shop_overlay.py
import os
import pygame as pg
from src.utils import GameSettings
from src.interface.components import Button
from src.sprites import BackgroundSprite
from src.core.services import input_manager
from src.utils import Logger
from src.utils.definition import Monster, Item
from src.scenes.scene import Scene   
from typing import TYPE_CHECKING
ASSET = "assets/images/"
if TYPE_CHECKING:
    from src.core.managers.game_manager import GameManager
    

class ShopOverlay(Scene):
    game_manager: "GameManager"
    def __init__(self, game_manager):
        super().__init__()
        self.game_manager = game_manager
        #Overlay預設不顯示
        self.mode = "buy"
        self.visible = False   
        self.buy_items= [
        { "name": "Heal Potion",   "count":1,"price": 50,  "sprite_path": "ingame_ui/potion.png" },
        { "name": "Attack Potion", "count":1,"price": 70,  "sprite_path": "ingame_ui/potion.png" },
        { "name": "Defense Potion","count":1,"price": 80,  "sprite_path": "ingame_ui/potion.png" },
        { "name": "Pokeball",      "count":1,"price": 60,  "sprite_path": "ingame_ui/ball.png" }
        ]
        
        self.items_buttons = []
        self.items = self.buy_items
        
        
        #提示字
        self.msg = ""
        self.msg_timer = 0
        
        #視窗位置
        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2
        
        self.refresh_items()
            
        #buy按鈕
        self.buy_button = Button(
            "UI/raw/UI_Flat_Button01a_3.png", 
            "UI/raw/UI_Flat_Button01a_1.png",
            px-340, py -200,    
            80, 50,
            lambda: self.switch_to_buy()  
        )
            
        #sell按鈕
        self.sell_button = Button(
            "UI/raw/UI_Flat_Button01a_3.png", 
            "UI/raw/UI_Flat_Button01a_1.png",
            px-240, py -200,    
            80, 50,
            lambda: self.switch_to_sell()  
        )

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
        
    def switch_to_buy(self):
        self.mode = "buy"
        self.refresh_items()

    def switch_to_sell(self):
        self.mode = "sell"
        self.refresh_items()
        
    def refresh_items(self):
        # 切換模式後重新設定 items 與按鈕
        if self.mode == "buy":
            self.items = self.buy_items
        else:
            self.items = [i for i in self.game_manager.bag._items_data if i["name"] != "Coins"]

        
        self.items_buttons.clear()
        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2
        start = -115

        for item in self.items:
            if self.mode == "buy":
                self.items_buttons.append(Button(
                    "UI/button_shop.png",
                    "UI/button_shop_hover.png",
                    px + 50, py + start,
                    50, 50,
                    lambda i=item: self.buy_item(i)
                ))
            else:
                self.items_buttons.append(Button(
                    "UI/button_shop.png",
                    "UI/button_shop_hover.png",
                    px + 50, py + start,
                    50, 50,
                    lambda i=item: self.sell_item(i)
                ))
            start += 80
    
    
    def show_message(self, text, duration=0.8):
        self.msg = text
        self.msg_timer = duration

    def sell_item(self, item):
        
        # 找 Coins
        coins = None
        for own in self.game_manager.bag._items_data:
            if own["name"] == "Coins":
                coins = own
            
        if item["count"]>0:
            # 給錢
            coins["count"] += item["price"]
            # 扣物品
            item["count"] -= 1
            
            # 顯示訊息
            self.show_message(f"Sold {item['name']} +{item["price"]}$")
        else:
            self.show_message(f"Do not have {item['name']}")
    
    
    def buy_item(self, item):
        for own in self.game_manager.bag._items_data:
            if own["name"]=="Coins":
                coins = own
        if coins["count"]<item["price"]:
            self.show_message(f"Too poor to buy {item['name']}")
            return
        else:
            data = {
                "name": item["name"],
                "count": item["count"],
                "sprite_path": item["sprite_path"]
            }
            coins["count"]-=item["price"]
            self.game_manager.bag.add_item(Item(data))
            self.show_message(f"{item['name']} +1")
        
    def update(self, dt: float):
        if not self.visible:
            return
        
        if self.msg_timer > 0:
            self.msg_timer -= dt
            if self.msg_timer <= 0:
                self.msg = ""
        
        
        
        #按鈕
        self.back_button.update(dt)
        self.buy_button.update(dt)
        self.sell_button.update(dt)
        for button in self.items_buttons:
            button.update(dt)
        
        
    
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

        px = GameSettings.SCREEN_WIDTH // 2
        py = GameSettings.SCREEN_HEIGHT // 2
        #字
        font = pg.font.Font(None, 52)
        text = font.render("shop", True, (30, 30, 30))
        screen.blit(text, (
            window_x + (window_w - text.get_width()) // 2,
            window_y + 20
        ))
        font_small = pg.font.Font(None, 36)
        y_offset = 110
        
        #卡片連結
        card_bg_path = ASSET+"UI/raw/UI_Flat_Banner03a.png"
        card_bg_image = pg.image.load(card_bg_path).convert_alpha()
        card_bg_image = pg.transform.scale(card_bg_image, (370, 70))
        
        #畫商品
        for i, item in enumerate(self.items):
            #把所有資料叫出來
            name = item["name"] if isinstance(item, dict) else item.name
            price = item["price"] if isinstance(item, dict) else item.price
            count = item["count"] if isinstance(item, dict) else item.price
            image_path = item["sprite_path"] if isinstance(item, dict) else item.sprite_path
            
            #卡片位置
            card_x = window_x + 20
            card_y = window_y + y_offset + i * 80
            

            # 畫卡片背景卡片
            screen.blit(card_bg_image, (card_x, card_y))

            #畫商品圖片
            image_path=ASSET+image_path
            i_image =pg.image.load(image_path).convert_alpha()
            i_image = pg.transform.scale(i_image,(45, 45))
            screen.blit(i_image, (card_x +20, card_y+5))
            
            #畫商品名稱
            font_small = pg.font.Font(None, 28)
            name_text = font_small.render(f"{name} *{count}", True, (0, 0, 0))
            screen.blit(name_text, (card_x +80, card_y +10))

            #畫商品價格
            price_text = font_small.render(f"{price}$", True, (30,30, 30))
            screen.blit(price_text, (card_x +300, card_y +10))
            
            
        screen.set_clip(None)
        
        #提示字
        if self.msg:
            font_msg = pg.font.Font(None, 36)
            msg_surf = font_msg.render(self.msg, True, (255, 255, 255))
            screen.blit(
                msg_surf,
                (GameSettings.SCREEN_WIDTH - msg_surf.get_width()-30,
                GameSettings.SCREEN_HEIGHT - msg_surf.get_height()-30)
            )
            
            
        #畫按鈕
        self.back_button.draw(screen)
        self.buy_button.draw(screen)
        self.sell_button.draw(screen)
        for button in self.items_buttons:
            button.draw(screen)
        for own in self.game_manager.bag._items_data:
            if own["name"]=="Coins":
                coins = own
        
        #畫有多少錢
        coin_card_bg_path = ASSET+"UI/raw/UI_Flat_Frame03a.png"
        coin_card_bg_image = pg.image.load(coin_card_bg_path).convert_alpha()
        coin_card_bg_image = pg.transform.scale(coin_card_bg_image, (130, 40))
        screen.blit(coin_card_bg_image, (window_x +580, window_y+400))
        coin_text = font_small.render(f"coins:{coins['count']}", True, (0, 0, 0))
        screen.blit(coin_text,(window_x +580+20, window_y+400+10))
        
        #畫buy,sell字
        buy_mode_text = font_small.render("Buy", True, (0, 0, 0))
        screen.blit(buy_mode_text, (px-340+20, py -200+15))
        sell_mode_text = font_small.render("Sell", True, (0, 0, 0))
        screen.blit(sell_mode_text, (px-240+20, py -200+15))
