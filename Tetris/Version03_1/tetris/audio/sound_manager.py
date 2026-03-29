"""音效管理器模块"""

import os
import pygame

from ..utils import get_resource_path


class SoundManager:
    """音效管理器"""

    def __init__(self):
        self.sounds = {}
        self.bgm_tracks = []
        self.current_bgm_index = 0
        self.bgm_playing = False
        self.bgm_paused = False
        self.bgm_delay_timer = 0
        self.waiting_for_next_bgm = False
        self.bgm_volume = 0.8  # BGM音量 (0.0 - 1.0)
        self.load_sounds()

    def load_sounds(self) -> None:
        """加载所有音效"""
        audio_dir = get_resource_path("audio")

        # 加载背景音乐 (BGM1, BGM2, BGM3)
        for i in range(1, 4):
            bgm_path = os.path.join(audio_dir, f"1. BGM{i}.mp3")
            if os.path.exists(bgm_path):
                self.bgm_tracks.append(bgm_path)

        # 加载音效及其音量设置
        sound_files = {
            'game_over': ("2. Game Over.wav", 1),
            'drop': ("3. Drop.wav", 0.5),
            'move': ("4. Move.wav", 0.4),
            'land': ("5. Land.wav", 1),
            'rotation': ("6. Rotation.wav", 0.3),
            'level_up': ("8. Level Up.wav", 1),
            'tetris': ("9. TETRIS.wav", 1),
            'clear_line': ("10. Clear Line.wav", 1),
            'plummet': ("11. Plummet .wav", 0.5),  # 注意文件名有空格
        }

        for key, (filename, volume) in sound_files.items():
            path = os.path.join(audio_dir, filename)
            if os.path.exists(path):
                try:
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(volume)
                    self.sounds[key] = sound
                except Exception:
                    pass

        # 加载连击音效 (Combo01-08)
        for i in range(1, 9):
            combo_path = os.path.join(audio_dir, f"7. Combo{i:02d}.wav")
            if os.path.exists(combo_path):
                try:
                    sound = pygame.mixer.Sound(combo_path)
                    sound.set_volume(1)
                    self.sounds[f'combo_{i}'] = sound
                except Exception:
                    pass

    def play_bgm(self) -> None:
        """开始播放背景音乐"""
        if not self.bgm_tracks:
            return
        self.bgm_playing = True
        self.current_bgm_index = 0
        self.waiting_for_next_bgm = False
        self.bgm_delay_timer = 0
        pygame.mixer.music.load(self.bgm_tracks[0])
        pygame.mixer.music.set_volume(self.bgm_volume)
        pygame.mixer.music.play()

    def stop_bgm(self) -> None:
        """停止背景音乐"""
        pygame.mixer.music.stop()
        self.bgm_playing = False
        self.bgm_paused = False
        self.waiting_for_next_bgm = False

    def pause_bgm(self) -> None:
        """暂停背景音乐"""
        if self.bgm_playing and not self.bgm_paused:
            pygame.mixer.music.pause()
            self.bgm_paused = True

    def resume_bgm(self) -> None:
        """恢复背景音乐"""
        if self.bgm_playing and self.bgm_paused:
            pygame.mixer.music.unpause()
            self.bgm_paused = False

    def update_bgm(self, dt: float) -> None:
        """更新背景音乐状态"""
        if not self.bgm_playing or self.bgm_paused:
            return

        # 检查是否在等待下一首BGM
        if self.waiting_for_next_bgm:
            self.bgm_delay_timer += dt
            if self.bgm_delay_timer >= 1.0:
                self.waiting_for_next_bgm = False
                self.bgm_delay_timer = 0
                self._play_next_bgm()
            return

        # 检查当前BGM是否播放完毕
        if not pygame.mixer.music.get_busy():
            # 如果是第3首（索引2），循环播放
            if self.current_bgm_index == 2:
                pygame.mixer.music.set_volume(self.bgm_volume)
                pygame.mixer.music.play()
            else:
                # 等待1秒后播放下一首
                self.waiting_for_next_bgm = True
                self.bgm_delay_timer = 0

    def _play_next_bgm(self) -> None:
        """播放下一首背景音乐"""
        if self.current_bgm_index < 2:
            self.current_bgm_index += 1
        pygame.mixer.music.load(self.bgm_tracks[self.current_bgm_index])
        pygame.mixer.music.set_volume(self.bgm_volume)
        pygame.mixer.music.play()

    def play_sound(self, sound_name: str) -> None:
        """播放音效"""
        if sound_name in self.sounds:
            self.sounds[sound_name].play()

    def play_combo(self, combo_count: int) -> None:
        """播放连击音效"""
        if combo_count < 1 or combo_count > 8:
            combo_count = min(8, max(1, combo_count))
        sound_key = f'combo_{combo_count}'
        if sound_key in self.sounds:
            self.sounds[sound_key].play()