import socket
import threading

# --- FEATURE 3  ---
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
aesgcm = AESGCM(b'sixteen_byte_key_sixteen_byte_ky') 

def encrypt_f3(message):
    nonce = os.urandom(12)
    return nonce + aesgcm.encrypt(nonce, message.encode(), None)

def decrypt_f3(data):
    return aesgcm.decrypt(data[:12], data[12:], None).decode()
# ------------------------
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
            raw_data = client_socket.recv(1024).decode('latin-1').strip()
            if not raw_data:
                break
            # DEMONSTRATION LOG: Proof that the server sees ciphertext, not plaintext.
            print(f"SERVER LOG: Intercepted raw data -> {raw_data}")
            message = raw_data

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
            encrypted_msg = parts[1]

            with lock:
                if target in clients:
                    final_payload = f"{username}: {encrypted_msg}\n"
                    clients[target].send(final_payload.encode('latin-1'))
                else:
                    client_socket.send("User not found\n".encode())

    except Exception as e:
        print(f"Error occurred: {e}")
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
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen()

    print("Server running...")

    while True:
        client_socket, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()


start_server()
