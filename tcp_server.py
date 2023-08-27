from admin_secrets import server_secret
from menu_start import stock_exchange
from actions_apps import open_stock_market, close_stock_market

import socket
import threading
import atexit
import signal
from queue import Queue
import time

running = True
clients = []
MAX_CLIENTS = 20
message_queue = Queue()

def close_server():
    global running
    running = False  # Zmiana wskaźnika
    print("Server is shutting down.")

def signal_handler(signal, frame):
    print("Received signal to shut down.")
    close_server()

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)



def handle_client(client_socket):
    global clients
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            broadcast(message, client_socket)
    except (OSError, ConnectionResetError):
        print("Connection lost or error occurred.")
    finally:
        clients.remove(client_socket)
        client_socket.close()

def broadcast(message, sending_client):
    for client in clients:
        if client != sending_client:
            try:
                client.send(message.encode('utf-8'))
            except (OSError, ConnectionResetError):
                print("Failed to send message, closing client socket.")
                client.close()
                clients.remove(client)

def authenticate(client_socket):
    client_socket.send("Please enter the server password: ".encode('utf-8'))
    password = client_socket.recv(1024).decode('utf-8')
    return password == server_secret

def main():
    global clients, running

    stock_exchange_thread = threading.Thread(target=stock_exchange, args=(message_queue, "server"))
    stock_exchange_thread.start()

    server_ip = "0.0.0.0"
    server_port = 9999

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((server_ip, server_port))
    server.listen(MAX_CLIENTS)
    server.settimeout(1)

    print(f"Listening on {server_ip}:{server_port}")

    while running:
        try:
            client_socket, addr = server.accept()
            if authenticate(client_socket):
                clients.append(client_socket)
                print(f"Authenticated connection from {addr}")
                client_thread = threading.Thread(target=handle_client, args=(client_socket,))
                client_thread.start()
            else:
                print(f"Failed authentication from {addr}")
                client_socket.send("Authentication failed.".encode('utf-8'))
                client_socket.close()
        except socket.timeout:
            pass 

        # Sprawdzam, czy w kolejce są jakieś wiadomości
        if not message_queue.empty():
            message = message_queue.get()
            if message == "SHUTDOWN":
                print("Received shutdown command. Shutting down...")
                running = False  # zmiana wskaźnika, aby zakończyć pętlę

    # Zamykam wszystkie połączenia i sockety serwera
    for client in clients:
        client.close()
    server.close()



if __name__ == "__main__":
    atexit.register(close_stock_market)
    open_stock_market()
    main()