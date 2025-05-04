# tests/game/test_main.py
import os
import pygame
import pytest
from unittest.mock import MagicMock

# headless 模式
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
try:
    pygame.display.set_mode((1,1))
except pygame.error:
    pass

from game.main import run_game
from game.background import Background
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT

@pytest.fixture
def common_args():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    # 最简字体
    fonts = {"score": pygame.font.SysFont(None, 24)}
    # 仅需一个玩家图，其他都空
    images = {"player": pygame.Surface((10,10)), "powerups": {}}
    # 只需要 player_shoot, shield_up/down, powerup_pickup, bomb
    sounds = dict.fromkeys(["player_shoot","shield_up","shield_down","powerup_pickup","bomb"], None)
    # 非 boss 关卡
    level_data = {
        "level_number": 7,
        "is_boss_level": False,
        "enemy_types": [],
        "spawn_interval": 1,
        "max_on_screen": 0,
        "enemy_speed_y_range": (1,1),
        "enemy_speed_x_range": (1,1),
        "powerup_interval": 1000000,  # 避免生成
    }
    bg = Background("", SCREEN_WIDTH, SCREEN_HEIGHT, 1)
    return screen, clock, fonts, images, sounds, level_data, bg

def test_run_game_immediate_quit(common_args):
    screen, clock, fonts, images, sounds, lvl, bg = common_args
    # 模拟用户点击关闭
    pygame.event.post(pygame.event.Event(pygame.QUIT))
    result, score, level = run_game(screen, clock, fonts, images, sounds, lvl, bg)
    assert result == "QUIT"
    assert score == 0
    assert level == lvl["level_number"]
