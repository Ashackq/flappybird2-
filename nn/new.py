import neat.config
import neat.population
import pygame
import random
import os
import neat

pygame.init()

gen = 0
# Set up the game window
WIDTH, HEIGHT = 500, 800


WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 0, 255)


background_image = pygame.image.load("assets/b2g.png")
background_image = pygame.transform.scale(background_image, (WIDTH, HEIGHT))

bird_sprite = pygame.image.load("assets/sprite.png")
bird_sprite = pygame.transform.scale(bird_sprite, (40, 30))

pipe_sprite = pygame.image.load("assets/pipe.png")
STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    def __init__(
        self,
        x,
        y,
        sprite=bird_sprite,
        speed=5,
        gravity=0.5,
        jump_force=-9,
    ):
        self.x = x
        self.y = y
        self.sprite = sprite
        self.width = self.sprite.get_width()
        self.height = self.sprite.get_height()
        self.speed = speed
        self.gravity = gravity
        self.jump_force = jump_force

    def draw(self, win):
        win.blit(self.sprite, (self.x, self.y))

    def update(self):
        self.speed += self.gravity
        self.y += self.speed

    def jump(self):
        self.speed = self.jump_force

    def get_mask(self):
        return pygame.mask.from_surface(self.sprite)


class Pipe:
    def __init__(self, x):
        self.speed = 5
        self.x = x
        self.pipe_gap = 150
        self.bottom_pipe_height = 0
        self.top_pipe_height = 0
        self.passed = False
        self.botpipe = pipe_sprite
        self.pipe_width = self.botpipe.get_width()
        self.toppipe = pygame.transform.flip(pipe_sprite, False, True)
        self.set_height()

    def set_height(self):
        self.pipe_height = random.randrange(50, 450)
        self.top_pipe_height = self.pipe_height - self.toppipe.get_height()
        self.bottom_pipe_height = self.pipe_height + self.pipe_gap

    def draw(self, win):
        win.blit(self.toppipe, (self.x, self.top_pipe_height))
        win.blit(self.botpipe, (self.x, self.bottom_pipe_height))

    def update(self):
        self.x -= self.speed

    def collide(self, bird: Bird):
        bird_mask = bird.get_mask()
        bottom_mask = pygame.mask.from_surface(self.botpipe)
        top_mask = pygame.mask.from_surface(self.toppipe)

        top_offset = (self.x - bird.x, self.top_pipe_height - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom_pipe_height - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if t_point or b_point:
            return True
        return False


def draw_window(win, birds: list[Bird], pipes: list[Pipe], score: int, gen):
    win.blit(background_image, (0, 0))
    for bird in birds:
        bird.draw(win)

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Score: " + str(score), 1, WHITE)
    win.blit(text, (WIDTH - 10 - text.get_width(), 10))
    text1 = STAT_FONT.render("Gen: " + str(gen), 1, WHITE)
    win.blit(text1, (10, 10))
    pygame.display.update()


def main(gnomes, config):
    global gen
    gen += 1
    nets = []
    ge = []
    birds = []

    for _, g in gnomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        g.fitness = 0
        ge.append(g)

    win = pygame.display.set_mode((WIDTH, HEIGHT))
    run = True
    clock = pygame.time.Clock()
    pipes = [Pipe(700)]

    score = 0

    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
            # if event.type == pygame.KEYDOWN:
            #     if event.key == pygame.K_SPACE and game_state == START_SCREEN:
            #         game_state = PLAYING
            #     if event.key == pygame.K_ESCAPE and game_state == GAME_OVER:
            #         run = False
            #     if event.key == pygame.K_SPACE and game_state == PLAYING:
            #         bird_speed = jump_force
            #     if event.key == pygame.K_RETURN:
            #         if game_state == START_SCREEN or game_state == GAME_OVER:
            #             game_state = PLAYING
            #             reset_game()

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].pipe_width:
                pipe_ind = 1
        else:
            run = False
            break

        # jump
        for x, bird in enumerate(birds):
            bird.update()
            ge[x].fitness += 0.1
            output = nets[x].activate(
                (
                    bird.y,
                    abs(bird.y - pipes[pipe_ind].pipe_height),
                    abs(bird.y - pipes[pipe_ind].bottom_pipe_height),
                )
            )

            if output[0] > 0.5:
                bird.jump()

        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[x].fitness -= 2
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.pipe_width < 0:
                rem.append(pipe)

            pipe.update()

        if add_pipe:
            add_pipe = False
            score += 1
            pipes.append(Pipe(500))
            for g in ge:
                g.fitness += 2

        for r in rem:
            pipes.remove(r)
            rem.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.height >= HEIGHT or bird.y <= 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win, birds, pipes, score, gen)


def run(config_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)
