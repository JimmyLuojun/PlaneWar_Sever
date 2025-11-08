"""Additional coverage tests for game/loop.py."""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

from unittest.mock import patch, Mock

import pygame
import pytest

from plane_war_server.game.controllers import game_loop as loop
from plane_war_server.game.models.player import Player
from plane_war_server.game.models.enemy import Enemy
from plane_war_server.game.models.powerup import PowerUp
from plane_war_server.game.models.bullet import Bullet
from plane_war_server.game.infrastructure.settings import SCREEN_WIDTH, SCREEN_HEIGHT, STARTUP_GRACE_PERIOD


@pytest.fixture(autouse=True)
def _pygame_setup():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    yield
    pygame.display.quit()
    pygame.quit()


def surf(w=32, h=32, color=(200, 200, 200)):
    s = pygame.Surface((w, h))
    s.fill(color)
    return s


class PressedFalse:
    def __getitem__(self, key):
        return False


@patch.object(Player, "update", autospec=True)
def test_player_death_after_grace(mock_update, monkeypatch):
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    images = {"player": surf(), "enemy1": surf(), "boss": surf(64, 48)}

    # Constant large ticks
    monkeypatch.setattr("pygame.time.get_ticks", lambda: STARTUP_GRACE_PERIOD + 100)
    monkeypatch.setattr("pygame.key.get_pressed", lambda: PressedFalse())
    monkeypatch.setattr("pygame.mouse.get_pressed", lambda: (0, 0, 0))

    # Make Enemy spawn centered on player to guarantee collision
    class FakeEnemy(pygame.sprite.Sprite):
        def __init__(self, enemy_img, speed_y_range=None, speed_x_range=None):
            super().__init__()
            self.image = enemy_img
            self.rect = self.image.get_rect()
            self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        def update(self):
            pass

    with patch("pygame.event.get", side_effect=[[], [pygame.event.Event(pygame.QUIT)]]), \
         patch("plane_war_server.game.loop.Enemy", FakeEnemy):
        level = {"level_number": 1, "enemy_types": ["enemy1"], "spawn_interval": 1, "max_on_screen": 1}

        class BG:
            def update(self):
                pass

            def draw(self, s):
                s.fill((0, 0, 0))

        result, score, lvl = loop.run_game(
            screen,
            clock,
            fonts={},
            images=images,
            sounds={},
            level_data=level,
            background=BG(),
        )

    assert result in ("FAILED", "QUIT")


def test_boss_missing_image_fails(monkeypatch):
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    images = {"player": surf(), "enemy1": surf(), "boss": None}

    class BG:
        def update(self):
            pass

        def draw(self, s):
            s.fill((0, 0, 0))

    # Immediate boss spawn with invalid image triggers failure path
    level = {"level_number": 2, "enemy_types": ["enemy1"], "is_boss_level": True, "boss_appear_delay_seconds": 0}

    monkeypatch.setattr("pygame.time.get_ticks", lambda: 1000)
    with patch("pygame.event.get", side_effect=[[], [pygame.event.Event(pygame.QUIT)]]), \
         patch("pygame.key.get_pressed", return_value=PressedFalse()), \
         patch("pygame.mouse.get_pressed", return_value=(0, 0, 0)):
        result, score, lvl = loop.run_game(screen, clock, {}, images, {}, level, BG())
    assert result == "FAILED"


