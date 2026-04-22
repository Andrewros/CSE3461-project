import socket
import threading

# --- FEATURE 3  ---
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os
aesgcm = AESGCM(b'sixteen_byte_key_sixteen_byte_ky') 

def encrypt_f3(message):
    nonce = os.urandom(12)
    # Convert encrypted bytes to latin-1 string for the network
    return (nonce + aesgcm.encrypt(nonce, message.encode(), None)).decode('latin-1')

def decrypt_f3(latin_str):
    # Convert latin-1 string back to bytes for decryption
    data = latin_str.encode('latin-1')
    return aesgcm.decrypt(data[:12], data[12:], None).decode()
# ------------------------

def receive_messages(sock):
    while True:
        try:
            # Receive raw bytes and decode using latin-1 to preserve binary ciphertext
            raw_data = sock.recv(2048).decode('latin-1')
            
            if not raw_data:
                print("Server disconnected.")
                break
            #check if message follows feature 2 format
            if ": " in raw_data:
                sender, ciphertext = raw_data.split(": ", 1)
                #removes trailing newline and whitespace that may have been added during transmission
                try:
                    clean_ciphertext = ciphertext.strip()
                    message = decrypt_f3(clean_ciphertext)
                    print(f"{sender}: {message}")
                except Exception as e:
                    print(f"{sender} (Encrypted): {ciphertext}")
            else:
                print(raw_data)
        except Exception as e:
            print("Connection closed.")
            break
    sock.close()
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(("127.0.0.1", 12345))
print("Connected to server.")
thread = threading.Thread(
    target=receive_messages,
    args=(client,),
    daemon=True
)
thread.start()
is_logged_in = False
while True:
    try:
        msg = input()
        if not msg: 
            continue
        
        if not is_logged_in:
            client.send(msg.encode('latin-1'))
            is_logged_in = True
        else:
            if msg.startswith('@') and ' ' in msg:
                target, content = msg.split(' ', 1)
                encrypted_content = encrypt_f3(content)
                client.send(f"{target} {encrypted_content}".encode('latin-1'))
            else:
                client.send(encrypt_f3(msg).encode('latin-1'))
    except Exception:
        print("Unable to send. Connection lost.")
        break
client.close()
