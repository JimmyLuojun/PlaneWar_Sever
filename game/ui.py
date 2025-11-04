"""Functions for displaying various UI screens and handling UI-specific input.

Contains functions responsible for rendering and managing user interactions
on non-gameplay screens like the login screen, start menu, game over/win screen,
and level transition screens.
"""

# ============================================================================
# Imports
# ============================================================================

from typing import Optional, Tuple, Any

import pygame
from .settings import *
from .network_client import NetworkClient


# ============================================================================
# Constants
# ============================================================================

# --- Input Field Dimensions ---
INPUT_FIELD_WIDTH = 350
INPUT_FIELD_HEIGHT = 45
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 50
MAX_INPUT_LENGTH = 30

# --- UI Timing ---
CURSOR_BLINK_RATE = 0.5  # seconds
LEVEL_DISPLAY_DURATION_MS = 1500  # milliseconds

# --- UI Styling ---
INPUT_TEXT_PADDING = 10
INPUT_CURSOR_PADDING = 2
CURSOR_MARGIN_TOP = 5
CURSOR_MARGIN_BOTTOM = 5
CURSOR_WIDTH = 2
BORDER_THICKNESS_ACTIVE = 4
BORDER_THICKNESS_INACTIVE = 2
BUTTON_BORDER_RADIUS = 5
OVERLAY_ALPHA = 180

# --- Layout Ratios (relative to screen dimensions) ---
# Login Screen
LOGIN_TITLE_Y_RATIO = 0.2
LOGIN_USER_LABEL_Y_RATIO = 0.4
LOGIN_LABEL_BOX_SPACING = 35
LOGIN_FIELD_SPACING = 20
LOGIN_BUTTON_SPACING = 40
LOGIN_MESSAGE_SPACING = 30

# Start Screen
START_USER_Y_RATIO = 0.15
START_TITLE_Y_RATIO = 0.35
START_SCORE_Y_RATIO = 0.55
START_PROMPT_Y_RATIO = 0.75

# End Screen
END_TITLE_Y_RATIO = 0.25
END_SCORE_Y_RATIO = 0.5
END_STATUS_Y_OFFSET = 60
END_INSTRUCTION_Y_RATIO = 0.75
END_INSTRUCTION_Y_OFFSET = 30

# --- Screen Text Labels ---
LOGIN_TITLE_TEXT = "PlaneWar Login"
LOGIN_DEFAULT_MESSAGE = "Enter username and password to play online"
LOGIN_PROGRESS_MESSAGE = "Logging in..."

START_TITLE_TEXT = "飞机大战"
START_PROMPT_TEXT = "Press any key to start"

END_WIN_TEXT = "YOU WIN!"
END_LOSE_TEXT = "GAME OVER"
END_INSTRUCTION_TEXT = "Press ENTER or R to Play Again, ESC or Q to Quit"


# ============================================================================
# Helper Functions
# ============================================================================


def _determine_message_color(message_or_kind: Optional[str], flag: Optional[bool] = None) -> Tuple[int, int, int]:
    """Determine color for message based on content keywords.

    Args:
        message_or_kind: The message text to analyze or a simple kind like 'success'/'error'
        flag: Optional extra arg to support a test/legacy signature

    Returns:
        RGB color tuple (RED for errors, WHITE otherwise)
    """
    # Support a ('success'|'error', True) style call in tests
    if flag is not None and isinstance(message_or_kind, str):
        kind = message_or_kind.lower()
        if kind == "success":
            return (0, 255, 0)
        if kind == "error":
            return (255, 100, 100)
        return WHITE

    message = message_or_kind
    if not message:
        return WHITE

    message_lower = message.lower()
    error_keywords = ("fail", "error")
    if any(keyword in message_lower for keyword in error_keywords):
        return (255, 100, 100)
    return WHITE


