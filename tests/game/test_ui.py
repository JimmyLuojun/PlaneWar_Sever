# tests/test_ui.py
import pytest
import pygame
import os
import sys
from unittest.mock import MagicMock, patch

# --- Fixture Setup (Moved from conftest.py) ---

# Define a dummy settings module or import the real one if safe
class MockSettings:
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    FPS = 60
    # Colors
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)
    YELLOW = (255, 255, 0)
    CYAN = (0, 255, 255)
    GREY = (128, 128, 128)
    ORANGE = (255, 165, 0)
    # Font Sizes
    FONT_SIZE_LARGE = 50
    FONT_SIZE_SCORE = 30
    FONT_SIZE_TITLE = 70
    FONT_SIZE_SMALL = 24
    # Add any other constants ui.py might import via *
    # Example:
    # SERVER_API_URL = "http://mock-server/api"


# Use module-scoped autouse fixture for Pygame setup within this file
@pytest.fixture(scope="module", autouse=True)
def pygame_setup_module():
    """
    Initializes Pygame modules once for this test module.
    Uses a dummy video driver to avoid opening windows.
    """
    print("\nSetting up Pygame for test_ui.py...")
    os.environ["SDL_VIDEODRIVER"] = "dummy"
    # Initialize Pygame itself
    pygame.init()
    # Explicitly initialize display and font modules *after* setting dummy driver
    pygame.display.init()
    if not pygame.font.get_init():
        pygame.font.init()
    yield
    print("\nTearing down Pygame for test_ui.py...")
    pygame.quit()

@pytest.fixture
def mock_screen():
    """Provides a mock Pygame screen surface."""
    # We still need a surface for blitting onto, even if display mode isn't fully set
    # Ensure display is initialized before creating surface
    if not pygame.display.get_init():
         pygame.display.init()
    # Use MagicMock to allow attribute access like get_rect if needed by ui code
    screen_mock = MagicMock(spec=pygame.Surface)
    screen_mock.get_rect.return_value = pygame.Rect(0, 0, MockSettings.SCREEN_WIDTH, MockSettings.SCREEN_HEIGHT)
    screen_mock.blit.return_value = None # Mock blit to do nothing
    screen_mock.fill.return_value = None # Mock fill to do nothing
    # Add other methods if your UI code calls them on the screen surface
    return screen_mock
    # return pygame.Surface((MockSettings.SCREEN_WIDTH, MockSettings.SCREEN_HEIGHT), pygame.SRCALPHA) # Original

@pytest.fixture
def mock_clock():
    """Provides a mock Pygame clock."""
    # Use MagicMock for more control if needed, e.g., controlling tick return value
    clock_mock = MagicMock(spec=pygame.time.Clock)
    clock_mock.tick.return_value = 1000 / MockSettings.FPS # Simulate time passing per tick
    return clock_mock
    # return pygame.time.Clock() # Original

@pytest.fixture
def mock_fonts():
    """
    Provides a dictionary of mock Pygame fonts.
    Uses MagicMock to simulate font objects and render method.
    """
    if not pygame.font.get_init():
        pytest.skip("Pygame font module not initialized.")

    fonts_dict = {}
    font_sizes = {
        'large': MockSettings.FONT_SIZE_LARGE, 'score': MockSettings.FONT_SIZE_SCORE,
        'title': MockSettings.FONT_SIZE_TITLE, 'small': MockSettings.FONT_SIZE_SMALL,
        'input': MockSettings.FONT_SIZE_SCORE, 'button': MockSettings.FONT_SIZE_SCORE,
        'label': MockSettings.FONT_SIZE_SCORE, 'msg': MockSettings.FONT_SIZE_SMALL,
    }

    for name, size in font_sizes.items():
        try:
            # Create a mock font object
            mock_font = MagicMock(spec=pygame.font.Font)
            # Mock the render method to return a mock surface
            mock_surface = MagicMock(spec=pygame.Surface)
            mock_surface.get_rect.return_value = pygame.Rect(0, 0, 50, 20) # Example rect
            mock_font.render.return_value = mock_surface
            fonts_dict[name] = mock_font
        except Exception as e:
            pytest.skip(f"Skipping UI tests: Failed to create mock font '{name}' - {e}")
            return {}
    return fonts_dict


