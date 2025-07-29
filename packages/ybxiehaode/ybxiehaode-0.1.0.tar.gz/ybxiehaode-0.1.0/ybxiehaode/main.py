# -*- coding: utf-8 -*-
# @Author  : 鱼玄机
# @File    : main.py
# @Time    : 2025/6/30 20:26
# fireworks_ai/main.py

import pygame
import random
import math
import sys
import time


def main():
    pygame.init()
    WIDTH, HEIGHT = 1000, 700
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("三生万物 - AI烟花秀")
    clock = pygame.time.Clock()

    # 设置字体
    title_font = pygame.font.SysFont("SimHei", 80)
    bubble_font = pygame.font.SysFont("SimHei", 30)

    # ===== 烟花粒子类 =====
    class Particle:
        def __init__(self, x, y, color, angle=None, speed=None):
            self.x = x
            self.y = y
            self.radius = 2
            angle = angle if angle is not None else random.uniform(0, 2 * math.pi)
            speed = speed if speed is not None else random.uniform(3, 7)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
            self.color = color
            self.life = 100
            self.trail = []

        def update(self):
            self.trail.append((self.x, self.y))
            if len(self.trail) > 10:
                self.trail.pop(0)

            self.x += self.vx
            self.y += self.vy
            self.vy += 0.05  # 模拟重力
            self.life -= 1

        def draw(self, surface):
            for i, (tx, ty) in enumerate(self.trail):
                alpha = int(255 * (i / len(self.trail)))
                trail_color = (*self.color, alpha)
                s = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(s, trail_color, (2, 2), 2)
                surface.blit(s, (int(tx), int(ty)))

            if self.life > 0:
                pygame.draw.circle(surface, self.color, (int(self.x), int(self.y)), self.radius)

    # ===== 烟花生成器 =====
    def create_firework():
        x = random.randint(100, WIDTH - 100)
        y = random.randint(100, HEIGHT // 2)
        base_color = [random.randint(100, 255) for _ in range(3)]
        return [Particle(x, y, base_color) for _ in range(60)]

    # ===== AI“哲理语”泡泡类 =====
    zen_quotes = [
        "一生二，二生三，三生万物。",
        "形而上者谓之道，形而下者谓之器。",
        "有无相生，难易相成。",
        "知人者智，自知者明。",
        "无为而无不为。",
        "顺其自然，万物皆一。"
    ]

    class QuoteBubble:
        def __init__(self, text, x, y):
            self.text = text
            self.x = x
            self.y = y
            self.life = 200
            self.speed = random.uniform(0.3, 1.0)
            self.alpha = 255

        def update(self):
            self.y -= self.speed
            self.life -= 1
            self.alpha = max(0, int(self.life / 200 * 255))

        def draw(self, surface):
            if self.life > 0:
                s = bubble_font.render(self.text, True, (255, 255, 255))
                s.set_alpha(self.alpha)
                surface.blit(s, (int(self.x), int(self.y)))

    # ===== 星空背景点 =====
    stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(30, 100)) for _ in range(100)]

    # ===== 主循环 =====
    particles = []
    bubbles = []
    frame_count = 0
    last_bubble_time = time.time()
    running = True

    while running:
        screen.fill((0, 0, 20))  # 深夜蓝背景

        # 背景星星
        for (sx, sy, brightness) in stars:
            pygame.draw.circle(screen, (brightness, brightness, brightness), (sx, sy), 1)

        # 随机添加烟花
        if random.random() < 0.05:
            particles.extend(create_firework())

        # 更新烟花粒子
        for p in particles[:]:
            p.update()
            p.draw(screen)
            if p.life <= 0:
                particles.remove(p)

        # 每隔几秒生成一个泡泡
        if time.time() - last_bubble_time > 5:
            quote = random.choice(zen_quotes)
            bubbles.append(QuoteBubble(quote, random.randint(100, WIDTH - 300), random.randint(100, HEIGHT - 200)))
            last_bubble_time = time.time()

        # 更新并绘制泡泡
        for b in bubbles[:]:
            b.update()
            b.draw(screen)
            if b.life <= 0:
                bubbles.remove(b)

        # 三生万物标题特效
        offset = int(math.sin(frame_count * 0.05) * 5)
        glow_color = (255, 255, 180)
        text_surface = title_font.render("三生万物", True, glow_color)

        # 发光边框效果
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2)]:
            glow = title_font.render("三生万物", True, (255, 255, 180, 50))
            screen.blit(glow, ((WIDTH - text_surface.get_width()) // 2 + dx, HEIGHT - 150 + dy + offset))

        # 主文字
        screen.blit(text_surface, ((WIDTH - text_surface.get_width()) // 2, HEIGHT - 150 + offset))

        # 刷新
        pygame.display.flip()
        clock.tick(60)
        frame_count += 1

        # 退出事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()