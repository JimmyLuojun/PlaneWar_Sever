# tests/game/test_enemy.py
import os
import random
import pygame
import pytest
from unittest.mock import MagicMock

# 强制 headless 模式
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
try:
    pygame.display.set_mode((1,1))
except pygame.error:
    pass

from game.enemy import Enemy, EnemyBoss
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ENEMY_MIN_SPEED_Y, ENEMY_MAX_SPEED_Y,
    ENEMY_MIN_SPEED_X, ENEMY_MAX_SPEED_X,
    BOSS_SPEED_Y, BOSS_ENTRY_Y,
    BOSS_SPEED_X, BOSS_SHOOT_DELAY,
    BOSS_MAX_HEALTH,
)

# 一个简单的 Surface mock
mock_img = MagicMock(spec=pygame.Surface)
mock_rect = MagicMock(spec=pygame.Rect)
mock_rect.width = 20
mock_rect.height = 20
mock_img.get_rect.return_value = mock_rect

def test_enemy_init_default_speed_ranges(monkeypatch):
    # randint 返回最小值，choice 取列表首项
    monkeypatch.setattr(random, "randint", lambda a,b: a)
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    e = Enemy(enemy_img=mock_img)
    # x,y 分别是 randint 返回的 a 和 -100
    assert e.rect.x == 0
    assert e.rect.y == -100
    # 垂直速度在合法范围内
    assert ENEMY_MIN_SPEED_Y <= e.speedy <= ENEMY_MAX_SPEED_Y
    # 水平速度不为 0
    assert e.speedx != 0

def test_enemy_update_movement_and_bounce(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a,b: a)
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    # 制造一个左右速度都可控的敌人
    e = Enemy(enemy_img=mock_img, speed_y_range=(5,5), speed_x_range=(3,3))
    # 放到屏幕右边缘外
    e.rect.right = SCREEN_WIDTH + 1
    e.rect.left = e.rect.right - e.rect.width
    # 更新并测试反弹
    old_speedx = e.speedx
    e.update()
    assert e.speedx == -old_speedx
    # 位置被 clamp 到 SCREEN_WIDTH
    assert e.rect.right <= SCREEN_WIDTH

def test_enemy_update_kill_offscreen(monkeypatch):
    monkeypatch.setattr(random, "randint", lambda a,b: a)
    monkeypatch.setattr(random, "choice", lambda seq: seq[0])
    e = Enemy(enemy_img=mock_img)
    e.kill = MagicMock()
    # 放到屏幕底部外
    e.rect.top = SCREEN_HEIGHT + 1
    e.update()
    e.kill.assert_called_once()

def test_enemyboss_init_and_take_damage():
    all_sprites = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    boss_img = mock_img.copy()
    shoot_sound = MagicMock()
    boss = EnemyBoss(
        boss_img, shoot_sound,
        all_sprites, enemy_bullets,
        target_player=False
    )
    # 初始状态检查
    assert boss.rect.centerx == SCREEN_WIDTH // 2
    assert boss.rect.bottom == -20
    assert not boss.entered
    assert boss.health == boss.max_health == BOSS_MAX_HEALTH

    boss.take_damage(7)
    assert boss.health == BOSS_MAX_HEALTH - 7

def test_enemyboss_shoot_straight(monkeypatch):
    all_sprites = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    boss_img = mock_img.copy()
    sound = MagicMock()
    boss = EnemyBoss(
        boss_img, sound,
        all_sprites, enemy_bullets,
        target_player=False
    )
    # 直接调用 shoot
    boss.shoot()
    # 子弹加进了组
    assert len(enemy_bullets) == 1
    bullet = next(iter(enemy_bullets))
    # 直射：速度向量 x=0
    assert pytest.approx(0) == bullet.velocity.x

def test_enemyboss_shoot_target(monkeypatch):
    all_sprites = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    boss_img = mock_img.copy()
    sound = MagicMock()
    # 准备一个伪玩家
    player = MagicMock()
    player.rect.center = (30, 80)
    player.alive.return_value = True

    boss = EnemyBoss(
        boss_img, sound,
        all_sprites, enemy_bullets,
        target_player=True, player_ref=player
    )
    # 伪造发射点
    boss.rect.midbottom = (30, 10)
    boss.shoot()
    bullet = next(iter(enemy_bullets))
    v = bullet.velocity
    from math import isclose
    mag = (v.x**2 + v.y**2)**0.5
    # 斜射：方向被规范化后乘 speed => 长度约等于 speed
    assert isclose(mag, bullet.speed, rel_tol=1e-3)

def test_draw_health_bar(monkeypatch):
    all_sprites = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    boss = EnemyBoss(
        mock_img.copy(), None,
        all_sprites, enemy_bullets
    )
    boss.health = boss.max_health // 2
    surf = MagicMock(spec=pygame.Surface)
    calls = []

    def fake_rect(surface, color, rect, width=0):
        calls.append((color, rect.width, rect.height, width))

    monkeypatch.setattr(pygame.draw, "rect", fake_rect)
    boss.draw_health_bar(surf)
    # 背景、填充、边框 共 3 次 draw
    assert len(calls) == 3