@pytest.fixture
def mock_display(mocker, mock_screen):
    """Mocks pygame.display functions to avoid 'Display mode not set' error."""
    mocker.patch('pygame.display.flip', return_value=None)
    # Make set_mode return the MagicMock screen if using that fixture
    mocker.patch('pygame.display.set_mode', return_value=mock_screen)
    mocker.patch('pygame.display.set_caption', return_value=None)
    mocker.patch('pygame.display.get_init', return_value=True)


@pytest.fixture
def mock_settings_and_network_patch(mocker):
    """
    Mocks the constants imported from game.settings into game.ui
    and also mocks the network client used by game.ui.
    """
    mock_settings_obj = MagicMock()
    for setting_name, setting_value in vars(MockSettings).items():
        if not setting_name.startswith("__"):
            setattr(mock_settings_obj, setting_name, setting_value)

    # Patch the source module 'game.settings'
    # Use autospec=True if MockSettings accurately reflects game.settings structure
    # Use create=True if the module might not be loaded when patch is applied
    mocker.patch('game.settings', mock_settings_obj, create=True)

    # Patch the network client import within game.ui
    mocker.patch('game.ui.network', autospec=True)

    return mock_settings_obj


# --- Test Helper Functions ---

# Keep post_key and post_click if other tests still use event posting
def post_key(key, unicode_char=None):
    """Posts a KEYDOWN event for the given key."""
    if unicode_char is None:
        unicode_char = chr(key) if key < 256 and chr(key).isprintable() else ''
    down_event = pygame.event.Event(pygame.KEYDOWN, key=key, unicode=unicode_char)
    pygame.event.post(down_event)

def post_click(pos):
    """Posts a MOUSEBUTTONDOWN event at the given position."""
    down_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=pos)
    pygame.event.post(down_event)

# Helper to create a QUIT event object easily
def create_quit_event():
    return pygame.event.Event(pygame.QUIT)


# --- Actual Test Code ---

# NOTE: 'from game import ui' is now MOVED inside each test function

# === Tests for show_login_screen ===

@pytest.mark.parametrize("login_success, expected_return_part", [
    (True, True),
    (False, False)
])
# Add mock_display fixture to tests calling UI functions
def test_show_login_screen_login_attempt(mocker, mock_screen, mock_clock, mock_fonts, mock_settings_and_network_patch, mock_display, login_success, expected_return_part):
    """Tests successful and failed login attempts via network mock."""
    from game import ui # Import here

    user_id = 123
    username = "testuser"
    status_msg = "Login successful" if login_success else "Invalid credentials"
    # Configure the mock network object (patched by fixture)
    ui.network.api_login_user.return_value = (login_success, user_id if login_success else None, username if login_success else None, status_msg)

    test_user = "test"
    test_pass = "pass"

    # Simulate typing by controlling event.get return values
    # This is more complex than posting, might be overkill if posting works
    # For now, stick with posting as it passed before
    pygame.event.clear()
    for char in test_user:
        post_key(ord(char), char)
    post_key(pygame.K_TAB)
    for char in test_pass:
        post_key(ord(char), char)
    post_key(pygame.K_RETURN)

    result, r_uid, r_uname, r_msg = ui.show_login_screen(mock_screen, mock_clock, mock_fonts)

    ui.network.api_login_user.assert_called_once_with(test_user, test_pass)
    assert result == expected_return_part
    if login_success:
        assert r_uid == user_id
        assert r_uname == username
    else:
        assert r_uid is None
        assert r_uname is None
    assert status_msg in r_msg

# Add mock_display fixture
def test_show_login_screen_quit(mocker, mock_screen, mock_clock, mock_fonts, mock_settings_and_network_patch, mock_display):
    """Tests quitting the login screen."""
    from game import ui # Import here

    # Mock event.get to return QUIT immediately
    mocker.patch('pygame.event.get', return_value=[create_quit_event()])

    result, r_uid, r_uname, r_msg = ui.show_login_screen(mock_screen, mock_clock, mock_fonts)

    assert result == "QUIT"
    assert r_uid is None
    assert r_uname is None
    assert r_msg is None
    ui.network.api_login_user.assert_not_called()

# === Tests for show_start_screen ===

@pytest.mark.parametrize("event_to_post", [
    pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, unicode=' '),
    pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 100))
])
# Add mock_display fixture
def test_show_start_screen_start(mocker, mock_screen, mock_clock, mock_fonts, mock_settings_and_network_patch, mock_display, event_to_post):
    """Tests starting the game from the start screen."""
    from game import ui # Import here

    # Mock event.get to return the specific start event
    mocker.patch('pygame.event.get', return_value=[event_to_post])

    result = ui.show_start_screen(mock_screen, mock_clock, mock_fonts, 0, "testuser")
    assert result == "START"

