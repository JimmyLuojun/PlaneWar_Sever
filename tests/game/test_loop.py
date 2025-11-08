"""Tests for game/loop.py - single-level game loop logic.

Covers key branches: immediate quit, bomb usage with enemy spawning,
and boss defeat flow to ensure PASSED outcome. Uses SDL dummy drivers.
"""

import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from plane_war_server.game.controllers import game_loop as loop
from plane_war_server.game.infrastructure.settings import SCREEN_WIDTH, SCREEN_HEIGHT, BOMB_KEY
from plane_war_server.game.models.bullet import Bullet


class DummyBackground:
    def update(self):
        pass

    def draw(self, surface):
        # Fill to ensure blits happen without relying on external assets
        surface.fill((0, 0, 0))


@pytest.fixture(autouse=True)
def _pygame_setup_teardown():
    pygame.init()
    pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    yield
    pygame.display.quit()
    pygame.quit()


def make_surface(w=32, h=32, color=(200, 200, 200)):
    surf = pygame.Surface((w, h))
    surf.fill(color)
    return surf


def test_run_game_quit_immediately(monkeypatch):
    """Posting a QUIT event should return ('QUIT', 0, level_num)."""
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    # Provide minimal assets
    images = {
        "player": make_surface(),
        "enemy1": make_surface(),
        "boss": make_surface(64, 48),
    }

    # Ensure a single QUIT event then no more events
    events = [pygame.event.Event(pygame.QUIT)]

    def fake_event_get():
        nonlocal events
        if events:
            out, events = events, []
            return out
        return []

    monkeypatch.setattr(pygame.event, "get", fake_event_get)

    result, score, level_num = loop.run_game(
        screen,
        clock,
        fonts={},
        images=images,
        sounds={},
        level_data={"level_number": 1, "enemy_types": ["enemy1"]},
        background=DummyBackground(),
    )

    assert result == "QUIT"
    assert score == 0
    assert level_num == 1


def test_run_game_bomb_kills_spawned_enemy(monkeypatch):
    """Bomb key after one spawn increases score by enemies killed, then QUIT."""
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    images = {
        "player": make_surface(),
        "enemy1": make_surface(),
        "boss": make_surface(64, 48),
    }

    # Sequence: frame1 -> no events (let one enemy spawn),
    # frame2 -> bomb keydown, frame3 -> QUIT to end loop.
    event_sequences = [
        [],
        [pygame.event.Event(pygame.KEYDOWN, key=BOMB_KEY)],
        [pygame.event.Event(pygame.QUIT)],
    ]

    def fake_event_get():
        return event_sequences.pop(0) if event_sequences else []

    monkeypatch.setattr(pygame.event, "get", fake_event_get)

    # Avoid accidental shooting via keyboard/mouse
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: {i: False for i in range(512)})
    monkeypatch.setattr(pygame.mouse, "get_pressed", lambda: (0, 0, 0))

    # Fast enemy spawning: every frame
    level_data = {
        "level_number": 2,
        "enemy_types": ["enemy1"],
        "spawn_interval": 1,
        "max_on_screen": 3,
    }

    result, score, level_num = loop.run_game(
        screen,
        clock,
        fonts={},
        images=images,
        sounds={},
        level_data=level_data,
        background=DummyBackground(),
    )

    # On frame2 bomb, at least 1 enemy should have spawned and been killed
    assert result == "QUIT"
    assert score >= 1
    assert level_num == 2


def test_run_game_boss_defeat_leads_to_pass(monkeypatch):
    """Force a boss spawn and immediate defeat via a bullet collision."""
    screen = pygame.display.get_surface()
    clock = pygame.time.Clock()

    images = {
        "player": make_surface(),
        "enemy1": make_surface(),
        "boss": make_surface(64, 48),
    }

    # Fake boss that spawns at screen center with 1 HP
    class FakeBoss(pygame.sprite.Sprite):
        def __init__(self, boss_img, shoot_sound, all_sprites, enemy_bullets, **kwargs):
            super().__init__()
            self.image = boss_img
            self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.health = 1

        def draw_health_bar(self, surf):
            pass

    monkeypatch.setattr(loop, "EnemyBoss", FakeBoss)

    # Make spacebar appear pressed to trigger Player.shoot
    class _Pressed:
        def __getitem__(self, key):
            return key == pygame.K_SPACE

    monkeypatch.setattr(pygame.key, "get_pressed", lambda: _Pressed())
    monkeypatch.setattr(pygame.mouse, "get_pressed", lambda: (0, 0, 0))

    # Ensure that when Player.shoot() is called, it returns a bullet positioned
    # to collide with the boss at center of screen
    def fake_shoot(self):
        return [Bullet(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)]

    monkeypatch.setattr(loop.Player, "shoot", fake_shoot, raising=True)

    # No explicit events; loop should end with PASSED once boss is defeated
    monkeypatch.setattr(pygame.event, "get", lambda: [])

    level_data = {
        "level_number": 3,
        "is_boss_level": True,
        "boss_appear_delay_seconds": 0,  # Spawn immediately
        "enemy_types": ["enemy1"],
    }

    result, score, level_num = loop.run_game(
        screen,
        clock,
        fonts={},
        images=images,
        sounds={},
        level_data=level_data,
        background=DummyBackground(),
    )

    assert result == "PASSED"
    assert score >= 50  # Boss defeat adds 50 points
    assert level_num == 3
