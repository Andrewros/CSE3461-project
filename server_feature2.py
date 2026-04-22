import socket
import threading

HOST = '0.0.0.0'
PORT = 12345

clients = {}  # username -> socket
lock = threading.Lock()


def handle_client(client_socket):
    username = None

    try:
        client_socket.send("Enter username: ".encode())
        username = client_socket.recv(1024).decode().strip()

        with lock:
            if username in clients:
                client_socket.send("Username taken.\n".encode())
                client_socket.close()
                return
            clients[username] = client_socket

        print(f"{username} connected")

        while True:
            message = client_socket.recv(1024).decode().strip()

            if not message:
                break

            # must start with @
            if not message.startswith('@'):
                client_socket.send("Use format: @username message\n".encode())
                continue

            parts = message.split(' ', 1)
            if len(parts) < 2:
                client_socket.send("Invalid format\n".encode())
                continue

            target = parts[0][1:]
            msg = parts[1]

            with lock:
                if target in clients:
                    clients[target].send(f"{username}: {msg}\n".encode())
                else:
                    client_socket.send("User not found\n".encode())

    except:
        pass

    finally:
        if username:
            with lock:
                if username in clients:
                    del clients[username]
        client_socket.close()
        print(f"{username} disconnected")


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print("Server running...")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()


start_server()