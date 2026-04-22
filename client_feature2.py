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
HOST = '127.0.0.1'
PORT = 12345


def receive_messages(client):
    while True:
        try:
            raw_data = client.recv(1024)
            if not raw_data:
                break
            msg = decrypt_f3(raw_data)
            print(msg)
        except:
            break


def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()

    while True:
        try:
            message = input()
            if message.lower() == 'quit': break
            encrypted_payload = encrypt_f3(message) 
            client.send(encrypted_payload)
        except:
            break


start_client()
