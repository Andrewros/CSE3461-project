import socket
import threading
import sys

# --- FEATURE 3 ---
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os

# Must be 16, 24, or 32 bytes
aesgcm = AESGCM(b'sixteen_byte_key_sixteen_byte_ky')

def encrypt_f3(message):
    nonce = os.urandom(12)
    return (nonce + aesgcm.encrypt(nonce, message.encode(), None)).decode('latin-1')

def decrypt_f3(latin_str):
    data = latin_str.encode('latin-1')
    return aesgcm.decrypt(data[:12], data[12:], None).decode()
# ------------------------

HOST = sys.argv[1] if len(sys.argv) > 1 else '127.0.0.1'
PORT = 12345

def receive_messages(sock):
    while True:
        try:
            raw_data = sock.recv(2048).decode('latin-1')

            if not raw_data:
                print("Server disconnected.")
                break

            # Feature 2 format: "sender: ciphertext"
            if ": " in raw_data:
                sender, ciphertext = raw_data.split(": ", 1)
                try:
                    # Direct messages arrive encrypted, so decrypt before printing.
                    clean_ciphertext = ciphertext.strip()
                    message = decrypt_f3(clean_ciphertext)
                    print(f"{sender}: {message}")
                except Exception:
                    print(f"{sender} (Encrypted): {ciphertext}")
            else:
                # Broadcast messages may be encrypted chat text or plain server prompts.
                try:
                    message = decrypt_f3(raw_data.strip())
                    print(message)
                except Exception:
                    # Leave prompts like "Enter username:" untouched.
                    print(raw_data)
        except Exception:
            print("Connection closed.")
            break
    sock.close()
def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect((HOST, PORT))
    print("Connected to server.")

    threading.Thread(
        target=receive_messages,
        args=(client,),
        daemon=True
    ).start()
    is_logged_in = False
    while True:
        try:
            msg = input()
            if not msg:
                continue
            if msg.lower() == 'quit':
                break
            if not is_logged_in:
                # The first input is the username expected by the server.
                client.send(msg.encode('latin-1'))
                is_logged_in = True
            else:
                if msg.startswith('@') and ' ' in msg:
                    # Encrypt only the message body; keep the target username readable.
                    target, content = msg.split(' ', 1)
                    encrypted_content = encrypt_f3(content)
                    client.send(f"{target} {encrypted_content}".encode('latin-1'))
                else:
                    client.send(encrypt_f3(msg).encode('latin-1'))

        except Exception:
            print("Unable to send. Connection lost.")
            break

    client.close()

start_client()
