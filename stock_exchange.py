from tcp_connection import HOST, PORT, start_connections, service_connection, sel
from menu_start import stock_exchange

stock_exchange()

start_connections(HOST, PORT, 5)

while True:
    events = sel.select(timeout=None)
    for key, mask in events:
        if key.data is None:
            continue
        service_connection(key, mask)

