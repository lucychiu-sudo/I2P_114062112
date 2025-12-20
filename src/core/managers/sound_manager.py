import pygame as pg
from src.utils import load_sound, GameSettings

class SoundManager:
    def __init__(self):
        pg.mixer.init()
        pg.mixer.set_num_channels(GameSettings.MAX_CHANNELS)
        self.current_bgm = None
        self.bgm_volume = GameSettings.AUDIO_VOLUME   # 0~1
        self.bgm_enabled = GameSettings.BGM_ENABLED
        

    def play_bgm(self, filepath: str):
        if self.current_bgm:
            self.current_bgm.stop()
        if not self.bgm_enabled:
            return
        audio = load_sound(filepath)
        audio.set_volume(self.bgm_volume)
        audio.play(-1)
        self.current_bgm = audio
        
    def init_bgm_state(self):
        """在切換場景或啟動遊戲時，保持 BGM 狀態與音量"""
        self.bgm_enabled = getattr(GameSettings, "BGM_ENABLED", True)
        if self.bgm_enabled:
            self.resume_all()
        else:
            self.pause_all()
        self.set_bgm_volume(GameSettings.AUDIO_VOLUME)
        
    def set_bgm_volume(self, v: float):
        """Set BGM volume (0~1)."""
        self.bgm_volume = max(0.0, min(1.0, v))
        GameSettings.AUDIO_VOLUME = self.bgm_volume
        if self.current_bgm and self.bgm_enabled:
            self.current_bgm.set_volume(self.bgm_volume)

    def get_bgm_volume(self) -> float:
        """Return current BGM volume (0~1)."""
        return self.bgm_volume
    
    def pause_all(self):
        self.bgm_enabled = False
        GameSettings.BGM_ENABLED = False
        pg.mixer.pause()

    def resume_all(self):
        self.bgm_enabled = True
        GameSettings.BGM_ENABLED = True
        pg.mixer.unpause()
        
    def play_sound(self, filepath):
        if not self.bgm_enabled:
            return
        sound = load_sound(filepath)
        sound.set_volume(self.bgm_volume)
        self.pause_all()
        sound.play()
        self.resume_all()

    def stop_all_sounds(self):
        pg.mixer.stop()
        self.current_bgm = None