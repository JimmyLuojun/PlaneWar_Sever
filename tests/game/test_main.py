# tests/game/test_main.py
import pytest
import pygame
import sys
import os
from unittest.mock import MagicMock, patch, call

# --- Absolute Imports from game package (assuming main.py uses these now) ---
# If main.py still uses relative imports, this test file might still work,
# but ensure main.py uses the absolute imports as recommended previously.
from game import main
from game.player import Player
from game.enemy import Enemy, EnemyBoss
from game.powerup import PowerUp
from game.background import Background
from game.settings import *

# Assume conftest.py provides:
# mock_sounds, mock_surface, mock_powerup_images, mock_all_images, mock_groups,
# pygame_setup, mock_pygame_display (maybe needs enhancement),
# mock_pygame_font (dictionary - might not be used directly if constructors are patched),
# mock_pygame_time, mock_pygame_input

# --- Constants for Tests ---
DEFAULT_LEVEL_DATA = {
    'level_number': 1, 'is_boss_level': False, 'enemy_types': ['enemy1'],
    'spawn_interval': 60, 'max_on_screen': 5, 'enemy_speed_y_range': (1, 3),
    'enemy_speed_x_range': (-1, 1), 'powerup_interval': 10000,
    'boss_appear_delay_seconds': 5, 'music': 'level1_music.ogg'
}
BOSS_LEVEL_DATA = {
    'level_number': 2, 'is_boss_level': True, 'enemy_types': [],
    'spawn_interval': 60, 'max_on_screen': 0, 'enemy_speed_y_range': (1, 1),
    'enemy_speed_x_range': (0, 0), 'powerup_interval': 15000,
    'boss_appear_delay_seconds': 0.1, 'music': 'boss_music.ogg'
}
MOCK_LEVELS_DATA = [DEFAULT_LEVEL_DATA, BOSS_LEVEL_DATA]

# --- Test Fixtures Specific to main.py ---

@pytest.fixture
def mock_background(mocker):
    mock_bg_instance = MagicMock(spec=Background)
    mock_bg_instance.update = MagicMock()
    mock_bg_instance.draw = MagicMock()
    mocker.patch('game.main.Background', return_value=mock_bg_instance)
    return mock_bg_instance

@pytest.fixture
def mock_player_instance(mocker, mock_surface, mock_sounds):
    mock_player = MagicMock(spec=Player)
    mock_player.score = 0
    mock_player.bomb_count = PLAYER_STARTING_BOMBS
    mock_player.shield_active = False
    mock_player.alive.return_value = True
    mock_player.kill = MagicMock()
    mock_player.shoot.return_value = None
    mock_player.use_bomb.return_value = 0
    mock_player.activate_powerup = MagicMock()
    mock_player.draw_shield = MagicMock()
    mock_player.rect = mock_surface.get_rect()
    mocker.patch('game.main.Player', return_value=mock_player)
    return mock_player

@pytest.fixture
def mock_enemy_boss_instance(mocker, mock_sounds):
    mock_boss = MagicMock(spec=EnemyBoss)
    mock_boss.health = 100
    mock_boss.kill = MagicMock()
    mock_boss.draw_health_bar = MagicMock()
    mock_boss.update = MagicMock()
    mocker.patch('game.main.EnemyBoss', return_value=mock_boss)
    return mock_boss

@pytest.fixture
def mock_pygame_font_constructors(mocker):
    """Mocks pygame.font.Font and pygame.font.SysFont constructors."""
    mock_font_instance = MagicMock(spec=pygame.font.Font)
    mock_surface = MagicMock(spec=pygame.Surface)
    mock_rect = MagicMock(spec=pygame.Rect)
    mock_surface.get_rect.return_value = mock_rect
    mock_font_instance.render.return_value = mock_surface
    mock_font_constructor = mocker.patch('pygame.font.Font', return_value=mock_font_instance)
    mock_sysfont_constructor = mocker.patch('pygame.font.SysFont', return_value=mock_font_instance)
    return {'Font': mock_font_constructor, 'SysFont': mock_sysfont_constructor}

# --- Tests for run_game Function ---

