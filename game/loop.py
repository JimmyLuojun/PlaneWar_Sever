"""
Level loop logic for the PlaneWar Pygame client.

Contains the `run_game` orchestration function that manages a single level's
event-driven loop, including spawning, updates, collisions, and drawing.
Applies the Event-Driven Standard Order from CLAUDE.md within function scope.
"""

# ==============================================================================
# Imports (dependencies)
# ==============================================================================
from __future__ import annotations

import random
import sys
from typing import Any, Protocol, runtime_checkable, cast

import pygame

from .settings import (
    WHITE,
    ORANGE,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    FPS,
    STARTUP_GRACE_PERIOD,
    BOMB_KEY,
)
from .player import Player
from .enemy import Enemy, EnemyBoss
from .powerup import PowerUp
from .background import Background


# ==============================================================================
# Orchestration Function (Core Logic)
# ==============================================================================
@runtime_checkable
class CollidableSprite(Protocol):
    """Protocol for sprites used with pygame.sprite.spritecollide.

    Requires `image` and `rect` attributes.
    """
    image: pygame.Surface
    rect: pygame.Rect

def run_game(
    screen_surf: pygame.Surface,
    clock_obj: pygame.time.Clock,
    fonts: dict[str, pygame.font.Font],
    images: dict[str, pygame.Surface | dict[str, pygame.Surface]],
    sounds: dict[str, pygame.mixer.Sound],
    level_data: dict[str, Any],
    background: Background,
) -> tuple[str, int, int]:
    """
    Runs a single level. Spawns enemies, handles player actions, collisions,
    and level progression. Uses the Background object for drawing and updating.

    Args:
        screen_surf: The main Pygame screen surface.
        clock_obj: The Pygame clock object.
        fonts: Dictionary of loaded fonts.
        images: Dictionary of loaded images.
        sounds: Dictionary of loaded sounds.
        level_data: Configuration for the current level.
        background: The background object.

    Returns:
        tuple[str, int, int]: (result ('PASSED', 'FAILED', 'QUIT'), score, level_number)
    """
    level_num = level_data.get("level_number", "?")
    print(f"\n--- Starting Level {level_num} ---")

    # --- Get Level Configuration ---
    is_boss_level = level_data.get("is_boss_level", False)
    boss_targets_player_flag = level_data.get("boss_targets_player", False)
    boss_fire_rate_multiplier = level_data.get("boss_fire_rate_multiplier", 1.0)
    enemy_types = level_data.get("enemy_types", ["enemy1"])
    spawn_interval = level_data.get("spawn_interval", 30)
    max_on_screen = level_data.get("max_on_screen", 8)
    enemy_speed_y_range = level_data.get("enemy_speed_y_range", (1, 4))
    enemy_speed_x_range = level_data.get("enemy_speed_x_range", (-1, 1))
    powerup_interval = level_data.get("powerup_interval", 10000)
    boss_appear_delay_seconds = level_data.get("boss_appear_delay_seconds", 99999)

    # --- Resources ---
    font_score = fonts.get("score") or pygame.font.SysFont(None, 24)
    player_img = images.get("player")
    boss_img = images.get("boss")
    powerup_images_dict = images.get("powerups", {})
    available_enemy_images: list[pygame.Surface] = []
    for etype in enemy_types:
        img = images.get(etype)
        if isinstance(img, pygame.Surface):
            available_enemy_images.append(img)
        else:
            print(
                f"Error: Image for enemy type '{etype}' is not a valid Surface in level {level_num}."
            )

    # --- Initialize Level State ---
    all_sprites = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    bullets = pygame.sprite.Group()
    enemy_bullets = pygame.sprite.Group()
    powerups = pygame.sprite.Group()
    boss_group = pygame.sprite.GroupSingle()

    if not isinstance(player_img, pygame.Surface):
        print("CRITICAL ERROR: Player image not available. Exiting.")
        pygame.quit()
        sys.exit("Asset Loading Error")

    player = Player(
        player_img,
        sounds.get("player_shoot"),
        sounds.get("shield_up"),
        sounds.get("shield_down"),
        sounds.get("powerup_pickup"),
        sounds.get("bomb"),
    )
    all_sprites.add(player)

    # Level State Variables
    game_over_local = False
    level_passed = False
    boss_active = False
    boss_spawned = False
    boss_defeated = False
    boss_instance: EnemyBoss | None = None
    enemy_spawn_timer = 0
    powerup_last_spawn_time = pygame.time.get_ticks()
    level_start_time = pygame.time.get_ticks()

    # --- Level Game Loop ---
    running_this_level = True
    while running_this_level:
        # Timing
        clock_obj.tick(FPS)
        now = pygame.time.get_ticks()

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "QUIT", player.score, level_num

            if event.type == pygame.KEYDOWN:
                if (
                    event.key == BOMB_KEY
                    and not game_over_local
                    and player.bomb_count > 0
                ):
                    killed_by_bomb = player.use_bomb(enemies, enemy_bullets)
                    player.score += killed_by_bomb

        # --- Game Logic Update ---
        if not game_over_local and not level_passed:
            all_sprites.update()
            background.update()

            # Player Shooting
            keys = pygame.key.get_pressed()
            mouse_buttons = pygame.mouse.get_pressed()
            if keys[pygame.K_SPACE] or mouse_buttons[0]:
                new_player_bullets = player.shoot()
                if new_player_bullets:
                    all_sprites.add(new_player_bullets)
                    bullets.add(new_player_bullets)

            # Boss Spawning Logic
            if is_boss_level and not boss_spawned and not boss_defeated:
                elapsed_seconds = (now - level_start_time) / 1000
                if elapsed_seconds >= boss_appear_delay_seconds:
                    if not isinstance(boss_img, pygame.Surface):
                        print(
                            f"Error: Boss image missing or invalid for level {level_num}. Failing level."
                        )
                        game_over_local = True
                    elif not boss_active:
                        print(
                            f"Spawning Boss (Targeting: {boss_targets_player_flag}, "
                            f"Fire Rate: {boss_fire_rate_multiplier}x)"
                        )
                        boss_instance = EnemyBoss(
                            boss_img,
                            sounds.get("boss_shoot"),
                            all_sprites,
                            enemy_bullets,
                            target_player=boss_targets_player_flag,
                            player_ref=player,
                            fire_rate_multiplier=boss_fire_rate_multiplier,
                        )
                        boss_group.add(boss_instance)
                        boss_active = True
                        boss_spawned = True
                        print("Boss Incoming!")
                        boss_intro_sound = sounds.get("boss_intro")
                        if boss_intro_sound:
                            try:
                                boss_intro_sound.play()
                            except pygame.error as e:
                                print(f"Warning: Could not play boss intro sound: {e}")

            # Regular Enemy Spawning Logic
            if available_enemy_images and not (is_boss_level and boss_spawned):
                enemy_spawn_timer += 1
                if enemy_spawn_timer >= spawn_interval and len(enemies) < max_on_screen:
                    enemy_spawn_timer = 0
                    chosen_img = random.choice(available_enemy_images)
                    enemy = Enemy(
                        chosen_img,
                        speed_y_range=enemy_speed_y_range,
                        speed_x_range=enemy_speed_x_range,
                    )
                    all_sprites.add(enemy)
                    enemies.add(enemy)

            # Powerup Spawning Logic
            if now - powerup_last_spawn_time > powerup_interval:
                powerup_last_spawn_time = now
                if powerup_images_dict and isinstance(powerup_images_dict, dict):
                    powerup = PowerUp(powerup_images_dict)
                    all_sprites.add(powerup)
                    powerups.add(powerup)

            # --- Collisions ---
            enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True)
            for _ in enemy_hits:
                player.score += 1
                enemy_explode_sound = sounds.get("enemy_explode")
                if enemy_explode_sound:
                    try:
                        enemy_explode_sound.play()
                    except pygame.error as e:
                        print(f"Warning: Could not play enemy explode sound: {e}")

            if boss_active and boss_instance:
                bullets_hitting_boss = pygame.sprite.spritecollide(
                    cast(CollidableSprite, boss_instance), bullets, True  # pyright: ignore[reportArgumentType]
                )
                if bullets_hitting_boss:
                    boss_hit_sound = sounds.get("boss_hit")
                    if boss_hit_sound:
                        try:
                            boss_hit_sound.play()
                        except pygame.error as e:
                            print(f"Warning: Could not play boss hit sound: {e}")
                    boss_instance.health -= len(bullets_hitting_boss)
                    if boss_instance.health <= 0:
                        boss_explode_sound = sounds.get("boss_explode")
                        if boss_explode_sound:
                            try:
                                boss_explode_sound.play()
                            except pygame.error as e:
                                print(
                                    f"Warning: Could not play boss explode sound: {e}"
                                )
                        game_win_sound = sounds.get("game_win")
                        if game_win_sound:
                            try:
                                game_win_sound.play()
                            except pygame.error as e:
                                print(f"Warning: Could not play game win sound: {e}")
                        boss_instance.kill()
                        player.score += 50
                        print("Boss Defeated!")
                        boss_defeated = True
                        boss_active = False
                        boss_instance = None
                        level_passed = True

            powerup_hits = pygame.sprite.spritecollide(cast(CollidableSprite, player), powerups, True)  # pyright: ignore[reportArgumentType]
            for hit_powerup in powerup_hits:
                player.activate_powerup(hit_powerup.type)

            # --- Player Death Check ---
            if now - level_start_time > STARTUP_GRACE_PERIOD:
                if player.alive() and not player.shield_active:
                    player_enemy_hits = pygame.sprite.spritecollide(
                        cast(CollidableSprite, player), enemies, True  # pyright: ignore[reportArgumentType]
                    )
                    player_boss_collision = pygame.sprite.spritecollide(
                        cast(CollidableSprite, player), boss_group, False  # pyright: ignore[reportArgumentType]
                    )
                    enemy_bullet_hits = pygame.sprite.spritecollide(
                        cast(CollidableSprite, player), enemy_bullets, True  # pyright: ignore[reportArgumentType]
                    )

                    if player_enemy_hits or player_boss_collision or enemy_bullet_hits:
                        reason = (
                            "Enemy"
                            if player_enemy_hits
                            else (
                                "Boss Collision"
                                if player_boss_collision
                                else "Enemy Bullet"
                            )
                        )
                        print(f"Player hit by {reason}! Level Failed!")
                        player_lose_sound = sounds.get("player_lose")
                        if player_lose_sound:
                            try:
                                player_lose_sound.play()
                            except pygame.error as e:
                                print(f"Warning: Could not play player lose sound: {e}")
                        player.kill()
                        game_over_local = True

        # --- Drawing ---
        background.draw(screen_surf)
        all_sprites.draw(screen_surf)

        # Draw UI
        try:
            score_text = font_score.render(f"Score: {player.score}", True, WHITE)
            screen_surf.blit(score_text, (10, 10))
            bomb_text = font_score.render(f"Bombs: {player.bomb_count}", True, ORANGE)
            screen_surf.blit(bomb_text, (10, 40))
            level_text_surf = font_score.render(f"Level: {level_num}", True, WHITE)
            level_rect = level_text_surf.get_rect(topright=(SCREEN_WIDTH - 10, 10))
            screen_surf.blit(level_text_surf, level_rect)
        except Exception as e:
            print(f"Error rendering UI text: {e}")

        if boss_active and boss_instance:
            boss_instance.draw_health_bar(screen_surf)
        if player.shield_active:
            player.draw_shield(screen_surf)

        if is_boss_level and boss_defeated:
            level_passed = True

        if game_over_local or level_passed:
            running_this_level = False

        pygame.display.flip()

    result = "PASSED" if level_passed else ("FAILED" if game_over_local else "QUIT")
    print(f"--- Level {level_num} Ended. Result: {result}, Score: {player.score} ---")
    return result, player.score, level_num