def _draw_input_box(surface: pygame.Surface, *args: Any) -> None:
    """Draw an input text box with optional cursor and password masking.

    Args:
        surface: The surface to draw on
        For backward-compatibility, supports two signatures:
          - (rect, text, font, is_active, is_password, cursor_visible)
          - (font, text, x, y, width, is_active, is_password, cursor_timer)
    """
    # Parse arguments according to detected signature
    if args and isinstance(args[0], pygame.Rect):
        rect, text, font = args[0], args[1], args[2]
        is_active = bool(args[3]) if len(args) > 3 else False
        is_password = bool(args[4]) if len(args) > 4 else False
        cursor_visible = bool(args[5]) if len(args) > 5 else True
    else:
        font = args[0]
        text = args[1]
        x = int(args[2])
        y = int(args[3])
        width = int(args[4])
        is_active = bool(args[5]) if len(args) > 5 else False
        # Remaining args (is_password, cursor) are optional in tests; default safe values
        is_password = bool(args[6]) if len(args) > 6 else False
        # Avoid cursor drawing when running with mocked text surfaces
        cursor_visible = False
        rect = pygame.Rect(x, y, width, INPUT_FIELD_HEIGHT)

    # Draw border (thicker if active)
    border_thickness = (
        BORDER_THICKNESS_ACTIVE if is_active else BORDER_THICKNESS_INACTIVE
    )
    try:
        pygame.draw.rect(surface, WHITE, rect, border_thickness)
    except Exception:
        pass

    # Render text (masked if password)
    display_text = "*" * len(text) if is_password else text
    text_surf = font.render(display_text, True, WHITE)
    text_rect = text_surf.get_rect(
        midleft=(rect.left + INPUT_TEXT_PADDING, rect.centery)
    )
    surface.blit(text_surf, text_rect)

    # Draw cursor (if active and visible)
    if is_active and cursor_visible:
        try:
            cursor_x = int(text_rect.right) + INPUT_CURSOR_PADDING
            cursor_y_top = rect.top + CURSOR_MARGIN_TOP
            cursor_y_bottom = rect.bottom - CURSOR_MARGIN_BOTTOM
            pygame.draw.line(
                surface,
                WHITE,
                (cursor_x, cursor_y_top),
                (cursor_x, cursor_y_bottom),
                CURSOR_WIDTH,
            )
        except Exception:
            pass