def test_run_game_initialization_and_quit(
    mocker, mock_pygame_time, mock_all_images, mock_sounds,
    mock_background, mock_player_instance, mock_pygame_font_constructors
):
    """Test basic setup of run_game and immediate quit via pygame event."""
    # Arrange
    mock_screen = MagicMock(spec=pygame.Surface)
    mock_clock = mock_pygame_time
    fonts = {'score': mock_pygame_font_constructors['SysFont']('dummy', 10)}
    images = mock_all_images
    sounds = mock_sounds
    level_data = DEFAULT_LEVEL_DATA
    background = mock_background
    player = mock_player_instance

    mock_event_quit = pygame.event.Event(pygame.QUIT)
    mocker.patch('pygame.event.get', return_value=[mock_event_quit])
    mock_add_to_group = mocker.patch('pygame.sprite.Group.add')
    mocker.patch('pygame.display.flip')

    # Act
    result, score, level_num = main.run_game(
        mock_screen, mock_clock, fonts, images, sounds, level_data, background
    )

    # Assert
    assert result == 'QUIT'
    assert score == player.score
    assert level_num == level_data['level_number']
    mock_add_to_group.assert_any_call(player)
    background.update.assert_not_called()
    background.draw.assert_not_called()
    mock_clock.tick.assert_called_once_with(FPS)

# VV --- THIS IS THE FAILING TEST --- VV
def test_run_game_player_dies_by_enemy(
    mocker, mock_pygame_time, mock_all_images, mock_sounds,
    mock_background, mock_player_instance, mock_pygame_font_constructors
):
    """Test the game ending when the player collides with an enemy."""
    # Arrange
    mock_screen = MagicMock(spec=pygame.Surface)
    mock_clock = mock_pygame_time
    fonts = {'score': mock_pygame_font_constructors['SysFont']('dummy', 10)} # Dummy dict
    images = mock_all_images
    sounds = mock_sounds
    level_data = DEFAULT_LEVEL_DATA
    background = mock_background
    player = mock_player_instance

    mocker.patch('pygame.display.flip')

    start_time = 1000
    # Provide *more* return values for get_ticks side_effect
    mocker.patch('pygame.time.get_ticks', side_effect=[
        start_time,                              # powerup_last_spawn_time init
        start_time + 10,                         # level_start_time init
        start_time + STARTUP_GRACE_PERIOD + 100, # 'now' in loop 1 (collision check time)
        start_time + STARTUP_GRACE_PERIOD + 200, # 'now' in loop 2 (before quit event)
        start_time + STARTUP_GRACE_PERIOD + 300, # Extra value if needed
        start_time + STARTUP_GRACE_PERIOD + 400  # Extra value if needed
    ])
    mock_event_quit = pygame.event.Event(pygame.QUIT)
    # This event sequence simulates: Loop 1 -> [], Loop 2 -> [QUIT]
    mocker.patch('pygame.event.get', side_effect=[[], [mock_event_quit]])

    # This spritecollide sequence simulates for Loop 1:
    # 1. powerup_hits -> []
    # 2. player_enemy_hits (in death check) -> [mock_enemy] -> Triggers Death
    mock_enemy = MagicMock(spec=Enemy)
    mocker.patch('pygame.sprite.spritecollide', side_effect=[
        [],             # powerup_hits
        [mock_enemy],   # player_enemy_hits -> Simulate Hit!
        [],             # player_boss_collision (should be skipped)
        []              # enemy_bullet_hits (should be skipped)
    ])
    player.shield_active = False
    player.alive.return_value = True

    # Act
    result, score, level_num = main.run_game(
        mock_screen, mock_clock, fonts, images, sounds, level_data, background
    )

    # Assert
    assert result == 'FAILED'
    assert score == player.score
    assert level_num == level_data['level_number']
    player.kill.assert_called_once()
    sounds['player_lose'].play.assert_called_once()
# ^^ --- END OF FAILING TEST MODIFICATION --- ^^


