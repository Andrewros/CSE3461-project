import socket
import threading
import sys

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
class ChatServer:
    def __init__(self, host, port):
        self.clients = []              # list of sockets for broadcast
        self.client_map = {}           # username -> socket for feature 2
        self.lock = threading.Lock()
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    def handle_client(self, client_socket, client_address):
        username = None
        try:
            # First message from each client is treated as the username.
            client_socket.send("Enter username: ".encode())
            username = client_socket.recv(1024).decode().strip()
            with self.lock:
                if username in self.client_map:
                    client_socket.send("Username taken.\n".encode())
                    client_socket.close()
                    return
                self.client_map[username] = client_socket
            print(f"{username} connected")
            while True:
                data = client_socket.recv(2048).decode('latin-1')
                if not data:
                    break
                data = data.strip()
                print(f"SERVER LOG: Intercepted raw data -> {data}")

                if data.startswith('@'):
                    # Direct messages use "@user encrypted_text".
                    parts = data.split(' ', 1)
                    if len(parts) < 2:
                        client_socket.send("Invalid format\n".encode())
                        continue

                    target = parts[0][1:]
                    encrypted_msg = parts[1]

                    with self.lock:
                        if target in self.client_map:
                            final_payload = f"{username}: {encrypted_msg}\n"
                            self.client_map[target].send(final_payload.encode('latin-1'))
                        else:
                            client_socket.send("User not found\n".encode())
                else:
                    # Anything else is broadcast to every other connected client.
                    with self.lock:
                        for c in self.clients:
                            if c != client_socket:
                                c.send(data.encode('latin-1'))
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            with self.lock:
                if client_socket in self.clients:
                    self.clients.remove(client_socket)
                if username and username in self.client_map:
                    del self.client_map[username]

            client_socket.close()
            print(f"{username} disconnected")

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print("Server running...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            with self.lock:
                self.clients.append(client_socket)
            # Each client gets its own thread so multiple users can chat at once.
            thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, client_address)
            )
            thread.start()
host = sys.argv[1] if len(sys.argv) > 1 else "0.0.0.0"
server = ChatServer(host, 12345)
server.start()
