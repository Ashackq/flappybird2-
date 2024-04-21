import socket
import time
import pygame
import sys
import random
from draw_objects import draw_pipe, draw_bird
from game_states import start_screen, game_over_screen, wait_screen
from dbfn import db_init, db_save, save_game_state, load_game_state


# Server configuration
SERVER = "127.0.0.1"
PORT = 5051

user_id = 0
ready = 0
birds = []

# db data
db_init()
gameid = 101
name, high = load_game_state(gameid)
if name == None:
    name = "AKash"
    db_save(gameid, name)
print(name, high)

# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 400, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))


# Set the caption font
pygame.display.set_caption("Flappy Bird")

BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50

# assets
background_image = pygame.image.load("assets/b2g.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Bird properties
bird_width = 40
bird_height = 30
bird_x = 50
bird_y = HEIGHT // 2 - bird_height // 2
bird_speed = 5
gravity = 0.5
jump_force = -9

bird_sprite = pygame.image.load("assets/sprite.png")
bird_sprite = pygame.transform.scale(bird_sprite, (bird_width, bird_height))

# Pipe properties
pipe_width = 70
pipe_gap = 150
pipe_speed = 5
pipes = []


font = pygame.font.SysFont(None, 50)

# Game states
START_SCREEN = 0
PLAYING = 1
GAME_OVER = 2
WAITING = 3
game_state = -1
fps = 30
fpst = 0.3


def collision(pipe):
    if bird_x + bird_width > pipe[0] and bird_x < pipe[0] + pipe_width:
        if bird_y < pipe[1] or bird_y + bird_height > pipe[1] + pipe_gap:
            return True

    return False


def reset_game():
    global bird_y, bird_speed, pipes, score
    bird_y = HEIGHT // 2 - bird_height // 2
    bird_speed = 5
    pipes = []
    score = 0


def exitserver():
    s = socket.socket()

    try:
        s.connect((SERVER, PORT))
        send_text = "Byebye" ":" + str(user_id)
        s.sendall(send_text.encode("utf-8"))

        s.close()
    except socket.error as msg:
        print("Mesag:", msg)
        s.close()


def send_pos():
    time.sleep(fpst)
    global name, user_id, ready, bird_y, birds
    s = socket.socket()
    try:
        s.connect((SERVER, PORT))
        send_text = name + ":" + str(bird_y) + ":" + str(ready) + ":" + str(user_id)
        s.sendall(send_text.encode("utf-8"))
        yanit = s.recv(1024).decode("utf-8")
        spl = yanit.split(":")
        if spl[0] == "id":
            user_id = int(spl[-1])
        elif yanit == "START":
            ready = 3
        elif spl[0] == "ready":
            ready = int(spl[-1])
        else:
            birds = yanit.split(";")
            print(birds)

    except socket.error as msg:  # Handle other socket errors
        if "[WinError 10061]" not in str(msg):
            exitserver()
        else:
            print("Waiting for connection for server..")
    finally:
        s.close()  # Always close the socket


send_pos()


def main():
    global bird_y, bird_speed, game_state, ready, birds, run, high
    game_state = START_SCREEN
    score = 0
    clock = pygame.time.Clock()
    run = True

    start_button_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT
    )
    ready_button_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2,
        HEIGHT // 2 + 4 * BUTTON_HEIGHT,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    exit_button_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2,
        HEIGHT // 2 + 2 * BUTTON_HEIGHT,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )

    mouse_x, mouse_y = 0, 0

    frame_counter = 0
    while run:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                exitserver()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_state == START_SCREEN:
                    if ready > 0:
                        game_state = WAITING
                    else:
                        game_state = PLAYING
                if event.key == pygame.K_ESCAPE and game_state == GAME_OVER:
                    run = False
                    exitserver()
                if event.key == pygame.K_SPACE and game_state == PLAYING:
                    bird_speed = jump_force
                if event.key == pygame.K_RETURN:
                    if game_state == START_SCREEN or game_state == GAME_OVER:
                        game_state = PLAYING
                        reset_game()

        if game_state == START_SCREEN:

            if high == 0:
                h1 = None
                start_screen(win, WIDTH, HEIGHT, font, frame_counter, h1, ready)
            else:
                start_screen(win, WIDTH, HEIGHT, font, frame_counter, high, ready)
            # Handle mouse clicks on buttons
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_x, mouse_y):
                if pygame.mouse.get_pressed()[0]:  # Check left mouse button
                    if ready > 0:
                        game_state = WAITING
                    else:
                        game_state = PLAYING
                    reset_game()
            elif exit_button_rect.collidepoint(mouse_x, mouse_y):
                if pygame.mouse.get_pressed()[0]:  # Check left mouse button
                    run = False
                    reset_game()
                    if ready > 0:
                        exitserver()
            elif ready_button_rect.collidepoint(mouse_x, mouse_y):
                if pygame.mouse.get_pressed()[0]:  # Check left mouse button
                    ready = 1

            frame_counter += 1  # Increment the frame counter for animation
            pygame.time.Clock().tick(30)

        elif game_state == PLAYING:
            if ready > 0:
                send_pos()
            win.blit(background_image, (0, 0))
            # Move bird
            bird_speed += gravity
            bird_y += bird_speed
            if bird_y > HEIGHT:
                game_state = GAME_OVER

            # Generate pipes
            if len(pipes) == 0 or pipes[-1][0] < WIDTH - pipe_gap * 2:
                pipe_height = random.randint(100, HEIGHT - pipe_gap - 100)
                pipes.append((WIDTH, pipe_height))

            # Move pipes
            for i, pipe in enumerate(pipes):
                pipes[i] = (pipe[0] - pipe_speed, pipe[1])

                if pipe[0] + pipe_width < 0:
                    pipes.pop(i)
                    score += 1

                if collision(pipe):
                    game_state = GAME_OVER

                    # Draw everything
            # name:birdy:ready:id
            if ready > 0:
                for i in birds:
                    if i != "0":
                        spl = i.split(":")
                        if int(spl[-1]) != user_id:
                            if int(spl[-2]) == 3:
                                draw_bird(
                                    win, bird_x, float(spl[1]), bird_width, int(spl[-1])
                                )

            win.blit(bird_sprite, (bird_x, bird_y))

            for pipe in pipes:
                draw_pipe(win, pipe[0], pipe[1], pipe[1], pipe_gap, pipe_width, HEIGHT)

            score_text = font.render(str(score), True, WHITE)
            win.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 50))
            pygame.display.update()
        elif game_state == GAME_OVER:
            win.blit(background_image, (0, 0))
            if score > high:
                game_over_screen(win, WIDTH, HEIGHT, font, score)
            else:
                game_over_screen(win, WIDTH, HEIGHT, font, high)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                bird_speed = jump_force
        elif game_state == WAITING and ready > 0:
            wait_screen(win, WIDTH, HEIGHT, font, frame_counter)
            send_pos()
            if ready == 3:
                time.sleep(0.2)
                print("Lets Go!!")

                game_state = PLAYING
            frame_counter += 1  # Increment the frame counter for animation
            pygame.time.Clock().tick(30)

        clock.tick(fps)

    save_game_state(score, gameid, name)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
    exitserver()