def test_run_game_boss_defeated(
    mocker, mock_pygame_time, mock_all_images, mock_sounds,
    mock_background, mock_player_instance, mock_enemy_boss_instance, mock_pygame_font_constructors
):
    """Test the level ending successfully when the boss is defeated."""
    # Arrange
    mock_screen = MagicMock(spec=pygame.Surface)
    mock_clock = mock_pygame_time
    fonts = {'score': mock_pygame_font_constructors['SysFont']('dummy', 10)}
    images = mock_all_images
    sounds = mock_sounds
    level_data = BOSS_LEVEL_DATA
    background = mock_background
    player = mock_player_instance
    boss = mock_enemy_boss_instance
    boss.health = 1

    mocker.patch('pygame.display.flip')

    start_time = 1000
    boss_appear_time = start_time + (level_data['boss_appear_delay_seconds'] * 1000) + 10
    collision_check_time = boss_appear_time + 100
    # Provide enough ticks for boss spawn and collision checks
    mocker.patch('pygame.time.get_ticks', side_effect=[
        start_time,                     # powerup_last_spawn_time init
        start_time + 10,                # level_start_time init
        boss_appear_time,               # now (triggers boss spawn)
        collision_check_time,           # now (boss active, collision check happens)
        collision_check_time + 100,     # now (loop after boss defeat)
        collision_check_time + 200      # Extra
    ])
    mock_event_quit = pygame.event.Event(pygame.QUIT)
    # Spawn -> Collision -> Quit
    mocker.patch('pygame.event.get', side_effect=[[], [], [mock_event_quit]])

    mock_bullet = MagicMock(spec=pygame.Surface)
    mocker.patch('pygame.sprite.groupcollide', return_value={})
    # Collision sequence: bullets_hitting_boss, powerup_hits
    mocker.patch('pygame.sprite.spritecollide', side_effect=[ [mock_bullet], [] ])

    # Act
    result, score, level_num = main.run_game(
        mock_screen, mock_clock, fonts, images, sounds, level_data, background
    )

    # Assert
    assert result == 'PASSED'
    assert player.score == 50
    assert level_num == level_data['level_number']
    boss.kill.assert_called_once()
    sounds['boss_explode'].play.assert_called_once()
    sounds['game_win'].play.assert_called_once()


# --- Mock setup fixtures for the main() function tests ---

@pytest.fixture(autouse=True)
def mock_pygame_init_quit(mocker):
    """Mock pygame.init and pygame.quit for all main() tests."""
    mocker.patch('pygame.init', return_value=(6, 0))
    quit_mock = mocker.patch('pygame.quit')
    mocker.patch('pygame.mixer.init', return_value=None)
    mocker.patch('pygame.mixer.get_init', return_value=True)
    mocker.patch('pygame.mixer.quit')
    mocker.patch('pygame.mixer.music', MagicMock())
    return quit_mock

@pytest.fixture
def mock_utils(mocker):
    """Mock all functions from the game.main.utils module."""
    mock = MagicMock()
    mock_img_surface = MagicMock(spec=pygame.Surface)
    mock_img_surface.get_rect.return_value = MagicMock(spec=pygame.Rect)
    mock.load_and_scale_image = MagicMock(return_value=mock_img_surface)
    mock.load_sound = MagicMock(return_value=MagicMock(spec=pygame.mixer.Sound))
    mock.load_level_data = MagicMock(return_value=MOCK_LEVELS_DATA)
    mock.load_high_score = MagicMock(return_value=100)
    mock.save_high_score = MagicMock()
    mocker.patch('game.main.utils', mock)
    return mock

@pytest.fixture
def mock_ui(mocker):
    """Mock all functions from the game.main.ui module."""
    mock = MagicMock()
    mock.show_login_screen = MagicMock(return_value=('QUIT', None, None, 'User quit'))
    mock.show_start_screen = MagicMock()
    mock.show_level_start_screen = MagicMock()
    mock.show_end_screen = MagicMock(return_value='QUIT')
    mocker.patch('game.main.ui', mock)
    return mock

@pytest.fixture
def mock_network(mocker):
    """Mock game.main.network (network_client) functions."""
    mock = MagicMock()
    mock.api_login_user = MagicMock(return_value=(False, None, None, 'Network Error'))
    mock.api_submit_score = MagicMock(return_value=(False, 'Submission Failed'))
    mocker.patch('game.main.network', mock)
    return mock

@pytest.fixture
def mock_run_game(mocker):
    """Mock the main.run_game function itself."""
    mock = mocker.patch('game.main.run_game', return_value=('QUIT', 0, 1))
    return mock