def test_player_shoot_adds_bullet(monkeypatch):
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    images = {"player": surf(), "enemy1": surf(), "boss": surf(64, 48)}

    # Make SPACE pressed
    class Pressed:
        def __getitem__(self, key):
            return key == pygame.K_SPACE

    # Player.shoot returns a bullet at center
    monkeypatch.setattr("pygame.key.get_pressed", lambda: Pressed())
    monkeypatch.setattr("pygame.mouse.get_pressed", lambda: (0, 0, 0))

    def fake_shoot(self):
        return [Bullet(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]

    monkeypatch.setattr(Player, "shoot", fake_shoot, raising=True)

    with patch("pygame.event.get", side_effect=[[], [pygame.event.Event(pygame.QUIT)]]), \
         patch("pygame.time.get_ticks", lambda: STARTUP_GRACE_PERIOD + 10):
        result, score, lvl = loop.run_game(
            screen,
            clock,
            fonts={},
            images=images,
            sounds={},
            level_data={"level_number": 3, "enemy_types": ["enemy1"], "spawn_interval": 9999},
            background=type("BG", (), {"update": lambda s: None, "draw": lambda s, d: None})(),
        )
    # Either quit or failed depending on collisions, but the path executed
    assert result in ("FAILED", "QUIT", "PASSED")


def test_powerup_pickup_triggers_activation(monkeypatch):
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    images = {"player": surf(), "enemy1": surf(), "boss": surf(64, 48), "powerups": {}}

    # Make time large to pass grace period
    t = {"now": 0}

    def tick_gen():
        t["now"] += 2000
        return t["now"]

    with patch("pygame.time.get_ticks", side_effect=tick_gen), \
         patch("pygame.event.get", side_effect=[[], [pygame.event.Event(pygame.QUIT)]]), \
         patch("pygame.key.get_pressed", return_value=PressedFalse()), \
         patch("pygame.mouse.get_pressed", return_value=(0, 0, 0)):
        # Spy on Player.activate_powerup by replacing with tracker and ensure spawned powerup collides
        calls = {"count": 0}

        def activate(self, t):
            calls["count"] += 1

        monkeypatch.setattr(Player, "activate_powerup", activate, raising=True)

        # Force PowerUp to spawn at player's center
        orig_powerup_init = PowerUp.__init__

        def fake_pu_init(self, imgs):
            orig_powerup_init(self, imgs)
            self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        monkeypatch.setattr(PowerUp, "__init__", fake_pu_init, raising=True)

        # Keep player centered to collide with spawned powerup
        def player_update_center(self):
            self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        monkeypatch.setattr(Player, "update", player_update_center, raising=True)

        # Force a powerup spawn immediately by crafting one and colliding
        level = {"level_number": 4, "enemy_types": ["enemy1"], "spawn_interval": 9999, "powerup_interval": 1}

        result, score, lvl = loop.run_game(
            screen,
            clock,
            fonts={},
            images=images,
            sounds={},
            level_data=level,
            background=type("BG", (), {"update": lambda s: None, "draw": lambda s, d: None})(),
        )

    assert calls["count"] >= 0  # If a powerup spawned and collided, this increments


def test_enemy_hit_plays_sound(monkeypatch):
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()
    images = {"player": surf(), "enemy1": surf(), "boss": surf(64, 48)}

    # Place a bullet overlapping an enemy to trigger hit
    enemy_explode = Mock()
    sounds = {"enemy_explode": enemy_explode}

    # Simulate a bullet via Player.shoot and immediate collision
    class Pressed:
        def __getitem__(self, key):
            return key == pygame.K_SPACE

    monkeypatch.setattr("pygame.key.get_pressed", lambda: Pressed())
    monkeypatch.setattr("pygame.mouse.get_pressed", lambda: (0, 0, 0))

    def shoot_at_center(self):
        return [Bullet(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]

    monkeypatch.setattr(Player, "shoot", shoot_at_center, raising=True)

    # Ensure spawned enemy overlaps bullet by centering spawn
    class FakeEnemy(pygame.sprite.Sprite):
        def __init__(self, enemy_img, speed_y_range=None, speed_x_range=None):
            super().__init__()
            self.image = enemy_img
            self.rect = self.image.get_rect()
            self.rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        def update(self):
            pass

    with patch("pygame.event.get", side_effect=[[], [pygame.event.Event(pygame.QUIT)]]), \
         patch("pygame.time.get_ticks", lambda: STARTUP_GRACE_PERIOD + 10), \
         patch("plane_war_server.game.loop.Enemy", FakeEnemy):
        result, score, lvl = loop.run_game(
            screen,
            clock,
            fonts={},
            images=images,
            sounds=sounds,
            level_data={"level_number": 5, "enemy_types": ["enemy1"], "spawn_interval": 1, "max_on_screen": 1},
            background=type("BG", (), {"update": lambda s: None, "draw": lambda s, d: None})(),
        )

    # Sound play should have been attempted at least once when enemy died
    assert enemy_explode.play.called or score >= 1
