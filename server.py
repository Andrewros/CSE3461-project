import socket
import threading
class ChatServer:
    def __init__(self, host, port):
        self.clients = []
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def handle_client(self, client_socket, client_address):
        while True:
            try:
                message = client_socket.recv(1024)
                if not message:
                    break
                for c in self.clients:
                    if c != client_socket:
                        c.send(message)
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