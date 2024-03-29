import socket
import threading

# Server configuration
HOST = "127.0.0.1"
PORT = 5050

# Create a TCP socket
server = socket.socket()
server.bind((HOST, PORT))

# Game state variables
clients_ready = 0
birds = []
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
    global clients_ready, birds,cli_data_next_count

    while True:
        try:
            userdata = conn.recv(1024).decode("utf-8")
            #name:birdy:ready:id
            
            spl = userdata.split(":")
            if spl[-2] == "1":
                clients_ready += 1
                mesaj = "ready:" + 2
                clients_ready += 1
                conn.send(mesaj.encode("utf-8"))

            if spl[-1] == "0":
                mesaj = "id:" + str(cli_data_next_count)
                userdata = re_id(spl, cli_data_next_count)
                #birds.append(userdata)
                cli_data_next_count += 1
                conn.send(mesaj.encode("utf-8"))
                
            if clients_ready == len(birds):
                for client_conn in clients:
                    client_conn.send("START".encode())
            else:
                birds[int(spl[-1])] = userdata
                conn.send(re_message(birds).encode("utf-8"))
                
        except Exception as e:
            print(e)
            break

    conn.close()


def start_server():
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        conn, addr = server.accept()
        clients.append(conn)
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {len(clients)}")


# Start the server
if __name__ == "__main__":
    clients = []
    start_server()
