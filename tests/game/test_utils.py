# tests/game/test_utils.py

import os
import json
import random
import pygame
import pytest
from game import utils
from game.settings import WHITE

# --- Dummy classes to simulate Surfaces and Sounds ---

class DummySurface:
    def __init__(self, size):
        # size: (w,h) tuple
        self.size = size
        self._colorkey = None
        self.filled = None
        self.rect = pygame.Rect(0, 0, *size)
    def fill(self, color):
        self.filled = color
    def get_rect(self):
        return self.rect
    def set_colorkey(self, key, flag):
        self._colorkey = key
    def get_at(self, pos):
        # return a dummy pixel RGBA
        return (10, 20, 30, 40)

class DummySound:
    def __init__(self, path):
        self.path = path
        self.volume = None
    def set_volume(self, v):
        self.volume = v

# --- Tests for load_and_scale_image ---

def test_load_and_scale_image_fallback(monkeypatch):
    # Path does not exist → fallback surface
    monkeypatch.setattr(os.path, "exists", lambda p: False)
    monkeypatch.setattr(pygame, "Surface", lambda size: DummySurface(size))
    monkeypatch.setattr(pygame.draw, "rect", lambda surf, col, rect, w=0: None)

    surf = utils.load_and_scale_image("no_such.png", 50, 60)
    assert isinstance(surf, DummySurface)
    assert surf.size == (50, 60)
    # fallback fill color is reddish
    assert surf.filled == (200, 50, 50)

def test_load_and_scale_image_success(monkeypatch, tmp_path):
    # Create a real file so os.path.exists returns True
    img_file = tmp_path / "test.png"
    img_file.write_text("irrelevant")

    # Dummy raw image from pygame.image.load
    class Raw:
        def convert_alpha(self): return self
        def get_at(self, pos): return (1,2,3,4)

    dummy_raw = Raw()
    scaled = DummySurface((80, 90))

    monkeypatch.setattr(os.path, "exists", lambda p: True)
    monkeypatch.setattr(pygame.image, "load", lambda p: dummy_raw)
    monkeypatch.setattr(pygame.transform, "scale", lambda img, size: scaled)
    # Test without colorkey
    out = utils.load_and_scale_image(str(img_file), 80, 90, colorkey=None)
    assert out is scaled

    # Test with special colorkey = -1 (use top-left pixel)
    scaled2 = DummySurface((80,90))
    monkeypatch.setattr(pygame.transform, "scale", lambda img, size: scaled2)
    out2 = utils.load_and_scale_image(str(img_file), 80, 90, colorkey=-1)
    # scaled2.set_colorkey should have been called with dummy_raw.get_at((0,0))
    assert scaled2._colorkey == (1,2,3,4)

# --- Tests for load_sound ---

def test_load_sound_no_mixer(monkeypatch):
    # mixer.get_init() False → returns None
    monkeypatch.setattr(pygame.mixer, "get_init", lambda: False)
    assert utils.load_sound("any.wav", 0.5) is None

def test_load_sound_missing_file(monkeypatch):
    monkeypatch.setattr(pygame.mixer, "get_init", lambda: True)
    monkeypatch.setattr(os.path, "exists", lambda p: False)
    assert utils.load_sound("no.wav", 0.3) is None

def test_load_sound_success(monkeypatch, tmp_path):
    monkeypatch.setattr(pygame.mixer, "get_init", lambda: True)
    path = tmp_path / "s.wav"
    path.write_bytes(b"dummy")
    dummy = DummySound(str(path))
    monkeypatch.setattr(pygame.mixer, "Sound", lambda p: dummy)

    snd = utils.load_sound(str(path), 0.75)
    assert isinstance(snd, DummySound)
    assert snd.volume == 0.75

# --- Tests for high-score file I/O ---

def test_load_high_score_missing(tmp_path):
    missing = tmp_path / "hs.txt"
    # file does not exist → 0
    assert utils.load_high_score(str(missing)) == 0

def test_load_high_score_valid(tmp_path):
    file = tmp_path / "hs.txt"
    file.write_text("123\n")
    assert utils.load_high_score(str(file)) == 123

def test_load_high_score_invalid_content(tmp_path):
    file = tmp_path / "hs.txt"
    file.write_text("abc")
    assert utils.load_high_score(str(file)) == 0

def test_save_high_score(tmp_path, capsys):
    file = tmp_path / "hs.txt"
    utils.save_high_score(str(file), 999)
    # file content
    assert file.read_text() == "999"
    # printed confirmation
    captured = capsys.readouterr()
    assert "Saved new high score 999" in captured.out

# --- Tests for load_level_data ---

def test_load_level_data_no_dir(tmp_path, capsys):
    missing = tmp_path / "levels"
    out = utils.load_level_data(str(missing))
    assert out == []
    assert "directory not found" in capsys.readouterr().out.lower()

def test_load_level_data_empty_dir(tmp_path, capsys):
    d = tmp_path / "levels"
    d.mkdir()
    out = utils.load_level_data(str(d))
    assert out == []
    assert "no .json level files found" in capsys.readouterr().out.lower()

def test_load_level_data_various(tmp_path, capsys):
    d = tmp_path / "levels"
    d.mkdir()
    # valid levels
    l1 = d / "lvl1.json"
    l1.write_text(json.dumps({"level_number": 2, "foo": "bar"}))
    l2 = d / "lvl2.json"
    l2.write_text(json.dumps({"level_number": 1}))
    # invalid JSON
    (d / "bad.json").write_text("{not valid")
    # missing level_number
    (d / "nolvl.json").write_text(json.dumps({"foo":"bar"}))

    out = utils.load_level_data(str(d))
    # Should load only the two valid ones, sorted by level_number
    assert isinstance(out, list)
    assert [lvl["level_number"] for lvl in out] == [1, 2]
    log = capsys.readouterr().out
    assert "Successfully loaded: lvl1.json" in log
    assert "Skipping file nolvl.json" in log

# End of test_utils.py