@pytest.fixture
def mock_os_path(mocker):
    """Mock os.path functions used in main."""
    mocker.patch('os.path.exists', return_value=True)
    mocker.patch('os.path.join', side_effect=lambda *args: "/".join(args))
    mocker.patch('os.path.dirname', return_value='/fake/game/dir')
    mocker.patch('os.path.basename', side_effect=lambda p: p.split('/')[-1])


# --- Tests for main() Function Logic ---

def test_main_initialization_and_immediate_quit(
    mocker, mock_pygame_init_quit, mock_pygame_display, mock_pygame_time,
    mock_pygame_font_constructors, # Use font constructor mock
    mock_utils, mock_ui, mock_network, mock_os_path, mock_background
):
    """Test if main initializes pygame, loads assets (mocked), shows login, and quits."""
    # Arrange
    mocker.patch('sys.exit')
    quit_mock = mock_pygame_init_quit # Get the mock for pygame.quit

    # Act
    main.main()

    # Assert
    pygame.init.assert_called_once()
    mock_utils.load_level_data.assert_called_once()
    mock_utils.load_high_score.assert_called_once()
    mock_ui.show_login_screen.assert_called_once()
    quit_mock.assert_called_once() # Use the returned mock from fixture
    sys.exit.assert_called_once()


def test_main_login_fail_stays_on_login(
    mocker, mock_pygame_init_quit, mock_pygame_display, mock_pygame_time,
    mock_pygame_font_constructors, # Use font constructor mock
    mock_utils, mock_ui, mock_network, mock_os_path, mock_background
):
    """Test if failing login keeps the state as LOGIN_SCREEN and tries again."""
    # Arrange
    mock_ui.show_login_screen.side_effect = [
        (False, None, None, 'Incorrect Password'),
        ('QUIT', None, None, 'User quit')
    ]
    mocker.patch('sys.exit')
    quit_mock = mock_pygame_init_quit

    # Act
    main.main()

    # Assert
    assert mock_ui.show_login_screen.call_count == 2
    mock_ui.show_start_screen.assert_not_called()
    quit_mock.assert_called_once()


def test_main_login_success_starts_game_and_runs_level(
    mocker, mock_pygame_init_quit, mock_pygame_display, mock_pygame_time,
    mock_pygame_font_constructors, # Use font constructor mock
    mock_utils, mock_ui, mock_network, mock_os_path, mock_background, mock_run_game
):
    """Test successful login transitions to start screen, level start, and calls run_game."""
    # Arrange
    mock_ui.show_login_screen.return_value = (True, 123, 'testUser', 'Login OK')
    mock_run_game.return_value = ('QUIT', 50, 1)
    mocker.patch('sys.exit')
    quit_mock = mock_pygame_init_quit

    # Act
    main.main()

    # Assert
    mock_ui.show_login_screen.assert_called_once()
    mock_ui.show_start_screen.assert_called_once()
    mock_ui.show_level_start_screen.assert_called_once_with(
        mocker.ANY, mocker.ANY, mocker.ANY, MOCK_LEVELS_DATA[0]['level_number']
    )
    mock_run_game.assert_called_once_with(
        mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY, mocker.ANY,
        MOCK_LEVELS_DATA[0], mocker.ANY
    )
    quit_mock.assert_called_once()
    sys.exit.assert_called_once()


def test_main_level_passed_proceeds_to_next_level(
    mocker, mock_pygame_init_quit, mock_pygame_display, mock_pygame_time,
    mock_pygame_font_constructors, # Use font constructor mock
    mock_utils, mock_ui, mock_network, mock_os_path, mock_background, mock_run_game
):
    """Test passing level 1 transitions to level 2 start screen."""
    # Arrange
    mock_ui.show_login_screen.return_value = (True, 123, 'testUser', 'Login OK')
    mock_run_game.side_effect = [ ('PASSED', 100, 1), ('QUIT', 150, 2) ]
    mocker.patch('sys.exit')
    quit_mock = mock_pygame_init_quit

    # Act
    main.main()

    # Assert
    assert mock_ui.show_level_start_screen.call_count == 2
    mock_ui.show_level_start_screen.assert_called_with(
        mocker.ANY, mocker.ANY, mocker.ANY, MOCK_LEVELS_DATA[1]['level_number']
    )
    assert mock_run_game.call_count == 2
    assert mock_run_game.call_args_list[1][0][5] == MOCK_LEVELS_DATA[1]
    quit_mock.assert_called_once()


