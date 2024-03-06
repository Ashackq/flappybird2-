'''
import pygame
import socket
import threading
#import pickle
from main import main 
import time

# Server configuration
SERVER = '127.0.0.1'
PORT = 5050

# Socket initialization
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((SERVER, PORT))

# Function to read data from the pickle file and display it
def display_data():
    while True:
        try:
            with open("game_state.pkl", 'rb') as f:
                data = pickle.load(f)
                game_state = data.get('game_state')
                high_score = data.get('high_score')
                print(f"Game State: {game_state}, High Score: {high_score}")
        except FileNotFoundError:
            print("Pickle file not found.")
        time.sleep(5)

# Start a separate thread to continuously display data
display_thread = threading.Thread(target=display_data)
display_thread.daemon = True
display_thread.start()

# Call the main function to start the game
main()

# Close the socket connection after the game ends
client.close()
'''