import socket
import threading
import pickle
import random

# Server configuration
HOST = '127.0.0.1'
PORT = 5050

# Create a TCP socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

# Game state
bird_width = 40
bird_height = 30
bird_x = 50
bird_y = 300
bird_speed = 5
gravity = 0.25
jump_force = -7
pipe_width = 70
pipe_gap = 150
pipe_speed = 3
pipes = []
score = 0

def generate_pipes():
    if len(pipes) == 0 or pipes[-1]['x'] < 400 - pipe_gap * 2:
        pipe_height = random.randint(100, 400 - pipe_gap - 100)
        pipes.append({'x': 400, 'y': pipe_height})

def move_pipes():
    for pipe in pipes:
        pipe['x'] -= pipe_speed

def check_collision():
    global score
    for pipe in pipes:
        if bird_x + bird_width > pipe['x'] and bird_x < pipe['x'] + pipe_width:
            if bird_y < pipe['y'] or bird_y + bird_height > pipe['y'] + pipe_gap:
                return True
        if pipe['x'] + pipe_width < 0:
            pipes.remove(pipe)
            score += 1
    return False

def handle_client(conn, addr):
    global bird_y, score, pipes
    print(f"[NEW CONNECTION] {addr} connected.")

    while True:
        try:
            data = conn.recv(1024).decode()
            if not data:
                print(f"[{addr}] disconnected.")
                break

            if data == "JUMP":
                bird_y += jump_force

            generate_pipes()
            move_pipes()

            game_state = {'bird_y': bird_y, 'pipes': pipes, 'score': score}
            game_state_data = pickle.dumps(game_state)
            conn.send(game_state_data)

            if check_collision():
                bird_y = 300
                pipes = []
                score = 0

        except Exception as e:
            print(e)
            break

    conn.close()

def start_server():
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

if __name__ == "__main__":
    start_server()