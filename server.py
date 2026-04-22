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
class ChatServer:
    def __init__(self, host, port):
        self.clients = []
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def handle_client(self, client_socket, client_address):
        while True:
            try:
                data = client_socket.recv(2048).decode('latin-1')
                if not data:
                    break
                if data.startswith('@'):
                    # The server reads the @name but leaves the rest encrypted
                    # Then it sends the whole latin-1 string back out as bytes
                    for c in self.clients:
                        if c != client_socket:
                            c.send(data.encode('latin-1'))
                else:
                    # Normal broadcast for non-routed messages
                    for c in self.clients:
                        if c != client_socket:
                            c.send(data.encode('latin-1'))
                            
            except:
                break
        if client_socket in self.clients:
            self.clients.remove(client_socket)
        client_socket.close()
    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.clients.append(client_socket)
            thread = threading.Thread(
                target=self.handle_client,
                args=(client_socket, client_address)
            )
            thread.start()
server = ChatServer("0.0.0.0", 12345)
server.start()
