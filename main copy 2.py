import pygame
import sys
import random
import numpy1 as np
import pickle
import os
from draw_objects import draw_pipe
from game_states import start_screen, game_over_screen
import math
from collections import deque


def sigmoid(x):
    """Calculates the sigmoid activation function."""
    return 1 / (1 + math.exp(-x))


# Initialize Pygame
pygame.init()

# Set up the game window
WIDTH, HEIGHT = 400, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
# font_path = "path_to_your_font.ttf"
# font = pygame.font.Font(font_path, 36)

# Set the caption font
pygame.display.set_caption("Flappy Bird")
# pygame.display.set_caption("Flappy Bird", font=font)
BUTTON_WIDTH = 150
BUTTON_HEIGHT = 50

# Assets
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

# Score
score = 0
font = pygame.font.SysFont(None, 50)

# Game states
START_SCREEN = 0
PLAYING = 1
GAME_OVER = 2
game_state = START_SCREEN

# File to store game state and high score
pickle_file = "game_state.pkl"


def collision(pipe):
    """Checks for collision between the bird and a pipe."""
    if bird_x + bird_width > pipe[0] and bird_x < pipe[0] + pipe_width:
        if bird_y < pipe[1] or bird_y + bird_height > pipe[1] + pipe_gap:
            return True

    return False


def save_game_state(highscore):
    """Saves game state and high score to a pickle file."""
    global game_state, score
    if score > highscore:
        data = {"game_state": game_state, "high_score": score}
    else:
        data = {"game_state": game_state, "high_score": highscore}
    with open(pickle_file, "wb") as f:
        pickle.dump(data, f)


def load_game_state():
    """Loads game state and high score from a pickle file (if it exists)."""
    global game_state, score
    try:
        if os.path.exists(pickle_file):
            with open(pickle_file, "rb") as f:
                data = pickle.load(f)
                game_state = data.get("game_state", START_SCREEN)
                score = data.get("high_score", 0)
        else:
            # File doesn't exist, initialize defaults
            game_state = START_SCREEN
            score = 0
    except (Exception, EOFError) as e:
        print("Error occurred while loading game state:", e)
        game_state = START_SCREEN
        score = 0
    return {"game_state": game_state, "high_score": score}


class NeuralNetwork:
    def __init__(self, input_size, hidden_size, output_size):
        self.weights1 = np.random.rand(input_size, hidden_size)
        self.weights2 = np.random.rand(hidden_size, output_size)
        self.bias1 = np.zeros((hidden_size,))
        self.bias2 = np.zeros((output_size,))

    def predict(self, X):
        """Predicts the bird's action (jump or not) based on its state."""
        # Forward pass
        layer1 = np.tanh(X.dot(self.weights1) + self.bias1)
        output = sigmoid(layer1.dot(self.weights2) + self.bias2)
        return output


def reset_game(bird_brain):
    """Resets the game and optionally updates the bird's brain state."""
    bird_state_size = 3
    hidden_size = 4
    output_size = 1
    global bird_y, bird_speed, pipes, score
    bird_y = HEIGHT // 2 - bird_height // 2
    bird_speed = 5
    pipes = []
    score = 0
    # Reset the bird's brain state (optional for some training algorithms)
    # You can implement an update mechanism for the bird's brain here based on
    # its performance during the previous game. For example, you could adjust
    # weights slightly or use more sophisticated reinforcement learning techniques.
    # However, for simplicity, this example keeps the brain state unchanged
    # upon reset.
    # bird_brain.weights1 = np.random.rand(bird_state_size, hidden_size)
    # bird_brain.weights2 = np.random.rand(hidden_size, output_size)


