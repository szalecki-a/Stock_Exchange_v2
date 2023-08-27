from classes import User
from tcp_connection import conn
from menus import main_menu
from live_data import logged_in_users

import psycopg2
import sys
import logging

running = True

# Start
def stock_exchange(message_queue, source):
    print('''Welcome to Hashira Exchange, the virtual stock market where you can gain valuable experience in stock trading. \nHappy investing!''')
    if source == "server":
        start_admin(message_queue)
    if source == "client":
        start(message_queue)


# start app
def start(message_queue):
    while True:
        choice = input('''Press:
1 - to login
2 - to create an account
3 - exit\n''')
        
        if choice == "1":
            user_id = login(start, message_queue)
            if user_id in logged_in_users:
                user = logged_in_users[user_id]
                main_menu(user)
            break
        elif choice == "2":
            user_id = create_account(start, message_queue)
            if user_id in logged_in_users:
                user = logged_in_users[user_id]
                main_menu(user)
            break
        elif choice == "3":
            print("Thanks for visiting Hashira Exchange!\n Hope we'll see you soon!")
            break
        else:
            print("Invalid choice. Please select a valid option.")


def create_account(start_func, message_queue):
    while True:
        name = input("Set your account name:\n(type 'return' to go back to the main menu): ")

        if name.lower() == "return":
            return start_func(message_queue)

        if not is_valid_username(name):
            print("Invalid username. Please use only letters and numbers.")
            continue

        if username_exists(name):
            print("Username already exists. Please choose a different username.")
            continue

        password = input("Set your account password (minimum 8 characters long and include letters, numbers, and symbols): ")
        if not is_valid_password(password):
            print("Invalid password. Password must be at least 8 characters long and include letters, numbers, and symbols.")
            continue
        try:
            new_user_id = get_next_user_id()
            user = User(new_user_id, name)
            user._set_password(password)
            
            # Dodawanie użytkownika do bazy danych
            with conn.cursor() as cursor:
                insert_query = "INSERT INTO users (id, name, password, deposit, frozen_funds) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(insert_query, (user.id, user.name, user.db_password, user.deposit, user.frozen_funds))
                conn.commit()
            
            print("Account created successfully!")
            logged_in_users[user.id] = user
            return user.id
        except Exception as e:
            print("An error occurred:", e)



def login(start_func, message_queue):
    while True:
        name = input("Please enter your account name: (type 'return' if you want to return to the start menu): ")
        
        if name.lower() == "return":
            return start_func(message_queue)
        
        password = input("Please enter your password: ")
        
        user = get_user_from_db(name)
        
        if user:
            if user.verify_password(password):
                print("Login successful!\n")
                logged_in_users[user.id] = user
                return user.id
            else:
                print("Invalid password.")
        else:
            print("Username does not exist")
    

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



# helping methods
def get_user_from_db(name):
    try:
        with conn.cursor() as cursor:
            query = "SELECT id, name, password, deposit, frozen_funds FROM users WHERE name = %s"
            cursor.execute(query, (name,))
            db_user = cursor.fetchone()
            
            if db_user is not None:
                user = User(int(db_user[0]), db_user[1], float(db_user[3]), float(db_user[4]))
                user.db_password = db_user[2]
                return user
                
    except Exception as e:
        logging.error("An error occurred while fetching user from DB:", exc_info=True)  # Logging the exception
        print("An error occurred:", e)
    
    return None


def username_exists(username):
    with conn.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM users WHERE name = %s", (username,))
        count = cursor.fetchone()[0]
    return count > 0

def is_valid_username(username):
    return username.isalnum()

def is_valid_password(password):
    min_length = 8
    has_letter = any(c.isalpha() for c in password)
    has_digit = any(c.isdigit() for c in password)
    has_symbol = any(c.isascii() and not c.isalnum() for c in password)
    return len(password) >= min_length and has_letter and has_digit and has_symbol

def get_next_user_id():
    with conn.cursor() as cursor:
        cursor.execute("SELECT MAX(id) FROM users")
        max_id = cursor.fetchone()[0]
    
    return 1 if max_id is None else max_id + 1




def start_admin(message_queue):
    while True:
        choice = input('''Press:
1 - to login
2 - to create an account
3 - exit\n''')
        
        if choice == "1":
            user_id = login(start, message_queue)
            if user_id in logged_in_users:
                user = logged_in_users[user_id]
                main_menu(user)
            break
        elif choice == "2":
            user_id = create_account(start, message_queue)
            if user_id in logged_in_users:
                user = logged_in_users[user_id]
                main_menu(user)
            break
        elif choice == "3":
            print("Thanks for visiting Hashira Exchange!\n Hope we'll see you soon!")
            message_queue.put("SHUTDOWN")
            break
        else:
            print("Invalid choice. Please select a valid option.")