# Add mock_display fixture
def test_show_start_screen_quit(mocker, mock_screen, mock_clock, mock_fonts, mock_settings_and_network_patch, mock_display):
    """Tests quitting from the start screen."""
    from game import ui # Import here

    # Mock event.get to return QUIT
    mocker.patch('pygame.event.get', return_value=[create_quit_event()])

    result = ui.show_start_screen(mock_screen, mock_clock, mock_fonts, 0, "testuser")
    assert result == "QUIT"

# === Tests for show_end_screen ===

@pytest.mark.parametrize("key, expected_result", [
    (pygame.K_RETURN, "REPLAY"),
    (pygame.K_r, "REPLAY"),
    (pygame.K_ESCAPE, "QUIT"),
    (pygame.K_q, "QUIT"),
])
# Add mock_display fixture
def test_show_end_screen_key_input(mocker, mock_screen, mock_clock, mock_fonts, mock_settings_and_network_patch, mock_display, key, expected_result):
    """Tests replay/quit via keyboard input on the end screen."""
    from game import ui # Import here

    # Mock event.get to return the specific key event
    key_event = pygame.event.Event(pygame.KEYDOWN, key=key, unicode=chr(key) if key < 256 else '')
    mocker.patch('pygame.event.get', return_value=[key_event])

    result = ui.show_end_screen(mock_screen, mock_clock, mock_fonts, "LOSE", 100, "Score submitted successfully.")
    assert result == expected_result

# Add mock_display fixture
def test_show_end_screen_quit_event(mocker, mock_screen, mock_clock, mock_fonts, mock_settings_and_network_patch, mock_display):
    """Tests quitting via QUIT event on the end screen."""
    from game import ui # Import here

    # Mock event.get to return QUIT
    mocker.patch('pygame.event.get', return_value=[create_quit_event()])

    result = ui.show_end_screen(mock_screen, mock_clock, mock_fonts, "WIN", 500)
    assert result == "QUIT"

# === Tests for show_level_start_screen ===

# Add mock_display fixture
def test_show_level_start_screen_runs(mocker, mock_screen, mock_clock, mock_fonts, mock_settings_and_network_patch, mock_display):
    """Tests that the level start screen runs without crashing."""
    from game import ui # Import here

    mock_exit = mocker.patch('sys.exit')
    # Mock get_ticks to ensure the loop finishes
    mocker.patch('pygame.time.get_ticks', side_effect=[1000, 2600]) # Start time, End time (>1500ms later)
    # Mock event.get to return nothing
    mocker.patch('pygame.event.get', return_value=[])

    try:
        ui.show_level_start_screen(mock_screen, mock_clock, mock_fonts, 1)
    except Exception as e:
        pytest.fail(f"show_level_start_screen raised an exception: {e}")

    mock_exit.assert_not_called()

# Add mock_display fixture
def test_show_level_start_screen_handles_quit(mocker, mock_screen, mock_clock, mock_fonts, mock_display):
    """Tests that the level start screen raises SystemExit on QUIT event."""
    from game import ui  # Import here

    # Mock sys.exit is not strictly needed since we catch SystemExit,
    # but mocking pygame.quit is important to verify it's *not* called by ui.
    mock_pygame_quit = mocker.patch('pygame.quit')

    # Mock get_ticks to control the loop timing
    mocker.patch('pygame.time.get_ticks', side_effect=[
        1000,  # Initial call for start_ticks
        1100,  # First loop iteration time check (1100-1000 < 1500)
        1200,  # Second loop iteration time check (1200-1000 < 1500)
        2600   # Failsafe tick value if loop continues
    ])

    # Mock pygame.event.get to return an empty list, then the QUIT event
    mock_event_get = mocker.patch('pygame.event.get', side_effect=[
        [],  # First call inside the loop yields no events
        [create_quit_event()],  # Second call yields the QUIT event
        []  # Subsequent calls (shouldn't be needed if exit works)
    ])

    # Expect SystemExit to be raised directly by the function
    with pytest.raises(SystemExit):
        ui.show_level_start_screen(mock_screen, mock_clock, mock_fonts, 1)

    # Verify pygame.quit was NOT called during the test, as ui should just raise
    mock_pygame_quit.assert_not_called()
    # Verify the event loop was checked
    assert mock_event_get.call_count >= 2


