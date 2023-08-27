from tcp_connection import conn

import bcrypt
from datetime import datetime
from stock_data import stocks_dict

#user - id("primary key"), name("unique"), password, deposit, frozen_funds
class User:
    def __init__(self, id, name, deposit=10000, frozen_funds=0):
        self.id = id
        self.name = name
        self.deposit = deposit
        self.frozen_funds = frozen_funds
        self.db_password = None  # Przechowujemy zahaszowane hasło tylko w celu weryfikacji
    
    def _set_password(self, password):
        self.db_password = self._hash_password(password)
    
    def _hash_password(self, password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')
    
    def verify_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.db_password.encode('utf-8'))



#SHARE - short_name, company_name #może warto pomysleć o puli akcji - chociaż chyba nie, ktoś musi je sprzedać żeby mo zna bylo je kupić, bot będzie miał ilość, wystarczy
class Share:
    def __init__(self, name, company_name=None):
        self.short_name = name #PRIMARY_KEY
        self.company_name = stocks_dict[name]['company_name']



#TRANSACTIONS - id, stock_short_name, amount, price, value, date, seller_id, buyer_id 
class Transactions:
    def __init__(self, stock_short_name, amount, price, seller_id, buyer_id):
        self.stock_short_name = stock_short_name
        self.amount = amount
        self.price = price
        self.value = amount * price
        self.date = datetime.now().isoformat()
        self.seller_id = seller_id
        self.buyer_id = buyer_id

        # Dodawanie nowego rekordu do tabeli przy inicjacji instancji
        self.add_to_database()

    def add_to_database(self):
        insert_query = "INSERT INTO transactions (stock_short_name, amount, price, value, date, seller_id, buyer_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (self.stock_short_name, self.amount, self.price, self.value, self.date, self.seller_id, self.buyer_id)

        cursor = conn.cursor()
        cursor.execute(insert_query, values)
        conn.commit()