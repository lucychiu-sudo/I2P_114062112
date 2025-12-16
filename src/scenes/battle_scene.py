# src/scenes/battle_scene.py
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
    
class BattleScene(Scene):
    # Background Image
    background: BackgroundSprite
    # Buttons
    back_button: Button
    _checkbox: Checkbox
    volume_slider: Slider
    
    def __init__(self, monsters_data, items_data, on_exit_scene=None):
        super().__init__()
        self.monsters = monsters_data
        self.items = items_data
        self.background = BackgroundSprite("backgrounds/background2.png")
        
        self.enemy_list= [
            { "name": "Pikachu",   "hp": 100, "max_hp": 100, "level": 14,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite1.png" },
            { "name": "Charizard", "hp": 200, "max_hp": 200, "level": 12,"attack":23,"defense":8,"element":"grass", "sprite_path": "menu_sprites/menusprite2.png" },
            { "name": "Blastoise", "hp": 180, "max_hp": 180, "level": 33,"attack":25,"defense":9,"element":"grass", "sprite_path": "menu_sprites/menusprite3.png" },
            { "name": "Venusaur",  "hp": 160, "max_hp": 160, "level": 25,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite4.png" },
            { "name": "Gengar",    "hp": 140, "max_hp": 140, "level": 21,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite5.png" },
            { "name": "Dragonite", "hp": 220, "max_hp": 220, "level": 14,"attack":24,"defense":7,"element":"water", "sprite_path": "menu_sprites/menusprite6.png" },
            { "name": "Mouse",     "hp": 240, "max_hp": 240, "level": 15,"attack":20,"defense":5,"element":"fire", "sprite_path": "menu_sprites/menusprite7.png" },
            { "name": "FireMouse", "hp": 280, "max_hp": 280, "level": 17,"attack":24,"defense":8,"element":"fire", "sprite_path": "menu_sprites/menusprite8.png" },
            { "name": "GiantMouse", "hp": 300, "max_hp": 300, "level": 11,"attack":29,"defense":11,"element":"fire", "sprite_path": "menu_sprites/menusprite9.png" },
            { "name": "PurpleMouse", "hp": 150, "max_hp": 150, "level": 9,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite10.png" },
            { "name": "PurpleSnake", "hp": 200, "max_hp": 200, "level": 22,"attack":25,"defense":8,"element":"grass", "sprite_path": "menu_sprites/menusprite11.png" },
            { "name": "Dophin",      "hp": 220, "max_hp": 220, "level": 18,"attack":20,"defense":5,"element":"water", "sprite_path": "menu_sprites/menusprite12.png" },
            { "name": "BigDophin",   "hp": 230, "max_hp": 230, "level": 19,"attack":26,"defense":9,"element":"water", "sprite_path": "menu_sprites/menusprite13.png" },
            { "name": "LargeDophin", "hp": 250, "max_hp": 250, "level": 20,"attack":31,"defense":12,"element":"water", "sprite_path": "menu_sprites/menusprite14.png" },
            { "name": "Bug",         "hp": 100, "max_hp": 100, "level": 17,"attack":20,"defense":5,"element":"grass", "sprite_path": "menu_sprites/menusprite15.png" },
            { "name": "UglyBug",     "hp": 130, "max_hp": 130, "level": 15,"attack":25,"defense":10,"element":"grass", "sprite_path": "menu_sprites/menusprite16.png" }
            ]
        #敵人資料
        self.enemy=random.choice(self.enemy_list)
        self.enemy_hp = 100
        self.enemy_original_pos=(700,125)
        self.enemy_pos = self.enemy_original_pos
        self.enemy_img_path = self.enemy["sprite_path"] if isinstance(self.enemy, dict) else self.enemy.sprite_path
        self.big_enemy_img_path=self.enemy_img_path.replace("menu","")
        self.big_enemy_img_path=self.big_enemy_img_path.replace("_","")
        self.big_enemy_idle_img_path=self.big_enemy_img_path.replace(".png","_idle.png")
        #self.big_enemy_idle_img_path= ASSET+self.big_enemy_idle_img_path
        self.bid_enemy_idle_anim=Animation(self.big_enemy_idle_img_path,["idle"],4,(300,300))
        self.bid_enemy_idle_anim.rect.x,self.bid_enemy_idle_anim.rect.y=self.enemy_pos
        
        self.big_enemy_attack_img_path=self.big_enemy_img_path.replace(".png","_attack.png")
        #self.big_enemy_attack_img_path=f"assets/images/{self.big_enemy_attack_img_path}"
        self.bid_enemy_attack_anim=Animation(self.big_enemy_attack_img_path,["attack"],4,(300,300))
        self.bid_enemy_attack_anim.rect.x,self.bid_enemy_attack_anim.rect.y=self.enemy_pos
        self.enemy_anim_finished = False
        self.enemy_hit_timer = 1.0
        
        
        #怪獸資料
        for i in range(len(self.monsters)-1):
            if self.monsters[i]["hp"]>0:
                self.current_monster_index = i
                break
        self.player_monster = self.monsters[self.current_monster_index]
        
        #物品資料
        for item in self.items:
            if item["name"]=="Attack Potion":
                self.attack_potion = item
                self.add_attack = 0
            elif  item["name"]=="Heal Potion":
                self.heal_potion = item
                
            elif  item["name"]=="Defense Potion":
                self.defense_potion = item
                self.add_defense = 0
            elif item["name"]=="Coins":
                self.coins = item
        
        1
        
        #字體和偵測
        self.turn=True
        self.font = pg.font.Font(None, 36)
        self.state = "player_turn"
        self.finished = False
        self.result = None
        self.damage = 0
        self.hit_timer = 1.0
        self.original_pos = (200, 221)
        self.player_pos = self.original_pos
        self.turn_delay = 1.0
        
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
        


        #用來離開戰鬥回主畫面
        self.on_exit_scene = on_exit_scene
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 5 // 6

        #建立按鈕
        self.attack_button = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png",
            px-100, py, 70, 70,
            self.player_attack
        )
        self.attack_potion_button = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png",
            px+300, py, 70, 70,
            self.player_attack_potion
        )
        self.defense_potion_button = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png",
            px+200, py, 70, 70,
            self.player_defense_potion
        )
        self.heal_potion_button = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png",
            px+400, py, 70, 70,
            self.player_heal_potion
        )
        self.run_button = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png",
            px, py, 70, 70,
            self.player_run
        )
        self.switch_button = Button(
            "UI/raw/UI_Flat_Button02a_3.png", "UI/raw/UI_Flat_Button02a_1.png",
            px+100, py, 70, 70,
            self.player_switch
        )
        
    @override
    def enter(self) -> None:
        sound_manager.play_bgm("RBY 149 Victory Road.ogg")
        pass
    
    def show_message(self, text, duration=0.8):
        self.msg = text
        self.msg_timer = duration
    
    '''玩家換怪獸'''
    def player_switch(self):
        #切換到下一隻怪獸，不消耗回合
        self.current_monster_index += 1
        if self.current_monster_index >= len(self.monsters):
            self.current_monster_index = 0  #循環回第一隻
        self.player_monster = self.monsters[self.current_monster_index]
        #self.battle_potion_overlay = BattlePotionOverlay(self.attack_potion,self.heal_potion,self.defense_potion,self.player_monster)
        
    def element_stronger(self,attacker,other):
        if attacker["element"]=="water" and other["element"]=="fire":
            return True
        elif attacker["element"]=="fire" and other["element"]=="grass":
            return True
        elif attacker["element"]=="grass" and other["element"]=="water":
            return True
        else:
            return False
        
    '''玩家攻擊'''
    def player_attack(self):
        #不是玩家的回合就不要做事
        if self.state!="player_turn" or self.finished:
            return
        #用level當attack值
        if self.element_stronger(self.player_monster,self.enemy):
            self.player_monster["attack"]+=5
        self.damage = max(1,int(self.player_monster["attack"]+self.add_attack-self.enemy["defense"]))
        self.enemy["hp"] -= self.damage
        if self.element_stronger(self.player_monster,self.enemy):
            self.player_monster["attack"]-=5
            
        #判斷敵人被攻擊完有沒有死
        if self.enemy["hp"] <= 0:
            self.enemy["hp"] = 0
            self.finished = True
            self.result = "You Win!"
            sound_manager.play_sound("RBY 111 Victory! (Wild Pokemon).ogg")
            self.coins["count"]+=200
            self.player_monster["level"]+=1
            if self.player_monster["level"]>=10 and self.player_monster["name"] in self.evolution_map:
                old_name=self.player_monster["name"]
                
                self.player_monster["hp"] = self.evolution_map[self.player_monster["name"]]["hp"]
                self.player_monster["max_hp"] = self.evolution_map[self.player_monster["name"]]["max_hp"]
                self.player_monster["attack"] = self.evolution_map[self.player_monster["name"]]["attack"]
                self.player_monster["defense"] = self.evolution_map[self.player_monster["name"]]["defense"]
                self.player_monster["sprite_path"] = self.evolution_map[self.player_monster["name"]]["sprite_path"]
                self.player_monster["level"] =1
                self.player_monster["name"] = self.evolution_map[self.player_monster["name"]]["name"]
                self.evolution = True
                self.evolution_text = f"{old_name} has evolute to {self.player_monster['name']}"
            return
        #進入下一個狀態，敵人震動，設好震動時間
        self.state = "enemy_hit"      
        self.enemy_hit_timer = 1.0
        
        
    '''玩家逃跑'''
    def player_run(self):
        if self.state!="player_turn" or self.finished:
            return
        self.finished = True
        self.result = "You ran away."
        
    '''玩家家防禦'''
    def player_defense_potion(self):
        if self.state!="player_turn" or self.finished:
            return
        if self.defense_potion["count"]>0:
            self.add_defense+=10
            self.defense_potion["count"]-=1
            self.show_message(f"Using defense potion...")
        
    '''玩家加攻擊'''
    def player_attack_potion(self):
        if self.state!="player_turn" or self.finished:
            return
        if self.attack_potion["count"]>0:
            self.add_attack+=10
            self.attack_potion["count"]-=1
            self.show_message(f"Using attack potion...")
        
    '''玩家回血'''
    def player_heal_potion(self):
        if self.state!="player_turn" or self.finished:
            return
        if self.heal_potion["count"]>0 and self.player_monster["hp"]<self.player_monster["max_hp"]:
            self.player_monster["hp"] =min(self.player_monster["max_hp"], self.player_monster["hp"]+30)
            self.heal_potion["count"]-=1
            self.show_message(f"Using heal potion...")
    
    '''玩家震動'''
    def player_shake(self):
        offset = random.randint(-5, 5)
        self.player_pos = (self.original_pos[0] + offset, self.original_pos[1])
    
    '''玩家停止震動'''
    def reset_player_pos(self):
        self.player_pos = self.original_pos
    
    '''敵人震動'''
    def enemy_shake(self):
        offset = random.randint(-5, 5)
        self.enemy_pos = (self.enemy_original_pos[0] + offset,
                        self.enemy_original_pos[1])

    '''敵人停止震動'''
    def reset_enemy_pos(self):
        self.enemy_pos = self.enemy_original_pos
        
    def update(self, dt):
        if self.finished:
            #戰鬥結束按空白鍵退出
            if pg.key.get_pressed()[pg.K_SPACE] :
                scene_manager.change_scene("game")
            return
        
        if self.msg_timer > 0:
            self.msg_timer -= dt
            if self.msg_timer <= 0:
                self.msg = ""
                
        #玩家決定要幹嘛
        if self.state=="player_turn":
            
            self.turn=True #是玩家回合
            self.attack_button.update(dt) 
            self.run_button.update(dt)
            self.switch_button.update(dt)
            self.defense_potion_button.update(dt)
            self.attack_potion_button.update(dt)
            self.heal_potion_button.update(dt)
            self.bid_enemy_idle_anim.update(dt)
            
            return
        
        #敵人準備做攻擊動畫
        elif self.state == "enemy_prepare":
            self.turn=False
            self.bid_enemy_attack_anim.reset()   
            self.enemy_anim_finished = False
            self.state = "enemy_anim"
            return

        #敵人做攻擊動畫
        elif self.state == "enemy_anim":
            self.turn=False
            self.bid_enemy_attack_anim.update(dt)

            #計算當前動畫幀
            #(以播放時常//週期)*一周期的幀數
            current_frame = int((self.bid_enemy_attack_anim.accumulator / self.bid_enemy_attack_anim.loop) *
                                self.bid_enemy_attack_anim.n_keyframes)

            #如果動畫達到最後一幀，就認為播放完成
            if current_frame >= self.bid_enemy_attack_anim.n_keyframes - 1:
                self.enemy_anim_finished = True

            #播完動畫之後，玩家震動
            if self.enemy_anim_finished:
                self.state = "player_hit"
                self.hit_timer = 1.0  #玩家震動 1 秒
            return

        #玩家震動
        elif self.state == "player_hit":
            self.turn=False
            if self.element_stronger(self.enemy,self.player_monster):
                self.enemy["attack"]+=5
            self.damage = max(1,int(self.enemy["attack"]-self.add_defense-self.player_monster["defense"]))
            if self.element_stronger(self.enemy,self.player_monster):
                self.enemy["attack"]-=5
            #一直呼叫震動函示直到震動時間結束
            self.hit_timer -= dt
            self.player_shake()

            if self.hit_timer <= 0:
                self.reset_player_pos()

                #扣血（在動畫完後才扣）
                
                self.player_monster["hp"] -= self.damage
                if self.element_stronger(self.enemy,self.player_monster):
                    self.enemy["attack"]-=5
                if self.player_monster["hp"] <= 0:
                    self.player_monster["hp"] = 0
                    self.finished = True
                    self.result = "You Lose!"
                    sound_manager.play_sound("RBY 129 Badge Acquired.ogg")
                    return
                #設置緩衝時間，進入緩衝狀態
                self.turn_delay = 1.0
                self.state = "turn_delay"
            return
        
        #緩衝狀態，從敵人回合到玩家回合
        elif self.state == "turn_delay":
            self.turn=False
            self.turn_delay -= dt
            if self.turn_delay <= 0:
                self.state = "player_turn"
                
        #緩衝狀態，從玩家回合到敵人回合
        elif self.state == "enemy_turn_delay":
            self.turn=False
            self.turn_delay -= dt
            if self.turn_delay <= 0:
                self.state = "enemy_prepare"
                
        #敵人震動
        elif self.state == "enemy_hit":
            self.turn=True
            self.enemy_hit_timer -= dt
            self.enemy_shake()

            if self.enemy_hit_timer <= 0:
                self.reset_enemy_pos()
                #去緩衝狀態
                self.turn_delay = 2.0
                self.state = "enemy_turn_delay"

    def draw_enemy_card(self, screen: pg.Surface):
        """右上角顯示敵人卡片"""
        card_bg_path =pg.image.load(f"assets/images/UI/raw/UI_Flat_Banner03a.png").convert_alpha()
        card_bg_image = pg.transform.scale(card_bg_path, (370, 70))
        card_x =850
        card_y =GameSettings.SCREEN_HEIGHT-680

        #背景卡片
        
        screen.blit(card_bg_image, (card_x, card_y))

        #敵人小圖片
        enemy_img = pg.image.load(f"assets/images/{self.enemy['sprite_path']}").convert_alpha()
        enemy_img = pg.transform.scale(enemy_img, (64, 64))
        screen.blit(enemy_img, (card_x + 15, card_y-10))
        
        #敵人大圖
        if self.state in ["enemy_anim", "enemy_prepare", "enemy_hit"]:
            self.bid_enemy_attack_anim.rect.topleft = self.enemy_pos
            self.bid_enemy_attack_anim.draw(screen, None)
        else:
            #原本的大圖
            self.bid_enemy_idle_anim.rect.topleft = self.enemy_pos
            self.bid_enemy_idle_anim.draw(screen, None)
        
        #敵人名字與等級
        font = pg.font.Font(None, 28)
        name_text = self.enemy["name"] if isinstance(self.enemy, dict) else self.enemy.name
        level = self.enemy["level"] if isinstance(self.enemy, dict) else self.enemy.level
        name_surf = font.render(f"{name_text}  Lv.{level}", True, (0, 0, 0))
        screen.blit(name_surf, (card_x + 85,card_y+ 10))

        #敵人HP條
        hp = self.enemy["hp"] if isinstance(self.enemy, dict) else self.enemy.hp
        max_hp = self.enemy["max_hp"] if isinstance(self.enemy, dict) else self.enemy.max_hp
        hp_bar_width = 140
        hp_bar_height = 15
        hp_x =card_x+ 85
        hp_y =card_y+ 32
        #底色
        pg.draw.rect(screen, (150, 150, 150), (hp_x, hp_y, hp_bar_width, hp_bar_height))
        #實際 HP
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
        
    def draw_monster_card(self, screen: pg.Surface):
        """左下角顯示怪獸卡片"""
        card_bg_path = ASSET+ "UI/raw/UI_Flat_Banner03a.png"
        card_bg_image = pg.image.load(card_bg_path).convert_alpha()
        card_bg_image = pg.transform.scale(card_bg_image, (370, 70))
        card_x =20
        card_y =GameSettings.SCREEN_HEIGHT-180
        card_w, card_h = 300, 70

        #背景卡片
        
        screen.blit(card_bg_image, (card_x, card_y))

        #怪獸圖片
        monster_img_path = self.player_monster["sprite_path"] if isinstance(self.player_monster, dict) else self.player_monster.sprite_path
        monster_img_path=f"assets/images/{monster_img_path}"
        monster_img = pg.image.load(monster_img_path).convert_alpha()
        monster_img = pg.transform.scale(monster_img, (64, 64))
        screen.blit(monster_img, (card_x + 15, card_y-10))
        #怪獸大圖
        big_img_path=monster_img_path.replace("menu","")
        big_img_path=big_img_path.replace("_","")
        #big_img_path=f"assets/images/{big_img_path}"
        big_img = pg.image.load(big_img_path).convert_alpha()
        big_img = pg.transform.scale(big_img, (600, 300))
        big_img = crop_image(big_img, 300, 0, 300, 300)
        screen.blit(big_img, self.player_pos)
        
        #名字與等級
        font = pg.font.Font(None, 28)
        name_text = self.player_monster["name"] if isinstance(self.player_monster, dict) else self.player_monster.name
        level = self.player_monster["level"] if isinstance(self.player_monster, dict) else self.player_monster.level
        name_surf = font.render(f"{name_text}  Lv.{level}", True, (0, 0, 0))
        screen.blit(name_surf, (card_x + 85,card_y+ 10))

        #HP條
        hp = self.player_monster["hp"] if isinstance(self.player_monster, dict) else self.player_monster.hp
        max_hp = self.player_monster["max_hp"] if isinstance(self.player_monster, dict) else self.player_monster.max_hp
        hp_bar_width = 140
        hp_bar_height = 15
        hp_x =card_x+ 85
        hp_y =card_y+ 32
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
        
    def draw_button_area(self, screen: pg.Surface):
        button_area_w = GameSettings.SCREEN_WIDTH
        button_area_h = 200
        button_area_x = 0
        button_area_y = GameSettings.SCREEN_HEIGHT - 200
        
        overlay = pg.Surface((button_area_w, button_area_h), pg.SRCALPHA)
        #填好半透明白色
        overlay.fill((255, 255, 255, 150))
        # 貼到螢幕上
        screen.blit(overlay, (button_area_x, button_area_y))
        border_color = (120, 120, 120)      
        border_rect = pg.Rect(button_area_x, button_area_y, button_area_w, button_area_h)
        pg.draw.rect(screen, border_color, border_rect, width=4) 
        
        
    def draw_button_image(self, screen: pg.Surface):
        '''畫按鈕圖片'''
        px, py = GameSettings.SCREEN_WIDTH // 2, GameSettings.SCREEN_HEIGHT * 5 // 6
        #attack圖片
        attack_image_path="ingame_ui/options1.png"
        show_attack_image_path= pg.image.load(f"assets/images/{attack_image_path}").convert_alpha()
        i_attack_image = pg.transform.scale(show_attack_image_path, (30, 30))
        screen.blit(i_attack_image, (px-100+20, py+20))
        #run圖片
        run_image_path="ingame_ui/baricon1.png"
        show_run_image_path=pg.image.load(f"assets/images/{run_image_path}").convert_alpha()
        i_run_image = pg.transform.scale(show_run_image_path, (30, 30))
        screen.blit(i_run_image, (px+20, py+20))
        #switch圖片
        switch_image_path="ingame_ui/options3.png"
        show_switch_image_path=pg.image.load(f"assets/images/{switch_image_path}").convert_alpha()
        i_switch_image = pg.transform.scale(show_switch_image_path, (30, 30))
        screen.blit(i_switch_image, (px+100+20, py+20))
        #defense圖片
        defense_image_path="ingame_ui/options6.png"
        show_defense_image_path=pg.image.load(f"assets/images/{defense_image_path}").convert_alpha()
        i_defense_image = pg.transform.scale(show_defense_image_path, (30, 30))
        screen.blit(i_defense_image, (px+200+20, py+20))
        #add attack圖片
        add_attack_image_path="ingame_ui/options5.png"
        show_add_attack_image_path=pg.image.load(f"assets/images/{add_attack_image_path}").convert_alpha()
        i_add_attack_image = pg.transform.scale(show_add_attack_image_path, (30, 30))
        screen.blit(i_add_attack_image, (px+300+20, py+20))
        #heal圖片
        heal_image_path="ingame_ui/potion.png"
        show_heal_image_path=pg.image.load(f"assets/images/{heal_image_path}").convert_alpha()
        i_heal_image = pg.transform.scale(show_heal_image_path, (30, 30))
        screen.blit(i_heal_image, (px+400+20, py+20))
        
    def draw(self, screen):
        self.background.draw(screen)
        self.draw_button_area(screen)
        
        
        #戰鬥結束
        if self.finished:
            font_big=pg.font.Font(None, 80)
            screen.blit(font_big.render(self.result, True, (30,30,30)), (GameSettings.SCREEN_WIDTH//2-150, GameSettings.SCREEN_HEIGHT // 2))
            screen.blit(self.font.render("Press SPACE to exit battle", True, (0,0,0)), (GameSettings.SCREEN_WIDTH//2+300, GameSettings.SCREEN_HEIGHT-50))
            if self.evolution:
                screen.blit(self.font.render(self.evolution_text, True, (30,30,30)), (GameSettings.SCREEN_WIDTH//2+300, GameSettings.SCREEN_HEIGHT-100))
            return
        
        if self.turn == True :
            screen.blit(self.font.render("Your turn !", True, (0,0,0)), (450,550))
        else:
            screen.blit(self.font.render("Enemy's turn !", True, (0,0,0)), (450,550))
            
        if self.state == "player_hit":
            if self.element_stronger(self.enemy,self.player_monster):
                screen.blit(self.font.render(f'your hp -({self.damage}+5) !', True, (0,0,0)), (450,600))
            else:
                screen.blit(self.font.render(f'your hp -{self.damage}!', True, (0,0,0)), (450,600))
        elif self.state == "enemy_hit":
            if self.element_stronger(self.player_monster,self.enemy):
                screen.blit(self.font.render(f'enemy\'s hp -({self.damage}+5) !', True, (0,0,0)), (450,600))
            else:
                screen.blit(self.font.render(f'enemy\'s hp -{self.damage}!', True, (0,0,0)), (450,600))
            
        #呼叫函式畫怪獸和敵人卡
        self.draw_monster_card(screen)
        self.draw_enemy_card(screen)
        
        # 玩家回合顯示按鈕
        if self.state == "player_turn":
            self.attack_button.draw(screen)
            self.defense_potion_button.draw(screen)
            self.attack_potion_button.draw(screen)
            self.heal_potion_button.draw(screen)
            self.run_button.draw(screen)
            self.switch_button.draw(screen)
            self.draw_button_image(screen)
            
        #提示字
        if self.msg:
            font_msg = pg.font.Font(None, 80)
            msg_surf = font_msg.render(self.msg, True, (250, 0, 0))
            screen.blit(
                msg_surf,
                (GameSettings.SCREEN_WIDTH//4,
                GameSettings.SCREEN_HEIGHT//3)
            )
        