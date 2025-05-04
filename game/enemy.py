# /Users/junluo/Desktop/桌面文件/PlaneWar_Sever/game/enemy.py

import pygame
import random
from pygame.math import Vector2
from .settings import *
from .bullet import EnemyBullet
import math

class Enemy(pygame.sprite.Sprite):
    """Basic enemy that drifts down and bounces horizontally."""
    def __init__(self, enemy_img, speed_y_range=None, speed_x_range=None):
        super().__init__()
        self.image = enemy_img
        self.rect = self.image.get_rect()
        # 随机初始位置
        self.rect.x = random.randint(0, SCREEN_WIDTH - self.rect.width)
        self.rect.y = random.randint(-100, -40)
        # 随机速度
        min_y, max_y = speed_y_range or (ENEMY_MIN_SPEED_Y, ENEMY_MAX_SPEED_Y)
        min_x, max_x = speed_x_range or (ENEMY_MIN_SPEED_X, ENEMY_MAX_SPEED_X)
        min_y, max_y = max(1, min_y), max(min_y, max_y)
        self.speedy = random.randint(min_y, max_y)
        xs = [i for i in range(min_x, max_x + 1) if i != 0] or [1]
        self.speedx = random.choice(xs)

    def update(self):
        self.rect.x += self.speedx
        self.rect.y += self.speedy
        # 左右反弹
        if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
            self.speedx *= -1
        # 出屏删除
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class EnemyBoss(pygame.sprite.Sprite):
    """Big boss: enters, patrols,智能预判射击，承受伤害。"""
    def __init__(self, boss_img, shoot_sound, all_sprites_group, enemy_bullets_group,
                 target_player=False, player_ref=None):
        super().__init__()
        # 基本属性...
        self.image = boss_img.copy()
        self.rect = self.image.get_rect(centerx=SCREEN_WIDTH//2, bottom=-20)
        self.entry_speedy = BOSS_SPEED_Y
        self.entry_y = BOSS_ENTRY_Y
        self.speedx = BOSS_SPEED_X
        self.entered = False

        self.health = BOSS_MAX_HEALTH
        self.shoot_delay = BOSS_SHOOT_DELAY
        self.last_shot_time = 0
        self.shoot_sound = shoot_sound

        self.all_sprites = all_sprites_group
        self.enemy_bullets = enemy_bullets_group

        self.target_player = target_player
        self.player_ref = player_ref if target_player else None

        self.all_sprites.add(self)

    def update(self):
        now = pygame.time.get_ticks()
        # 入场
        if not self.entered:
            if self.rect.centery < self.entry_y:
                self.rect.y += self.entry_speedy
            else:
                self.entered = True
                self.last_shot_time = now
        else:
            # 巡逻
            self.rect.x += self.speedx
            if self.rect.left < 0 or self.rect.right > SCREEN_WIDTH:
                self.speedx *= -1
            # 射击
            if now - self.last_shot_time >= self.shoot_delay:
                self.shoot()
                self.last_shot_time = now

    def _compute_intercept_direction(self, shoot_pos, target_pos, target_vel, bullet_speed):
        """
        解 a t^2 + b t + c = 0:
          a = |v_t|^2 - v_b^2
          b = 2 * r·v_t
          c = |r|^2
        取最小正根 t，然后方向指向 (target_pos + v_t t - shoot_pos)
        """
        r = target_pos - shoot_pos
        a = target_vel.dot(target_vel) - bullet_speed**2
        b = 2 * r.dot(target_vel)
        c = r.dot(r)
        disc = b*b - 4*a*c
        if disc < 0 or abs(a) < 1e-6:
            # 无解或 a≈0：退化为朝当前位置开火
            return (r if r.length_squared()>0 else Vector2(0,1)).normalize()
        sqrt_d = math.sqrt(disc)
        t1 = (-b + sqrt_d) / (2*a)
        t2 = (-b - sqrt_d) / (2*a)
        t = min(x for x in (t1, t2) if x>0) if any(x>0 for x in (t1, t2)) else max(t1, t2)
        if t <= 0:
            return (r if r.length_squared()>0 else Vector2(0,1)).normalize()
        intercept = target_pos + target_vel * t - shoot_pos
        return intercept.normalize()

    def shoot(self):
        shoot_pos = Vector2(self.rect.midbottom)
        direction = Vector2(0, 1)
        # 只有开启了追踪且玩家存活
        if self.target_player and self.player_ref and self.player_ref.alive():
            tp = Vector2(self.player_ref.rect.center)
            tv = getattr(self.player_ref, "velocity", Vector2(0,0))
            direction = self._compute_intercept_direction(
                shoot_pos, tp, tv, ENEMY_BULLET_SPEED_Y
            )
        # 发射子弹
        bullet = EnemyBullet(shoot_pos.x, shoot_pos.y, direction=direction)
        self.all_sprites.add(bullet); self.enemy_bullets.add(bullet)
        # 播放音效
        if self.shoot_sound:
            try: self.shoot_sound.play()
            except pygame.error: pass

    def draw_health_bar(self, surf):
        # 与之前一致...
        if self.health <= 0: return
        bar_len, bar_h = 100, 10
        x = self.rect.centerx - bar_len//2; y = self.rect.top - bar_h - 5
        fill = int(self.health / BOSS_MAX_HEALTH * bar_len)
        pygame.draw.rect(surf, RED,   (x, y, bar_len, bar_h))
        pygame.draw.rect(surf, GREEN, (x, y, fill, bar_h))
        pygame.draw.rect(surf, WHITE, (x-1, y-1, bar_len+2, bar_h+2), 2)
