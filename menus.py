from stock_data import stocks_dict
from tcp_connection import conn
from bot import create_bot, bot_random_sell, bot_random_buy
from actions_account import view_deposit, view_trade_history, view_pending_requests
from actions_apps import logout, close_stock_market
from actions_market import show_available_shares, display_stock_details



def main_menu(user):
    while True:
        if user.name == "admin":
            choice = input('''Press:
1 - to check your portfolio
2 - to go to the market
3 - to exit
9 - to bot menu\n''')
        
        else:
            choice = input('''Press:
1 - to check your portfolio
2 - to go to the market
3 - to exit\n''')

        if choice == "1":
            portfolio_menu(user)
            break
        elif choice == "2":
            print("Welcome to the virtual marketplace where you can gain experience in stock trading.")
            market_menu(user)
            break
        elif choice == "3":
            close_stock_market()
            logout(user.id)
        elif choice == "9" and user.name == "admin":
            bot_menu(user)
        else:
            print("Invalid choice. Please select a valid option.")



def bot_menu(user):
    while True:
        if user.name == "admin":
            choice = input('''Select an option:
1 - Make the bot sell shares
2 - Make the bot buy shares
3 - Make the bot perform both selling and buying
4 - Return to the main menu
9 - Create a new bot\n''')

            if choice == "1":
                bot_random_sell()

            elif choice == "2":
                bot_random_buy()

            elif choice == "3":
                bot_random_sell()
                bot_random_buy()
            
            elif choice == "4":
                main_menu(user)

            elif choice == "9" and user.name == "admin":
                create_bot(stocks_dict)

            else:
                print("Invalid choice. Please select a valid option.")
        
        else:
            print("You do not have the authority")
            main_menu(user)
            break



def portfolio_menu(user):
    while True:
        choice = input('''\nPlease choose an option:
1 - to view your deposit
2 - to view your trade history                       
3 - to view pending trade requests
4 - go to the market
5 - exit the program\n''')

        if choice == "1":
            view_deposit(user)
        elif choice == "2":
            view_trade_history(user)
        elif choice == "3":
            view_pending_requests(user)
        elif choice == "4":
            market_menu(user)
        elif choice == "5":
            close_stock_market()
            logout(user.id)
        else:
            print("Invalid choice. Please select a valid option.")



def market_menu(user):
    try:
        with conn.cursor() as cursor:
            query = "SELECT id, stock_short_name, amount, price FROM transactions ORDER BY id DESC LIMIT 5"
            cursor.execute(query)
            last_5_transactions = cursor.fetchall()

        # Display the last 5 transactions
        if last_5_transactions:
            print("Recent transactions:")
            for transaction in last_5_transactions:
                print(f"Stock: {transaction['stock_short_name']}, Amount: {transaction['amount']}, Price: {transaction['price']}")

    except Exception as e:
        print("An error occurred:", e)
    
    while True:
        choice = input('''\nPlease choose an option:
1 - View the list of available shares
2 - Go to your account
3 - Exit the program
Alternatively, enter the action symbol for which you wish to perform more actions: ''')
        if choice == "1":
            show_available_shares(user)
        elif choice == "2":
            portfolio_menu(user)
            break
        elif choice == "3":
            close_stock_market()
            logout(user.id)
        elif choice.upper() in stocks_dict:
            display_stock_details(choice.upper(), user)
        else:
            print("Invalid choice. Please select a valid option.")