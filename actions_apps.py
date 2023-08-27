from tcp_connection import conn
from queue_purchase import PurchaseStockMap
from queue_sales import SalesStockMap
from live_data import logged_in_users, markets

import sys
import psycopg2


def logout(user_id):
    if user_id in logged_in_users:
        user = logged_in_users.pop(user_id)

        try:
            with conn.cursor() as cursor:
                update_user = "UPDATE users SET deposit = %s, frozen_funds = %s WHERE id = %s"
                cursor.execute(update_user, (user.deposit, user.frozen_funds, user.id))
                conn.commit()
        except psycopg2.DatabaseError as e:
            print("An error occurred:", e)
        
        print("Thanks for visiting Hashira Exchange!\n Hope we'll see you soon!")
        conn.close()
        sys.exit()



# Initiation of the application
def open_stock_market():
   cursor = conn.cursor()
   sales_market =  SalesStockMap().load_state('_json_sales_stock_map_state.json')
   purchase_market = PurchaseStockMap().load_state('_json_purchase_stock_map_state.json')
   markets.append(purchase_market)
   markets.append(sales_market)
   


# Closure of the application
def close_stock_market():
    sales_market = markets[1]
    purchase_market = markets[0]
    try:
        sales_market.save_state('_json_sales_stock_map_state.json')
        purchase_market.save_state('_json_purchase_stock_map_state.json')
    except Exception as e:
        print("An error occurred while saving market states:", e)