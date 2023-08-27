from menu_start import stock_exchange

import socket
import threading
from queue import Queue

message_queue = Queue()

def receive_messages(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            print(f"Received: {message}")
        except (ConnectionResetError, ConnectionAbortedError, ConnectionRefusedError):
            print("Connection lost. Exiting...")
            break

def main():
    server_ip = "127.0.0.1"
    server_port = 9999

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_ip, server_port))

    # Proces autentykacji
    password_prompt = client_socket.recv(1024).decode('utf-8')
    print(password_prompt)
    password = input()
    client_socket.send(password.encode('utf-8'))

 

    auth_response = client_socket.recv(1024).decode('utf-8')
    print(auth_response)

    if "Authentication failed" in auth_response:
        print("Exiting...")
        client_socket.close()
        return

    stock_exchange_thread = threading.Thread(target=stock_exchange, args=(message_queue, "client"))
    stock_exchange_thread.start()

    
    # Odbieranie wiadomości w osobnym wątku
    receive_thread = threading.Thread(target=receive_messages, args=(client_socket,))
    receive_thread.start()


if __name__ == "__main__":
    main()
