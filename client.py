import socket
import threading
def receive_messages(sock):
    while True:
        try:
            message = sock.recv(1024).decode()
            if not message:
                print("Server disconnected.")
                break
            print(message)
        except:
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
while True:
    try:
        msg = input()
        client.send(msg.encode())
    except Exception:
        print("Unable to send. Connection lost.")
        break
client.close()