"""Functions for displaying various UI screens and handling UI-specific input.

Contains functions responsible for rendering and managing user interactions
on non-gameplay screens like the login screen, start menu, game over/win screen,
and level transition screens.
"""
# game/ui.py
import pygame
import sys
from .settings import *
# Import the updated network_client
from . import network_client as network

def show_login_screen(screen_surf, clock_obj, fonts, previous_message=None):
    """
    Displays the login screen, handles input, and attempts API login.

    Args:
        screen_surf: The Pygame screen surface.
        clock_obj: The Pygame clock object.
        fonts (dict): Dictionary of loaded fonts.
        previous_message (str, optional): Message to display from a previous attempt.

    Returns:
        tuple: (str: action, str|None: username, str: message)
               Action is 'LOGIN_SUCCESS', 'LOGIN_FAIL', or 'QUIT'.
               Username is returned on success. Message provides status/error info.
    """
    font_title  = fonts.get('large') or pygame.font.SysFont(None, FONT_SIZE_LARGE)
    font_label  = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    font_input  = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    font_button = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    font_msg    = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE - 4)

    username = ""
    password = ""
    active_field = "username"
    # Use previous message if provided, otherwise default
    message = previous_message or "Enter username and password to play online"
    # Determine color based on likely failure keywords in previous message
    message_color = RED if previous_message and ("fail" in previous_message.lower() or "error" in previous_message.lower()) else WHITE

    cursor_visible = True
    cursor_timer = 0.0

    input_w, input_h = 350, 45
    btn_w, btn_h   = 180, 50
    cx = SCREEN_WIDTH // 2

    y_title    = SCREEN_HEIGHT * 0.2
    y_user_lbl = SCREEN_HEIGHT * 0.4
    y_user_box = y_user_lbl + 35
    y_pass_lbl = y_user_box + input_h + 20
    y_pass_box = y_pass_lbl + 35
    y_btn      = y_pass_box + input_h + 40
    y_msg      = y_btn + btn_h + 30

    user_rect = pygame.Rect(cx - input_w//2, y_user_box, input_w, input_h)
    pass_rect = pygame.Rect(cx - input_w//2, y_pass_box, input_w, input_h)
    btn_rect  = pygame.Rect(cx - btn_w//2,    y_btn,     btn_w,  btn_h)

    quit_flag = False
    login_triggered = False

    # --- Main loop ---
    while not (quit_flag or login_triggered):
        dt = clock_obj.tick(FPS) / 1000.0
        cursor_timer += dt
        if cursor_timer >= 0.5:
            cursor_timer = 0.0
            cursor_visible = not cursor_visible

        events = pygame.event.get()
        # --- Event handling ---
        for e in events:
            if e.type == pygame.QUIT:
                quit_flag = True
                break # Exit inner event loop

            if e.type == pygame.MOUSEBUTTONDOWN:
                if user_rect.collidepoint(e.pos):
                    active_field = "username"
                elif pass_rect.collidepoint(e.pos):
                    active_field = "password"
                else:
                    active_field = None # Clicked outside input boxes

                if btn_rect.collidepoint(e.pos):
                    message = "Logging in..." # Update message immediately
                    message_color = YELLOW
                    login_triggered = True
                    break # Exit inner event loop

            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE: # Allow Esc key to quit
                    quit_flag = True
                    break # Exit inner event loop

                if e.key == pygame.K_RETURN: # Enter key triggers login
                    message = "Logging in..."
                    message_color = YELLOW
                    login_triggered = True
                    break # Exit inner event loop

                if e.key == pygame.K_TAB:
                    active_field = "password" if active_field == "username" else "username"
                elif e.key == pygame.K_BACKSPACE:
                    if active_field == "username":
                        username = username[:-1]
                    elif active_field == "password":
                        password = password[:-1]
                else:
                    # Add typed character if printable
                    if e.unicode and e.unicode.isprintable():
                        if active_field == "username" and len(username) < 30: # Limit length
                            username += e.unicode
                        elif active_field == "password" and len(password) < 30: # Limit length
                            password += e.unicode

        # --- DRAW EVERYTHING ---
        screen_surf.fill(BLACK)

        # Title
        t_surf = font_title.render("PlaneWar Login", True, WHITE)
        screen_surf.blit(t_surf, t_surf.get_rect(center=(cx, y_title)))

        # --- Input Field Drawing Helper ---
        def draw_input_box(rect, text, is_active, is_password):
            # Border (thicker if active)
            border_thickness = 4 if is_active else 2
            pygame.draw.rect(screen_surf, WHITE, rect, border_thickness)
            # Text (masked if password)
            display_text = "*" * len(text) if is_password else text
            text_surf = font_input.render(display_text, True, WHITE)
            text_rect = text_surf.get_rect(midleft=(rect.left + 10, rect.centery))
            screen_surf.blit(text_surf, text_rect)
            # Cursor (if active and visible)
            if is_active and cursor_visible:
                cursor_x = text_rect.right + 2
                pygame.draw.line(screen_surf, WHITE, (cursor_x, rect.top + 5), (cursor_x, rect.bottom - 5), 2)

        # Draw Username field
        l_surf = font_label.render("Username", True, WHITE)
        screen_surf.blit(l_surf, l_surf.get_rect(midbottom=(cx, y_user_box - 5)))
        draw_input_box(user_rect, username, active_field == "username", False)

        # Draw Password field
        p_l = font_label.render("Password", True, WHITE)
        screen_surf.blit(p_l, p_l.get_rect(midbottom=(cx, y_pass_box - 5)))
        draw_input_box(pass_rect, password, active_field == "password", True)

        # Draw Login button
        pygame.draw.rect(screen_surf, GREEN, btn_rect, border_radius=5)
        btn_s = font_button.render("Login", True, BLACK)
        screen_surf.blit(btn_s, btn_s.get_rect(center=btn_rect.center))

        # Status message
        if message:
            m_s = font_msg.render(message, True, message_color)
            screen_surf.blit(m_s, m_s.get_rect(center=(cx, y_msg)))

        pygame.display.flip() # Update screen

        # Exit loop check (needed if login triggered without break)
        if quit_flag or login_triggered:
            break

    # --- End of loop, handle return logic ---
    if quit_flag:
        # Return 'QUIT' action, no username, no message
        return "QUIT", None, None

    if login_triggered:
        # Try the network login using the updated network_client function
        print("UI: Calling network.api_login_user...")
        # --- Updated Call and Return Handling ---
        success, logged_username, status_message = network.api_login_user(username, password)
        if success:
            # Return 'LOGIN_SUCCESS' action, the username, and success message
            print(f"UI: Login successful for {logged_username}")
            return "LOGIN_SUCCESS", logged_username, status_message
        else:
            # Return 'LOGIN_FAIL' action, no username, and the error message
            print(f"UI: Login failed - {status_message}")
            return "LOGIN_FAIL", None, status_message
        # --------------------------------------

    # Fallback if loop exited unexpectedly (shouldn't normally happen)
    return "QUIT", None, "Unexpected exit from login screen"


# --- Other UI functions remain the same ---

def show_start_screen(screen_surf, clock_obj, fonts, high_score, logged_in_username=None):
    """
    Displays the start screen and returns 'START' or 'QUIT'.
    (No changes needed here based on login update)
    """
    font_title = fonts.get('title') or pygame.font.SysFont(None, FONT_SIZE_TITLE)
    font_score = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE)

    screen_surf.fill(BLACK)
    try:
        if logged_in_username:
            w_s = font_score.render(f"Logged in as: {logged_in_username}", True, CYAN)
            screen_surf.blit(w_s, w_s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT*0.15)))

        t_s = font_title.render("飞机大战", True, WHITE) # Using Chinese title from your main.py
        screen_surf.blit(t_s, t_s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT*0.35)))

        hs_s = font_score.render(f"High Score: {high_score}", True, WHITE)
        screen_surf.blit(hs_s, hs_s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT*0.55)))

        p_s = font_score.render("Press any key to start", True, YELLOW)
        screen_surf.blit(p_s, p_s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT*0.75)))
    except Exception as e:
        print(f"Error rendering start screen: {e}")

    pygame.display.flip()

    # Wait for key press or quit
    waiting = True
    while waiting:
        clock_obj.tick(FPS)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return "QUIT"
            if e.type == pygame.KEYDOWN:
                return "START"
            if e.type == pygame.MOUSEBUTTONDOWN:
                 return "START"
    return "QUIT" # Fallback


