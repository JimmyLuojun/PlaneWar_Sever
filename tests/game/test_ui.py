# test_ui.py
import pytest
import pygame
# --- FIX: Import itertools ---
import itertools
# ---------------------------
from unittest.mock import patch, MagicMock, call

# Import the module under test
from game import ui
from game import network_client # Need to mock this
from game.settings import * # Import settings constants

# --- Pytest Fixtures to Mock Pygame (Corrected in previous step) ---
# (Fixture code remains the same as the previous version)
@pytest.fixture(autouse=True)
def mock_pygame_essentials(monkeypatch):
    """Mocks essential Pygame modules and functions needed by ui.py"""
    mock_display_module = MagicMock()
    mock_screen_surf = MagicMock(spec=pygame.Surface)
    mock_screen_surf.get_rect.return_value = MagicMock(spec=pygame.Rect, center=(0,0), midleft=(0,0), midbottom=(0,0), topright=(0,0), width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
    mock_screen_surf.blit.return_value = None
    mock_screen_surf.fill.return_value = None
    mock_display_module.set_mode.return_value = mock_screen_surf
    mock_display_module.flip.return_value = None
    monkeypatch.setattr(pygame, "display", mock_display_module)

    mock_font_module = MagicMock()
    mock_font_instance = MagicMock(spec=pygame.font.Font)
    mock_font_render_surf = MagicMock(spec=pygame.Surface)
    mock_font_render_surf.get_rect.return_value = MagicMock(spec=pygame.Rect, center=(0,0), midleft=(0,0), midbottom=(0,0), topright=(0,0), size=(50,20), width=50, height=20)
    mock_font_instance.render.return_value = mock_font_render_surf
    monkeypatch.setattr(pygame.font, "Font", lambda path, size: mock_font_instance)
    monkeypatch.setattr(pygame.font, "SysFont", lambda name, size: mock_font_instance)
    mock_font_module.init.return_value = None
    mock_font_module.quit.return_value = None
    monkeypatch.setattr(pygame, "font", mock_font_module)

    mock_event_module = MagicMock()
    mock_event_module.get.return_value = []
    monkeypatch.setattr(pygame, "event", mock_event_module)

    mock_time_module = MagicMock()
    mock_clock_instance = MagicMock(spec=pygame.time.Clock)
    mock_clock_instance.tick.return_value = 16
    mock_time_module.Clock.return_value = mock_clock_instance
    mock_time_module.get_ticks.side_effect = [i * 100 for i in range(100)]
    monkeypatch.setattr(pygame, "time", mock_time_module)

    mock_draw_module = MagicMock()
    monkeypatch.setattr(pygame, "draw", mock_draw_module)

    mock_surf_class = MagicMock(spec=pygame.Surface)
    mock_surf_instance = MagicMock(spec=pygame.Surface)
    mock_surf_instance.fill.return_value = None
    mock_surf_instance.get_rect.return_value = MagicMock(spec=pygame.Rect)
    mock_surf_class.return_value = mock_surf_instance
    monkeypatch.setattr(pygame, "Surface", mock_surf_class)

    yield {
        "display": mock_display_module,
        "font": mock_font_module,
        "event": mock_event_module,
        "time": mock_time_module,
        "draw": mock_draw_module,
        "Surface": mock_surf_class,
        "screen": mock_screen_surf,
        "clock": mock_clock_instance
    }

# --- Helper to create Mock Events ---
# (Keep these as they are useful)
def create_key_event(key, unicode_char=''):
    mock_event = MagicMock()
    mock_event.type = pygame.KEYDOWN
    mock_event.key = key
    mock_event.unicode = unicode_char
    return mock_event

def create_mouse_event(pos):
    mock_event = MagicMock()
    mock_event.type = pygame.MOUSEBUTTONDOWN
    mock_event.pos = pos
    return mock_event

def create_quit_event():
    mock_event = MagicMock()
    mock_event.type = pygame.QUIT
    return mock_event

# --- Test show_login_screen ---

@patch('game.ui.network.api_login_user')
class TestLoginScreen:

    def test_show_login_screen_quit(self, mock_api_login, mock_pygame_essentials):
        mock_pygame_essentials["event"].get.return_value = [create_quit_event()]
        mock_screen = mock_pygame_essentials["screen"]
        mock_clock = mock_pygame_essentials["clock"]
        mock_fonts = {'large': MagicMock(), 'score': MagicMock()}
        action, username, msg = ui.show_login_screen(mock_screen, mock_clock, mock_fonts)
        assert action == "QUIT"
        assert username is None
        assert msg is None
        mock_api_login.assert_not_called()

    def test_show_login_screen_success_enter(self, mock_api_login, mock_pygame_essentials):
        mock_pygame_essentials["event"].get.side_effect = itertools.chain( # Use chain
            [[create_key_event(pygame.K_t, 't')]],
            [[create_key_event(pygame.K_e, 'e')]],
            [[create_key_event(pygame.K_s, 's')]],
            [[create_key_event(pygame.K_t, 't')]],
            [[create_key_event(pygame.K_TAB)]],
            [[create_key_event(pygame.K_p, 'p')]],
            [[create_key_event(pygame.K_a, 'a')]],
            [[create_key_event(pygame.K_s, 's')]],
            [[create_key_event(pygame.K_s, 's')]],
            [[create_key_event(pygame.K_RETURN)]], # Press Enter
            itertools.repeat([]) # Then infinite empty lists
        )
        mock_api_login.return_value = (True, "testuser", "Login OK")
        mock_screen = mock_pygame_essentials["screen"]
        mock_clock = mock_pygame_essentials["clock"]
        mock_fonts = {'large': MagicMock(), 'score': MagicMock()}
        action, username, msg = ui.show_login_screen(mock_screen, mock_clock, mock_fonts)
        assert action == "LOGIN_SUCCESS"
        assert username == "testuser"
        assert msg == "Login OK"
        mock_api_login.assert_called_once_with("test", "pass")

    def test_show_login_screen_success_button(self, mock_api_login, mock_pygame_essentials):
        """Test successful login via button click."""
        button_click_pos = (SCREEN_WIDTH // 2, SCREEN_HEIGHT * 0.7)
        # --- FIX: Use itertools.chain to prevent StopIteration robustly ---
        mock_pygame_essentials["event"].get.side_effect = itertools.chain(
            [[create_mouse_event(button_click_pos)]], # Click button
            itertools.repeat([]) # Yield empty lists indefinitely afterwards
        )
        # -------------------------------------------------------------
        mock_api_login.return_value = (True, "clickeduser", "Login Clicked OK")
        mock_screen = mock_pygame_essentials["screen"]
        mock_clock = mock_pygame_essentials["clock"]
        mock_fonts = {'large': MagicMock(), 'score': MagicMock()}
        action, username, msg = ui.show_login_screen(mock_screen, mock_clock, mock_fonts)
        assert action == "LOGIN_SUCCESS"
        assert username == "clickeduser"
        assert msg == "Login Clicked OK"
        mock_api_login.assert_called_once()


    def test_show_login_screen_fail_network(self, mock_api_login, mock_pygame_essentials):
        """Test failed login due to network response."""
        # --- FIX: Use itertools.chain here too ---
        mock_pygame_essentials["event"].get.side_effect = itertools.chain(
            [[create_key_event(pygame.K_RETURN)]], # Press Enter immediately
            itertools.repeat([]) # Yield empty lists indefinitely afterwards
        )
        # -----------------------------------------
        mock_api_login.return_value = (False, None, "Invalid Credentials")
        mock_screen = mock_pygame_essentials["screen"]
        mock_clock = mock_pygame_essentials["clock"]
        mock_fonts = {'large': MagicMock(), 'score': MagicMock()}
        action, username, msg = ui.show_login_screen(mock_screen, mock_clock, mock_fonts)
        assert action == "LOGIN_FAIL"
        assert username is None
        # --- FIX: Add print for debug and ensure assertion is correct ---
        print(f"DEBUG test_show_login_screen_fail_network: msg = {msg!r}")
        assert msg == "Login Failed: Invalid Credentials"
        # --------------------------------------------------------------
        mock_api_login.assert_called_once_with("", "")


# --- Test show_start_screen ---
# (No changes needed in this class)
class TestStartScreen:
    def test_show_start_screen_start_key(self, mock_pygame_essentials):
        mock_pygame_essentials["event"].get.return_value = [create_key_event(pygame.K_SPACE)]
        mock_screen = mock_pygame_essentials["screen"]
        mock_clock = mock_pygame_essentials["clock"]
        mock_fonts = {'title': MagicMock(), 'score': MagicMock()}
        result = ui.show_start_screen(mock_screen, mock_clock, mock_fonts, 0)
        assert result == "START"

    def test_show_start_screen_start_click(self, mock_pygame_essentials):
        mock_pygame_essentials["event"].get.return_value = [create_mouse_event((100, 100))]
        mock_screen = mock_pygame_essentials["screen"]
        mock_clock = mock_pygame_essentials["clock"]
        mock_fonts = {'title': MagicMock(), 'score': MagicMock()}
        result = ui.show_start_screen(mock_screen, mock_clock, mock_fonts, 0)
        assert result == "START"

    def test_show_start_screen_quit(self, mock_pygame_essentials):
        mock_pygame_essentials["event"].get.return_value = [create_quit_event()]
        mock_screen = mock_pygame_essentials["screen"]
        mock_clock = mock_pygame_essentials["clock"]
        mock_fonts = {'title': MagicMock(), 'score': MagicMock()}
        result = ui.show_start_screen(mock_screen, mock_clock, mock_fonts, 0)
        assert result == "QUIT"

# --- Test show_end_screen ---
# (No changes needed in this class)
class TestEndScreen:
    @pytest.mark.parametrize("key_event", [
        create_key_event(pygame.K_RETURN),
        create_key_event(pygame.K_r),
    ])
    def test_show_end_screen_replay(self, key_event, mock_pygame_essentials):
        mock_pygame_essentials["event"].get.return_value = [key_event]
        mock_screen = mock_pygame_essentials["screen"]
        mock_clock = mock_pygame_essentials["clock"]
        mock_fonts = {'large': MagicMock(), 'score': MagicMock(), 'small': MagicMock()}
        result = ui.show_end_screen(mock_screen, mock_clock, mock_fonts, "WIN", 100)
        assert result == "REPLAY"

    @pytest.mark.parametrize("key_event", [
        create_key_event(pygame.K_ESCAPE),
        create_key_event(pygame.K_q),
        create_quit_event(),
    ])
    def test_show_end_screen_quit(self, key_event, mock_pygame_essentials):
        mock_pygame_essentials["event"].get.return_value = [key_event]
        mock_screen = mock_pygame_essentials["screen"]
        mock_clock = mock_pygame_essentials["clock"]
        mock_fonts = {'large': MagicMock(), 'score': MagicMock(), 'small': MagicMock()}
        result = ui.show_end_screen(mock_screen, mock_clock, mock_fonts, "LOSE", 50)
        assert result == "QUIT"


# --- Test show_level_start_screen ---
# (No changes needed in this class)
class TestLevelStartScreen:
    def test_show_level_start_screen_completes(self, mock_pygame_essentials):
        mock_time_module = mock_pygame_essentials["time"]
        mock_clock_instance = mock_pygame_essentials["clock"]
        mock_time_module.get_ticks.side_effect = [0, 500, 1000, 1600]
        mock_screen = mock_pygame_essentials["screen"]
        mock_fonts = {'large': MagicMock()}
        result = ui.show_level_start_screen(mock_screen, mock_clock_instance, mock_fonts, 1)
        assert result is None

    def test_show_level_start_screen_quit_event(self, mock_pygame_essentials):
        mock_time_module = mock_pygame_essentials["time"]
        mock_clock_instance = mock_pygame_essentials["clock"]
        mock_event_module = mock_pygame_essentials["event"]
        mock_time_module.get_ticks.side_effect = [0, 500, 1000]
        mock_event_module.get.return_value = [create_quit_event()]
        mock_screen = mock_pygame_essentials["screen"]
        mock_fonts = {'large': MagicMock()}
        with pytest.raises(SystemExit):
            ui.show_level_start_screen(mock_screen, mock_clock_instance, mock_fonts, 1)