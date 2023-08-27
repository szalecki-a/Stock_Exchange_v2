from random import uniform, randrange, normalvariate
import psycopg2

from tcp_connection import conn, starter, bot
from stock_data import stocks_dict
from classes import User
from live_data import markets

stocks_list = [share for share in stocks_dict.keys()]

def create_stock_share(stocks_dict):
    try:
        with conn.cursor() as cursor:
            for key, value in stocks_dict.items():
                stock_query = "INSERT INTO share (short_name, company_name) VALUES (%s, %s)"
                cursor.execute(stock_query, (key, value["company_name"]))
            conn.commit()
    except Exception as e:
        conn.rollback()
        print("An error occurred:", e)


def create_bot(stocks_dict):
    user = User(bot[0], bot[1], bot[2], bot[3])
    user._set_password(starter)
    
    try:
        with conn.cursor() as cursor:
            user_query = """
                        INSERT INTO users (id, name, password, deposit, frozen_funds)
                        VALUES (%s, %s, %s, %s, %s)
                        ON CONFLICT (id) DO NOTHING
                        RETURNING 'bot already exist' AS message
                    """
            cursor.execute(user_query, (user.id, user.name, user.db_password, user.deposit, user.frozen_funds))

            for symbol in stocks_dict.keys():
                wallet_query = "INSERT INTO wallet_state (user_id, share_name, free_amount, occupied_amount) VALUES (%s, %s, %s, %s)"
                cursor.execute(wallet_query, (user.id, symbol, 1000, 0))
            
            conn.commit()
    
    except Exception as e:
        conn.rollback()
        print("An error occurred:", e)



def bot_random_sell():
    try:
        with conn.cursor() as cursor:
            bot_query = "SELECT id, name, deposit, frozen_funds FROM users WHERE id = %s"
            cursor.execute(bot_query, (bot[0],))
            db_user = cursor.fetchone()
        
            bot_wallet_query = "SELECT share_name, free_amount FROM wallet_state WHERE user_id = %s"
            cursor.execute(bot_wallet_query, (bot[0],))
            bot_wallet = cursor.fetchall()


        if db_user is not None:
            user = User(int(db_user[0]), db_user[1], float(db_user[2]), float(db_user[3]))
        else:
            print("No bot created.")

    except Exception as e:
        print("An error occurred:", e)
    
    bot_shares = {}
    for share in bot_wallet:
        bot_shares[share[0]] = share[1]

    random_share = stocks_list[randrange(0, len(stocks_list))]
    random_number = int(normalvariate(100, 20))
    if random_number < 10:
        random_number = 10

    random_price = round(stocks_dict[random_share]["price"] * normalvariate(1, 0.02), 2)

    sales_market = markets[1]
    sales_market.add_sale_to_market(random_share, random_price, random_number, user.id)
    print(f"BOT added {random_number} of {random_share} to the market by price ${random_price}")




def bot_random_buy():
    try:
        with conn.cursor() as cursor:
            query = "SELECT id, name, deposit, frozen_funds FROM users WHERE name = %s"
            cursor.execute(query, ('Trading_bot',))
            db_user = cursor.fetchone()
        
        if db_user is not None:
            user = User(int(db_user[0]), db_user[1], float(db_user[2]), float(db_user[3]))

    except Exception as e:
        print("An error occurred:", e)
    
    random_share = stocks_list[randrange(0, len(stocks_list))]
    random_price = round(stocks_dict[random_share]["price"] * normalvariate(1, 0.03), 2)
    amount = int(normalvariate(80, 10))
    if amount < 10:
        amount = 10

    purchase_market = markets[0]
    purchase_market.add_purchase_to_market(random_share, random_price, amount, user.id)
    print(f"BOT wants to buy {amount} of {random_share} by price ${random_price}")

    try:
        with conn.cursor() as cursor:
            update_user = "UPDATE users SET deposit = %s, frozen_funds = %s WHERE id = %s"
            cursor.execute(update_user, (user.deposit, user.frozen_funds, user.id))
            conn.commit()
    except psycopg2.DatabaseError as e:
        print("An error occurred:", e)