def show_end_screen(screen_surf, clock_obj, fonts, game_result, final_score, submission_status=None):
    """
    Displays the game over/win screen and waits for player input (R/Q/Enter/Esc).
    (No changes needed here based on login update)
    """
    font_large = fonts.get('large') or pygame.font.SysFont(None, FONT_SIZE_LARGE)
    font_score = fonts.get('score') or pygame.font.SysFont(None, FONT_SIZE_SCORE)
    font_small = fonts.get('small') or pygame.font.SysFont(None, FONT_SIZE_SCORE - 6)

    result_text = "YOU WIN!" if game_result == "WIN" else "GAME OVER"
    result_color = GREEN if game_result == "WIN" else RED
    instruction = "Press ENTER or R to Play Again, ESC or Q to Quit"

    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 180))

    waiting = True
    while waiting:
        clock_obj.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'QUIT'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_r:
                    return 'REPLAY'
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    return 'QUIT'

        screen_surf.blit(overlay, (0, 0))

        msg_surf = font_large.render(result_text, True, result_color)
        msg_rect = msg_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 4))
        screen_surf.blit(msg_surf, msg_rect)

        score_surf = font_score.render(f"Final Score: {final_score}", True, WHITE)
        score_rect = score_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen_surf.blit(score_surf, score_rect)

        if submission_status:
            status_color = GREEN if "success" in submission_status.lower() or "saved" in submission_status.lower() else \
                           RED if "fail" in submission_status.lower() or "error" in submission_status.lower() or "not logged in" in submission_status.lower() else \
                           YELLOW # Default/neutral color
            status_surf = font_small.render(submission_status, True, status_color)
            status_rect = status_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
            screen_surf.blit(status_surf, status_rect)

        instr_surf = font_score.render(instruction, True, YELLOW)
        instr_rect = instr_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT * 3 // 4 + 30))
        screen_surf.blit(instr_surf, instr_rect)

        pygame.display.flip()

    return 'QUIT' # Fallback


def show_level_start_screen(screen_surf, clock_obj, fonts, level_number):
    """
    Displays "Level N" for 1.5 seconds. Raises SystemExit if quit event received.
    (No changes needed here based on login update)
    """
    font_large = fonts.get('large') or pygame.font.SysFont(None, FONT_SIZE_LARGE)
    screen_surf.fill(BLACK)
    try:
        l_s = font_large.render(f"Level {level_number}", True, WHITE)
        screen_surf.blit(l_s, l_s.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)))
    except Exception as e:
        print(f"Error rendering level start: {e}")

    pygame.display.flip()

    start_ticks = pygame.time.get_ticks()
    while pygame.time.get_ticks() - start_ticks < 1500:
        clock_obj.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("QUIT event detected in show_level_start_screen loop.")
                raise SystemExit
    print("show_level_start_screen finished normally.")
    return None