import psycopg2

# Tworzenie połączenia do bazy danych
conn = psycopg2.connect(
    host="localhost",
    database="StockExchange",
    user="postgres",
    password="b885d77b"
)

def setup_notification(conn):
    conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    curs = conn.cursor()
    curs.execute("LISTEN channel_name;")
    curs.close()
    conn.commit()
    conn.add_notification_handler(notify_handler)

def notify_handler(event):
    print(f"Received notification: {event.payload}")


# testowanie kodu w tym pliku
if __name__ == "__main__":
    with conn:
        setup_notification(conn)
