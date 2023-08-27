from tcp_connection import conn
from live_data import logged_in_users

import psycopg2



def make_transaction(share_name, amount, seller_id, buyer_id):
    try:
        with conn.cursor() as cursor:
            # Select the current amount of shares for the seller and buyer
            select_query = "SELECT user_id, share_name, free_amount, occupied_amount FROM wallet_state WHERE user_id = %s AND share_name = %s"
            cursor.execute(select_query, (seller_id, share_name))
            seller_shares = cursor.fetchone()
            
            cursor.execute(select_query, (buyer_id, share_name))
            buyer_shares = cursor.fetchone()
            
            if seller_shares is None:
                raise ValueError("Seller shares not found.")
            
            if buyer_shares is None:
                buyer_shares = {'free_amount': 0, 'occupied_amount': 0}
            
            # Calculate the new amounts after the transaction
            new_seller_occupied_amount = seller_shares['occupied_amount'] - amount
            new_buyer_free_amount = buyer_shares['free_amount'] + amount
            
            # Update the database with the new amounts
            update_query_seller = "UPDATE wallet_state SET occupied_amount = %s WHERE user_id = %s AND share_name = %s"
            update_query_buyer = "UPDATE wallet_state SET free_amount = %s WHERE user_id = %s AND share_name = %s"
            cursor.execute(update_query_seller, (new_seller_occupied_amount, seller_id, share_name))
            cursor.execute(update_query_buyer, (new_buyer_free_amount, buyer_id, share_name))
            
            # Commit the transaction
            conn.commit()
    
    except Exception as e:
        print("An error occurred:", e)



def update_seller_deposit(seller_id, value):
    if seller_id in logged_in_users:
        seller = logged_in_users[seller_id]
        seller.deposit += value
        return True
    else:
        try:
            with conn:
                with conn.cursor() as cursor:
                    select_query = "SELECT id, deposit FROM users WHERE id = %s"
                    cursor.execute(select_query, (seller_id,))
                    seller_deposit = cursor.fetchone()
                    new_seller_deposit = seller_deposit['deposit'] + value
                    update_query = "UPDATE users SET deposit = %s WHERE id = %s"
                    cursor.execute(update_query, (new_seller_deposit, seller_id))
                conn.commit()
            return True
        except psycopg2.DatabaseError as e:
            print("An error occurred:", e)
            return False