def train_bird(
    bird_brain,
    training_data=None,
    epochs=1000,
    experience_replay=True,
    replay_memory_size=1000,
    gamma=0.9,
    batch_size=32,
):
    """Trains the neural network using provided training data or experience replay."""
    bird_state_size = (
        len(training_data[0][0]) if training_data else 3
    )  # Assuming first element is state (or default 3 for experience replay)
    output_size = 1  # Assuming output is a single jump probability
    learning_rate = 0.1  # Adjust as needed

    if experience_replay:
        replay_memory = deque(maxlen=replay_memory_size)

    for epoch in range(epochs):
        if experience_replay:
            # Sample mini-batch from replay memory (handle empty memory gracefully)
            if len(replay_memory) < batch_size:
                continue
            mini_batch = random.sample(replay_memory, batch_size)
        else:
            # Traditional training using entire training data (if no experience replay)
            mini_batch = training_data

        for state, action, reward, next_state, done in mini_batch:
            # Forward pass
            prediction = bird_brain.predict(state)

            # Calculate error (consider using Huber loss for robustness)
            target = reward
            if not done:
                target += gamma * np.max(
                    bird_brain.predict(next_state)
                )  # Bellman equation
            error = target - prediction

            # Backpropagation to update weights
            d_weights2 = (
                learning_rate
                * error
                * np.outer(
                    state,
                    sigmoid_derivative(
                        bird_brain.weights1.dot(state) + bird_brain.bias1
                    ),
                )
            )
            d_bias2 = (
                learning_rate
                * error
                * sigmoid_derivative(bird_brain.weights1.dot(state) + bird_brain.bias1)
            )

            d_weights1 = (
                learning_rate
                * d_bias2.dot(bird_brain.weights2.T)
                * np.outer(
                    state,
                    sigmoid_derivative(
                        bird_brain.weights1.dot(state) + bird_brain.bias1
                    ),
                )
            )
            d_bias1 = (
                learning_rate
                * d_bias2.dot(bird_brain.weights2.T)
                * sigmoid_derivative(bird_brain.weights1.dot(state) + bird_brain.bias1)
            )

            bird_brain.weights2 += d_weights2
            bird_brain.bias2 += d_bias2
            bird_brain.weights1 += d_weights1
            bird_brain.bias1 += d_bias1

            # Optionally, store the experience in replay memory (for experience replay)
            if experience_replay:
                replay_memory.append((state, action, reward, next_state, done))

    return replay_memory  # Optionally return replay memory for further training


def sigmoid_derivative(x):
    """Calculates the derivative of the sigmoid activation function."""
    return sigmoid(x) * (1 - sigmoid(x))


def main():
    bird_state_size = 3
    bird_brain = NeuralNetwork(bird_state_size, 4, 1)

    train_bird(bird_brain, training_data, epochs=1000, experience_replay=True)
    global bird_y, bird_speed, game_state, score

    game_data = load_game_state()
    game_state = START_SCREEN
    high = game_data["high_score"]
    score = 0
    clock = pygame.time.Clock()
    run = True
    start_button_rect = pygame.Rect(
        WIDTH // 2 - BUTTON_WIDTH // 2, HEIGHT // 2, BUTTON_WIDTH, BUTTON_HEIGHT
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
        # ... event handling (refer to original code)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game_state == START_SCREEN:
                    game_state = PLAYING
                if event.key == pygame.K_ESCAPE and game_state == GAME_OVER:
                    run = False
                if event.key == pygame.K_SPACE and game_state == PLAYING:
                    bird_speed = jump_force
                if event.key == pygame.K_RETURN:
                    if game_state == START_SCREEN or game_state == GAME_OVER:
                        game_state = PLAYING
                        reset_game(bird_brain)

        if game_state == START_SCREEN:
            if high == 0:
                h1 = None
                start_screen(win, WIDTH, HEIGHT, font, frame_counter, h1, 1)
            else:
                start_screen(win, WIDTH, HEIGHT, font, frame_counter, high, 1)
            # Handle mouse clicks on buttons
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if start_button_rect.collidepoint(mouse_x, mouse_y):
                if pygame.mouse.get_pressed()[0]:  # Check left mouse button
                    game_state = PLAYING
                    reset_game(bird_brain)
            elif exit_button_rect.collidepoint(mouse_x, mouse_y):
                if pygame.mouse.get_pressed()[0]:  # Check left mouse button
                    run = False
                    reset_game(bird_brain)
            frame_counter += 1  # Increment the frame counter for animation
            pygame.time.Clock().tick(30)

        elif game_state == PLAYING:
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

            # Create bird state representation
            bird_state = np.array(
                [
                    bird_y / HEIGHT,  # Normalized bird height
                    (pipes[0][0] - bird_x) / WIDTH,  # Distance to next pipe
                    bird_speed,
                ]
            )

            # Get the network's prediction (jump probability)
            jump_probability = bird_brain.predict(bird_state)

            # Decide to jump based on a threshold (e.g., 60% chance)
            if jump_probability > 0.5:
                bird_speed = jump_force

            # Draw everything
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
                reset_game(bird_brain)  # Reset with potential brain state update

        save_game_state(high)

        clock.tick(30)

    try:
        with open("flappy_bird_weights.pkl", "rb") as f:
            bird_brain.weights1 = pickle.load(f)
            bird_brain.weights2 = pickle.load(f)
            bird_brain.bias1 = pickle.load(f)
            bird_brain.bias2 = pickle.load(f)
    except FileNotFoundError:
        print("Weights file not found. Training a new network...")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
