import pygame
import random
import numpy1 as np
import tensorflow as tf

# ... other game code (imports, variables, etc.)

# Define the neural network model
model = tf.keras.Sequential(
    [
        tf.keras.layers.Dense(
            8, activation="relu", input_shape=(2,)
        ),  # Hidden layer with 8 neurons
        tf.keras.layers.Dense(
            1, activation="sigmoid"
        ),  # Output layer with sigmoid activation
    ]
)

# ... (other game related imports and definitions)


def calculate_reward(bird_y, pipe_gap, pipe_x, bird_x, score):
    """
    Calculates the reward based on game state.

    Args:
        bird_y (float): Bird's y-coordinate.
        pipe_gap (float): Size of the gap between pipes.
        pipe_x (float): x-coordinate of the next pipe.
        bird_x (float): Bird's x-coordinate.
        score (int): Current game score.

    Returns:
        float: Reward value based on game progress and survival.
    """
    # Reward for staying alive and progressing
    reward = 0.1
    # Bonus reward for passing through a pipe
    if pipe_x - bird_x < -bird_width and score != prev_score:
        reward += 5
    # Penalty for getting too close to the ground or pipes
    if bird_y < bird_height or bird_y > window_height - bird_height:
        reward -= 1
    # Penalty for colliding with pipes
    if abs(bird_x - pipe_x) < bird_width / 2 and (
        bird_y < pipe_height + pipe_gap / 2 or bird_y > pipe_height - pipe_gap / 2
    ):
        reward -= 10
    return reward


def preprocess_states(states):
    """
    Preprocesses the collected game states for network input.

    Args:
        states (list): List of game states (bird positions, pipe information)

    Returns:
        numpy.array: Preprocessed states as a numpy array suitable for the neural network.
    """
    # Normalize or scale states as needed (e.g., normalize bird_y between 0 and 1)
    processed_states = np.array(states)
    # ... (Implement your normalization or scaling logic here)
    return processed_states


def simulate_game(model):
    """
    Simulates a single game using a basic heuristic.

    Args:
        model (tf.keras.Model): The neural network model.

    Returns:
        tuple: A tuple containing the processed game states and the total reward.
    """
    # Initialize game state variables (bird position, pipe information, score, etc.)
    bird_y = window_height // 2
    bird_x = window_width // 3
    pipe_x = window_width + 100
    pipe_height = random.randint(
        bird_height * 2, window_height - pipe_gap - bird_height * 2
    )
    score = 0
    prev_score = 0  # Track previous score for pipe passing reward
    game_over = False

    states = []  # List to store game states

    while not game_over:
        # ... (Implement your game logic here: move bird, generate pipes, handle collisions, update score)

        # Get inputs for the neural network based on current game state
        inputs = [
            bird_y,
            pipe_gap,
            pipe_x - bird_x,
        ]  # You can add more inputs if needed
        states.append(inputs)

        # Get the network prediction for jumping
        prediction = model.predict(np.expand_dims(inputs, axis=0))[0][0]
        should_jump = prediction > 0.5  # Threshold for jumping

        # Apply jump based on network prediction
        if should_jump:
            bird_y += jump_force

        # Calculate reward based on current game state
        reward = calculate_reward(bird_y, pipe_gap, pipe_x, bird_x, score)

        # Update game over flag if collision happens
        game_over = (
            bird_y < 0
            or bird_y > window_height
            or abs(bird_x - pipe_x) < bird_width / 2
            and (
                bird_y < pipe_height + pipe_gap / 2
                or bird_y > pipe_height - pipe_gap / 2
            )
        )
        prev_score = score  # Update previous score for next iteration

    return preprocess_states(states), sum(
        reward
    )  # Return preprocessed states and total reward


def calculate_loss(predictions, reward):
    """
    Calculates the loss based on network predictions and reward.

    Args:
        predictions (numpy.array): Network predictions for each state during game simulation.
        reward (float): Total reward accumulated during the simulated game.

    Returns:
        float: Loss value based on the difference between predicted rewards and actual reward.
    """
    # Implement a suitable loss function based on your reward structure
    # Here, we use mean squared error between the predicted reward on each step
    # and a discounted future reward based on the actual reward at the end of the game.

    discount_rate = 0.9  # Discount factor for future rewards

    discounted_future_reward = 0
    losses = []
    for prediction in predictions[::-1]:  # Iterate through predictions in reverse order
        discounted_future_reward = reward + discount_rate * discounted_future_reward
        loss = tf.square(
            prediction - discounted_future_reward
        )  # MSE between prediction and discounted reward
        losses.append(loss)

    return tf.reduce_mean(losses)  # Calculate mean squared error across all losses


def train_model(model, learning_rate):
    optimizer = tf.keras.optimizers.Adam(learning_rate=learning_rate)

    # Training loop
    for epoch in range(num_epochs):
        total_reward = 0
        for _ in range(games_per_epoch):
            states, reward = simulate_game(model)
            total_reward += reward

            with tf.GradientTape() as tape:
                # Get network predictions for all states encountered during the simulation
                predictions = model.predict(states)

                # Calculate loss using the reward and predictions
                loss = calculate_loss(predictions, reward)

            # Backpropagate the loss to update network weights
            gradients = tape.gradient(loss, model.trainable_variables)
            optimizer.apply_gradients(zip(gradients, model.trainable_variables))

        print(f"Epoch: {epoch+1}, Average Reward: {total_reward / games_per_epoch}")


# ... (rest of your game code)

# Training parameters
learning_rate = 0.001
num_epochs = 100
games_per_epoch = 100

train_model(model, learning_rate)

# Save the trained model weights for future use
model.save_weights("flappy_bird_weights.h5")


def get_bird_inputs(bird_y, bird_x, pipe_gap, pipe_height, pipe_x):
    center_of_gap = pipe_gap / 2
    position_of_center_of_gap = pipe_height + center_of_gap
    vertical_distance = abs(bird_y - position_of_center_of_gap)
    distance_to_gap = pipe_x - bird_x

    return [distance_to_gap, vertical_distance]  # Replace with actual calculations


def make_move(bird_y, bird_x, pipe_gap, pipe_height, pipe_x):
    inputs = get_bird_inputs(bird_y, bird_x, pipe_gap, pipe_height, pipe_x)
    prediction = model.predict(tf.expand_dims(inputs, axis=0))[0][0]
    should_jump = prediction > 0.5  # Threshold for jumping
    return should_jump


"""
//runner 
  if should_jump:
    bird_y += jump_force  # Apply jump force if the network suggests jumping
  else:
    bird_y += bird_speed
"""
