# tests/game/test_bullet.py
import os
import pytest
import pygame
from unittest.mock import MagicMock
from game.bullet import EnemyBullet
from game.settings import SCREEN_HEIGHT, SCREEN_WIDTH, ENEMY_BULLET_SPEED_Y

# ——— 1) headless init so pygame.Surface/get_rect work in CI ———
os.environ["SDL_VIDEODRIVER"] = "dummy"
pygame.init()
try:
    pygame.display.set_mode((1, 1))
except pygame.error:
    pass

# ——— 2) prepare our mocks ———
# a) fake surface + rect
mock_bullet_surface = MagicMock(spec=pygame.Surface)
mock_bullet_rect_attrs = {
    'center': (100,  50),
    'top':    45, 'bottom': 55,
    'left':   95, 'right': 105,
    'width':  10, 'height': 10,
}
mock_bullet_rect = MagicMock(spec=pygame.Rect, **mock_bullet_rect_attrs)
mock_bullet_surface.get_rect.return_value = mock_bullet_rect

# b) fake Vector2 constructor
from pygame.math import Vector2 as RealV2
def vector2_constructor(*args):
    inst = MagicMock(spec=RealV2)
    # initialize x,y
    if len(args) == 2:
        inst.x, inst.y = float(args[0]), float(args[1])
    elif len(args) == 1 and hasattr(args[0], "__iter__"):
        inst.x, inst.y = float(args[0][0]), float(args[0][1])
    else:
        inst.x = inst.y = 0.0

    # define arithmetic
    inst.__add__.side_effect = lambda other: vector2_constructor(inst.x + other.x,
                                                                 inst.y + other.y)
    inst.__mul__.side_effect = lambda scalar: vector2_constructor(inst.x * float(scalar),
                                                                  inst.y * float(scalar))
    return inst

mock_vector2_class = vector2_constructor

# ——— 3) monkeypatch BOTH Surface and Vector2 in game.bullet ———
@pytest.fixture(autouse=True)
def patch_bullet_math_and_surface(monkeypatch):
    import game.bullet as gb
    # patch Surface so every new Surface(...) returns our mock
    monkeypatch.setattr(gb.pygame, "Surface",
                        lambda *args, **kwargs: mock_bullet_surface)
    # patch Vector2 so Vector2(...) → our fake constructor
    monkeypatch.setattr(gb, "Vector2", mock_vector2_class)

# ——— 4) helper factories (unchanged) ———
def create_straight_bullet():
    mock_bullet_surface.get_rect.return_value = MagicMock(spec=pygame.Rect,
                                                          **mock_bullet_rect_attrs)
    b = EnemyBullet(x=100, y=50, direction=None)
    assert b.image is mock_bullet_surface
    assert b.rect  is mock_bullet_surface.get_rect.return_value
    return b

def create_angled_bullet():
    mock_bullet_surface.get_rect.return_value = MagicMock(spec=pygame.Rect,
                                                          **mock_bullet_rect_attrs)
    dir_vec = mock_vector2_class(0.6, 0.8)
    dir_vec.normalize.return_value = dir_vec
    b = EnemyBullet(x=100, y=50, direction=dir_vec)
    assert b.image is mock_bullet_surface
    assert b.rect  is mock_bullet_surface.get_rect.return_value
    return b

# ——— 5) the eight tests (only signatures changed: no args) ———

def test_enemy_bullet_init_straight():
    b = create_straight_bullet()
    assert isinstance(b, EnemyBullet)
    assert b.velocity.x == pytest.approx(0)
    assert b.velocity.y == pytest.approx(ENEMY_BULLET_SPEED_Y)
    assert b.pos.x == mock_bullet_rect_attrs['center'][0]
    assert b.pos.y == mock_bullet_rect_attrs['center'][1]

def test_enemy_bullet_init_angled():
    b = create_angled_bullet()
    assert isinstance(b, EnemyBullet)
    assert b.velocity.x == pytest.approx(0.6 * ENEMY_BULLET_SPEED_Y)
    assert b.velocity.y == pytest.approx(0.8 * ENEMY_BULLET_SPEED_Y)
    assert b.pos.x == mock_bullet_rect_attrs['center'][0]
    assert b.pos.y == mock_bullet_rect_attrs['center'][1]

def test_enemy_bullet_update_straight():
    b = create_straight_bullet()
    initial_y = b.pos.y
    b.rect.center = mock_bullet_rect_attrs['center']
    b.update()
    assert b.pos.x == mock_bullet_rect_attrs['center'][0]
    assert b.pos.y == pytest.approx(initial_y + ENEMY_BULLET_SPEED_Y)
    assert b.rect.center == (b.pos.x, b.pos.y)

def test_enemy_bullet_update_angled():
    b = create_angled_bullet()
    ix, iy = b.pos.x, b.pos.y
    b.rect.center = mock_bullet_rect_attrs['center']
    b.update()
    exp_x = ix + 0.6 * ENEMY_BULLET_SPEED_Y
    exp_y = iy + 0.8 * ENEMY_BULLET_SPEED_Y
    assert b.pos.x == pytest.approx(exp_x)
    assert b.pos.y == pytest.approx(exp_y)
    assert b.rect.center == (b.pos.x, b.pos.y)

def test_enemy_bullet_kill_offscreen_bottom():
    b = create_straight_bullet()
    b.kill = MagicMock()
    # push it just over bottom
    b.rect = MagicMock(spec=pygame.Rect, top=SCREEN_HEIGHT+1,
                       centerx=0, centery=SCREEN_HEIGHT+1)
    b.pos = mock_vector2_class(b.rect.centerx, b.rect.centery)
    b.update()
    b.kill.assert_called_once()

def test_enemy_bullet_kill_offscreen_side_left():
    b = create_angled_bullet()
    b.kill = MagicMock()
    b.rect = MagicMock(spec=pygame.Rect, right=-1, left=-11,
                       centerx=-6, centery=50)
    b.pos = mock_vector2_class(b.rect.centerx, b.rect.centery)
    b.velocity = mock_vector2_class(-5, 5)
    b.update()
    b.kill.assert_called_once()

def test_enemy_bullet_kill_offscreen_side_right():
    b = create_angled_bullet()
    b.kill = MagicMock()
    b.rect = MagicMock(spec=pygame.Rect,
                      left=SCREEN_WIDTH+1, right=SCREEN_WIDTH+11,
                      centerx=SCREEN_WIDTH+6, centery=50)
    b.pos = mock_vector2_class(b.rect.centerx, b.rect.centery)
    b.velocity = mock_vector2_class(5, 5)
    b.update()
    b.kill.assert_called_once()

def test_enemy_bullet_no_kill_onscreen():
    b = create_straight_bullet()
    b.kill = MagicMock()
    cx, cy = SCREEN_WIDTH//2, SCREEN_HEIGHT//2
    b.rect = MagicMock(spec=pygame.Rect,
                       center=(cx, cy),
                       top=cy-5, bottom=cy+5,
                       left=cx-5, right=cx+5)
    b.pos = mock_vector2_class(b.rect.center)
    b.velocity = mock_vector2_class(0, ENEMY_BULLET_SPEED_Y)
    b.update()
    b.kill.assert_not_called()
