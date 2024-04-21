import socket
import threading
import time

# Server configuration
HOST = "127.0.0.1"
PORT = 5051
counter = 0
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Socket created")

    server.bind((HOST, PORT))
    print("Socket binding to address {} and port {}".format(HOST, PORT))

    server.listen(5)  # Listen for up to 5 incoming connections
    print("Socket listening")

except socket.error as msg:
    print("Error:", msg)
    exit()


# Game state variables
clients_ready = 0
birds = []
birds.append(0)
cli_data_next_count = 1


def re_id(spl, cli_data_next_count):
    spl[-1] = str(cli_data_next_count)
    ret_str = ":".join(spl)
    return ret_str


def re_ready(spl):
    spl[-2] = 2
    ret_str = ":".join(spl)
    return ret_str


def re_message(cli_datas):
    mesaj = ";".join([str(i) for i in cli_datas])
    return mesaj


def handle_client(conn, addr):
    global clients_ready, birds, cli_data_next_count, counter
    while True:
        try:
            userdata = conn.recv(1024).decode("utf-8")
            # name:birdy:ready:id
            spl = userdata.split(":")
            if spl[-2] == "1":
                mesaj = "ready:" + "2"
                conn.send(mesaj.encode("utf-8"))
                clients_ready += 1
            if spl[-1] == "0":
                mesaj = "id:" + str(cli_data_next_count)
                userdata = re_id(spl, cli_data_next_count)
                birds.append(userdata)
                cli_data_next_count += 1
                conn.send(mesaj.encode("utf-8"))
            if clients_ready == len(birds) - 1 and clients_ready > 1:
                conn.send("START".encode("utf-8"))
                if counter > 2:
                    clients_ready = 0
                    counter = 0
                counter += 1
            else:
                birds[int(spl[-1])] = userdata
                print(birds)
                conn.send(re_message(birds).encode("utf-8"))
            if spl[0] == "Byebye":
                birds.pop(int(spl[-1]))
                cli_data_next_count -= 1
                clients_ready -= 1
                print(birds)
            conn.close()

        except Exception as e:
            if "[WinError 10038]" not in str(e):  # Check for WinError code
                cli_data_next_count -= 1
                clients_ready -= 1
                clients_ready = max(clients_ready, 0)
                cli_data_next_count = max(cli_data_next_count, 1)
                print("Players Left - ", cli_data_next_count - 1)
                conn.close()
            if "[WinError 10038]" in str(e):
                clients.remove(addr)


def start_server():
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")
    while True:
        try:
            conn, addr = server.accept()
            print("Connection from:", addr)
            clients.append(addr)
            handle_client(conn, addr)
            print(f"[ACTIVE CONNECTIONS] {len(birds)-1}")
        except:
            pass

# Start the server
if __name__ == "__main__":
    clients = []
    start_server()