def test_main_game_failed_shows_end_screen_and_submits_score(
    mocker, mock_pygame_init_quit, mock_pygame_display, mock_pygame_time,
    mock_pygame_font_constructors, # Use font constructor mock
    mock_utils, mock_ui, mock_network, mock_os_path, mock_background, mock_run_game
):
    """Test failing a level transitions to the end screen and submits score if logged in."""
    # Arrange
    login_user_id, login_username = 123, 'testUser'
    final_score, level_failed = 75, 1
    mock_ui.show_login_screen.return_value = (True, login_user_id, login_username, 'Login OK')
    mock_run_game.return_value = ('FAILED', final_score, level_failed)
    mock_ui.show_end_screen.return_value = 'QUIT'
    mock_network.api_submit_score.return_value = (True, "Score submitted OK")
    mocker.patch('sys.exit')
    quit_mock = mock_pygame_init_quit

    # Act
    main.main()

    # Assert
    mock_run_game.assert_called_once()
    mock_network.api_submit_score.assert_called_once_with(login_user_id, final_score, level_failed)
    mock_ui.show_end_screen.assert_called_once_with(
        mocker.ANY, mocker.ANY, mocker.ANY, 'LOSE', final_score, "Score submitted OK"
    )
    quit_mock.assert_called_once()


def test_main_game_won_shows_end_screen(
    mocker, mock_pygame_init_quit, mock_pygame_display, mock_pygame_time,
    mock_pygame_font_constructors, # Use font constructor mock
    mock_utils, mock_ui, mock_network, mock_os_path, mock_background, mock_run_game
):
    """Test winning the last level transitions to the WIN end screen."""
    # Arrange
    login_user_id, login_username = 456, 'winner'
    final_score = 250
    last_level = MOCK_LEVELS_DATA[-1]['level_number']
    mock_ui.show_login_screen.return_value = (True, login_user_id, login_username, 'Login OK')
    mock_run_game.side_effect = [ ('PASSED', 100, 1), ('PASSED', final_score, last_level) ]
    mock_ui.show_end_screen.return_value = 'QUIT'
    mock_network.api_submit_score.return_value = (True, "Win Score Submitted!")
    mocker.patch('sys.exit')
    quit_mock = mock_pygame_init_quit

    # Act
    main.main()

    # Assert
    assert mock_run_game.call_count == len(MOCK_LEVELS_DATA)
    mock_network.api_submit_score.assert_called_once_with(login_user_id, final_score, last_level)
    mock_ui.show_end_screen.assert_called_once_with(
        mocker.ANY, mocker.ANY, mocker.ANY, 'WIN', final_score, "Win Score Submitted!"
    )
    quit_mock.assert_called_once()


def test_main_local_high_score_save_when_not_logged_in(
    mocker, mock_pygame_init_quit, mock_pygame_display, mock_pygame_time,
    mock_pygame_font_constructors, # Use font constructor mock
    mock_utils, mock_ui, mock_network, mock_os_path, mock_background, mock_run_game
):
    """Test saving high score locally using utils when user is not logged in (no user ID)."""
    # Arrange
    mock_ui.show_login_screen.return_value = (True, None, None, 'Logged in anonymously')
    current_high_score, new_high_score = 50, 150
    mock_utils.load_high_score.return_value = current_high_score
    mock_run_game.return_value = ('FAILED', new_high_score, 1)
    mock_ui.show_end_screen.return_value = 'QUIT'
    mocker.patch('sys.exit')
    quit_mock = mock_pygame_init_quit

    # Act
    main.main()

    # Assert
    mock_run_game.assert_called_once()
    mock_network.api_submit_score.assert_not_called()
    mock_utils.save_high_score.assert_called_once_with( mocker.ANY, new_high_score )
    mock_ui.show_end_screen.assert_called_once_with(
        mocker.ANY, mocker.ANY, mocker.ANY, 'LOSE', new_high_score,
        "Not logged in. Score saved locally (if new high)."
    )
    quit_mock.assert_called_once()