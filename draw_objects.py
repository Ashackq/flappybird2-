# draw_objects.py
import pygame
import random

bird_width = 40
bird_height = 30
bird_sprite = pygame.image.load("assets/sprite.png")
bird_sprite = pygame.transform.scale(bird_sprite, (bird_width, bird_height))

RED = (255, 0, 0)
BLACK = (0, 10, 0)
colors = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 255, 0),  # Yellow
    (0, 255, 255),  # Cyan
    (255, 0, 255),  # Magenta
    (255, 255, 255),  # White
    (128, 128, 128),  # Gray
    (192, 192, 192),  # Light Gray
    (64, 64, 64),  # Dark Gray
    (255, 165, 0),  # Orange
    (165, 42, 42),  # Brown
    (255, 192, 203),  # Pink
    (128, 0, 128),  # Purple
    (0, 255, 0),  # Lime
    (0, 128, 128),  # Teal
    (128, 0, 0),  # Maroon
    (0, 0, 128),  # Navy
    (128, 128, 0),  # Olive
    (135, 206, 235),  # Sky Blue
    (250, 128, 114),  # Salmon
]
random_color = random.choice(colors)


def draw_bird(win, x, y, width, id):
    # pygame.draw.rect(win, RED, (x, y, width, height))
    pygame.draw.circle(win, random_color, [x, y], width / 2, 0)
    win.blit(bird_sprite, (x, y))


def draw_pipe(win, x, y, height, gap, pipe_width, win_height):
    pygame.draw.rect(win, BLACK, (x, 0, pipe_width, height))
    pygame.draw.rect(
        win, BLACK, (x, height + gap, pipe_width, win_height - height - gap)
    )