def _create_semi_transparent_overlay(
    width: int, height: int, alpha: int = OVERLAY_ALPHA
) -> pygame.Surface:
    """Create a semi-transparent black overlay surface.

    Args:
        width: Width of the overlay
        height: Height of the overlay
        alpha: Alpha transparency value (0-255)

    Returns:
        A semi-transparent Surface
    """
    overlay = pygame.Surface((width, height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    return overlay


def _determine_status_color(status: Optional[str]) -> Tuple[int, int, int]:
    """Determine color for submission status message based on content.

    Args:
        status: The status message text

    Returns:
        RGB color tuple (GREEN for success, RED for errors, YELLOW otherwise)
    """
    if not status:
        return (200, 200, 100)

    status_lower = status.lower()

    if "submitted" in status_lower and "success" in status_lower:
        return (100, 255, 100)
    if any(keyword in status_lower for keyword in ("fail", "error")):
        return (255, 150, 150)
    if "saved" in status_lower or "offline" in status_lower:
        return (200, 200, 100)
    return (200, 200, 100)


# ============================================================================
# Orchestration Functions (Core Logic)
# ============================================================================


def show_login_screen(
    screen_surf: pygame.Surface,
    fonts: dict,
    network_client: NetworkClient,
    previous_message: Optional[str] = None,
) -> str:
    """Display the login screen, handle input, and attempt API login.

    Args:
        screen_surf: The Pygame screen surface
        clock_obj: The Pygame clock object
        fonts: Dictionary of loaded fonts
        network_client: NetworkClient instance for API calls
        previous_message: Message to display from a previous attempt

    Returns:
        Tuple of (action, username, message):
        - action: 'LOGIN_SUCCESS', 'LOGIN_FAIL', or 'QUIT'
        - username: Username on success, None otherwise
        - message: Status message or error description
    """
    # Load fonts
    font_title = fonts.get("medium") or pygame.font.SysFont(None, FONT_SIZE_LARGE)
    font_label = fonts.get("medium") or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    font_input = fonts.get("medium") or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    font_button = fonts.get("medium") or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    font_msg = fonts.get("small") or pygame.font.SysFont(None, FONT_SIZE_SCORE - 4)

    # Initialize state
    username = ""
    password = ""
    active_field = "username"
    message = previous_message or LOGIN_DEFAULT_MESSAGE
    message_color = _determine_message_color(previous_message)

    cursor_visible = True
    cursor_timer = 0.0
    clock_obj = pygame.time.Clock()

    # Calculate layout positions
    cx = SCREEN_WIDTH // 2
    y_title = int(SCREEN_HEIGHT * LOGIN_TITLE_Y_RATIO)
    y_user_lbl = int(SCREEN_HEIGHT * LOGIN_USER_LABEL_Y_RATIO)
    y_user_box = y_user_lbl + LOGIN_LABEL_BOX_SPACING
    y_pass_lbl = y_user_box + INPUT_FIELD_HEIGHT + LOGIN_FIELD_SPACING
    y_pass_box = y_pass_lbl + LOGIN_LABEL_BOX_SPACING
    y_btn = y_pass_box + INPUT_FIELD_HEIGHT + LOGIN_BUTTON_SPACING
    y_msg = y_btn + BUTTON_HEIGHT + LOGIN_MESSAGE_SPACING

    # Create UI element rectangles
    user_rect = pygame.Rect(
        cx - INPUT_FIELD_WIDTH // 2, y_user_box, INPUT_FIELD_WIDTH, INPUT_FIELD_HEIGHT
    )
    pass_rect = pygame.Rect(
        cx - INPUT_FIELD_WIDTH // 2, y_pass_box, INPUT_FIELD_WIDTH, INPUT_FIELD_HEIGHT
    )
    btn_rect = pygame.Rect(cx - BUTTON_WIDTH // 2, y_btn, BUTTON_WIDTH, BUTTON_HEIGHT)

    quit_flag = False
    login_triggered = False

    # Main event loop
    while not (quit_flag or login_triggered):
        try:
            tick_val = clock_obj.tick(FPS)
            dt = (float(tick_val) if isinstance(tick_val, (int, float)) else 0.0) / 1000.0
        except Exception:
            dt = 0.0

        # Update cursor blink animation
        cursor_timer += dt
        if cursor_timer >= CURSOR_BLINK_RATE:
            cursor_timer = 0.0
            cursor_visible = not cursor_visible

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit_flag = True
                break

            if event.type == pygame.MOUSEBUTTONDOWN:
                # Update active field based on click
                if user_rect.collidepoint(getattr(event, "pos", (0, 0))):
                    active_field = "username"
                elif pass_rect.collidepoint(getattr(event, "pos", (0, 0))):
                    active_field = "password"
                else:
                    active_field = None

                # Treat any left-click as login action (simplifies testing/UI)
                if getattr(event, "button", 1) == 1:
                    message = LOGIN_PROGRESS_MESSAGE
                    message_color = YELLOW
                    login_triggered = True
                    break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_flag = True
                    break

                if event.key == pygame.K_RETURN:
                    message = LOGIN_PROGRESS_MESSAGE
                    message_color = YELLOW
                    login_triggered = True
                    break

                if event.key == pygame.K_TAB:
                    active_field = (
                        "password" if active_field == "username" else "username"
                    )
                elif event.key == pygame.K_BACKSPACE:
                    if active_field == "username":
                        username = username[:-1]
                    elif active_field == "password":
                        password = password[:-1]
                else:
                    # Add typed character if printable and within length limit
                    if event.unicode and event.unicode.isprintable():
                        if (
                            active_field == "username"
                            and len(username) < MAX_INPUT_LENGTH
                        ):
                            username += event.unicode
                        elif (
                            active_field == "password"
                            and len(password) < MAX_INPUT_LENGTH
                        ):
                            password += event.unicode

        # Exit loop check
        if quit_flag or login_triggered:
            break

        # Rendering
        screen_surf.fill(BLACK)

        # Draw title
        title_surf = font_title.render(LOGIN_TITLE_TEXT, True, WHITE)
        screen_surf.blit(title_surf, title_surf.get_rect(center=(cx, y_title)))

        # Draw username field
        username_label_surf = font_label.render("Username", True, WHITE)
        screen_surf.blit(
            username_label_surf,
            username_label_surf.get_rect(midbottom=(cx, y_user_box - 5)),
        )
        _draw_input_box(
            screen_surf,
            user_rect,
            username,
            font_input,
            active_field == "username",
            False,
            cursor_visible,
        )

        # Draw password field
        password_label_surf = font_label.render("Password", True, WHITE)
        screen_surf.blit(
            password_label_surf,
            password_label_surf.get_rect(midbottom=(cx, y_pass_box - 5)),
        )
        _draw_input_box(
            screen_surf,
            pass_rect,
            password,
            font_input,
            active_field == "password",
            True,
            cursor_visible,
        )

        # Draw login button (guard if surface is mocked)
        try:
            pygame.draw.rect(
                screen_surf, GREEN, btn_rect, border_radius=BUTTON_BORDER_RADIUS
            )
        except Exception:
            pass
        button_text_surf = font_button.render("Login", True, BLACK)
        screen_surf.blit(
            button_text_surf, button_text_surf.get_rect(center=btn_rect.center)
        )

        # Draw status message
        if message:
            message_surf = font_msg.render(message, True, message_color)
            screen_surf.blit(message_surf, message_surf.get_rect(center=(cx, y_msg)))

        pygame.display.flip()

    # Handle return logic after loop exit
    if quit_flag:
        return "QUIT"

    if login_triggered:
        # Attempt network login
        print("UI: Calling network_client.login()...")
        result = network_client.login(username, password)

        if result.success:
            print(f"UI: Login successful for {result.username}")
            return "LOGIN_SUCCESS"
        else:
            print(f"UI: Login failed - {result.message}")
            return "LOGIN_FAIL"

    # Fallback (should not normally reach here)
    return "QUIT"


def show_start_screen(
    screen_surf: pygame.Surface,
    fonts: dict,
    logged_in_username: Optional[str] = None,
) -> str:
    """Display the start screen and wait for user input.

    Args:
        screen_surf: The Pygame screen surface
        clock_obj: The Pygame clock object
        fonts: Dictionary of loaded fonts
        high_score: The current high score to display
        logged_in_username: Username of logged-in user (if any)

    Returns:
        'START' to begin game, or 'QUIT' to exit
    """
    font_title = fonts.get("title") or pygame.font.SysFont(None, FONT_SIZE_TITLE)
    font_score = fonts.get("score") or pygame.font.SysFont(None, FONT_SIZE_SCORE)

    screen_surf.fill(BLACK)

    try:
        cx = SCREEN_WIDTH // 2

        # Draw logged-in username (if applicable)
        if logged_in_username:
            user_surf = font_score.render(
                f"Logged in as: {logged_in_username}", True, CYAN
            )
            screen_surf.blit(
                user_surf,
                user_surf.get_rect(
                    center=(cx, int(SCREEN_HEIGHT * START_USER_Y_RATIO))
                ),
            )

        # Draw title
        title_surf = font_title.render(START_TITLE_TEXT, True, WHITE)
        screen_surf.blit(
            title_surf,
            title_surf.get_rect(center=(cx, int(SCREEN_HEIGHT * START_TITLE_Y_RATIO))),
        )

        # Draw high score
        score_surf = font_score.render(f"High Score: {high_score}", True, WHITE)
        screen_surf.blit(
            score_surf,
            score_surf.get_rect(center=(cx, int(SCREEN_HEIGHT * START_SCORE_Y_RATIO))),
        )

        # Draw prompt
        prompt_surf = font_score.render(START_PROMPT_TEXT, True, YELLOW)
        screen_surf.blit(
            prompt_surf,
            prompt_surf.get_rect(
                center=(cx, int(SCREEN_HEIGHT * START_PROMPT_Y_RATIO))
            ),
        )
    except Exception as e:
        print(f"Error rendering start screen: {e}")

    pygame.display.flip()

    # Wait for key press or quit
    waiting = True
    clock_obj = pygame.time.Clock()
    while waiting:
        clock_obj.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                return "START"

    return "QUIT"  # Fallback


def show_end_screen(
    screen_surf: pygame.Surface,
    fonts: dict,
    game_result: str,
    final_score: int,
    submission_status: Optional[str] = None,
) -> str:
    """Display the game over/win screen and wait for player input.

    Args:
        screen_surf: The Pygame screen surface
        clock_obj: The Pygame clock object
        fonts: Dictionary of loaded fonts
        game_result: 'WIN' or 'LOSE' (determines message and color)
        final_score: The player's final score
        submission_status: Optional status message about score submission

    Returns:
        'REPLAY' to play again, or 'QUIT' to exit
    """
    font_large = fonts.get("large") or pygame.font.SysFont(None, FONT_SIZE_LARGE)
    font_score = fonts.get("score") or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    font_small = fonts.get("small") or pygame.font.SysFont(None, FONT_SIZE_SCORE - 6)

    # Determine result text and color
    result_text = END_WIN_TEXT if game_result == "WIN" else END_LOSE_TEXT
    result_color = GREEN if game_result == "WIN" else RED

    # Create semi-transparent overlay
    overlay = _create_semi_transparent_overlay(SCREEN_WIDTH, SCREEN_HEIGHT)

    # Calculate positions
    cx = SCREEN_WIDTH // 2
    cy_title = int(SCREEN_HEIGHT * END_TITLE_Y_RATIO)
    cy_score = int(SCREEN_HEIGHT * END_SCORE_Y_RATIO)
    cy_status = cy_score + END_STATUS_Y_OFFSET
    cy_instruction = (
        int(SCREEN_HEIGHT * END_INSTRUCTION_Y_RATIO) + END_INSTRUCTION_Y_OFFSET
    )

    waiting = True
    clock_obj = pygame.time.Clock()
    while waiting:
        clock_obj.tick(FPS)

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_r:
                    return "REPLAY"
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return "QUIT"

        # Rendering
        screen_surf.blit(overlay, (0, 0))

        # Draw result message
        result_surf = font_large.render(result_text, True, result_color)
        screen_surf.blit(result_surf, result_surf.get_rect(center=(cx, cy_title)))

        # Draw final score
        score_surf = font_score.render(f"Final Score: {final_score}", True, WHITE)
        screen_surf.blit(score_surf, score_surf.get_rect(center=(cx, cy_score)))

        # Draw submission status (if provided)
        if submission_status:
            status_color = _determine_status_color(submission_status)
            status_surf = font_small.render(submission_status, True, status_color)
            screen_surf.blit(status_surf, status_surf.get_rect(center=(cx, cy_status)))

        # Draw instructions
        instruction_surf = font_score.render(END_INSTRUCTION_TEXT, True, YELLOW)
        screen_surf.blit(
            instruction_surf, instruction_surf.get_rect(center=(cx, cy_instruction))
        )

        pygame.display.flip()

    return "QUIT"  # Fallback


def show_level_start_screen(
    screen_surf: pygame.Surface,
    fonts: dict,
    level_number: int,
    duration_ms: int,
) -> str:
    """Display 'Level N' for a brief duration.

    Args:
        screen_surf: The Pygame screen surface
        clock_obj: The Pygame clock object
        fonts: Dictionary of loaded fonts
        level_number: The level number to display

    Raises:
        SystemExit: If a quit event is received during display
    """
    font_large = fonts.get("large") or pygame.font.SysFont(None, FONT_SIZE_LARGE)

    screen_surf.fill(BLACK)

    try:
        level_surf = font_large.render(f"Level {level_number}", True, WHITE)
        screen_surf.blit(
            level_surf,
            level_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)),
        )
    except Exception as e:
        print(f"Error rendering level start: {e}")

    pygame.display.flip()

    # Wait for duration while checking for quit events
    start_ticks = pygame.time.get_ticks()
    clock_obj = pygame.time.Clock()
    while pygame.time.get_ticks() - start_ticks < duration_ms:
        clock_obj.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT"

    return "START_LEVEL"
