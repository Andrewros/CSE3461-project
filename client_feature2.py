import socket
import threading

HOST = '127.0.0.1'
PORT = 12345


def receive_messages(client):
    while True:
        try:
            msg = client.recv(1024).decode()
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
            client.send(message.encode())
        except:
            break


start_client()