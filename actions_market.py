from stock_data import stocks_dict, display_stocks
from tcp_connection import conn
from actions_apps import logout, close_stock_market
from live_data import markets


# import close_stock_market
import matplotlib.pyplot as plt
from datetime import datetime, timedelta



def display_stock_details(stock_symbol, user):
    print("\n\nCompany {} ({}) shares.".format(stocks_dict[stock_symbol]['company_name'], stock_symbol))
    try:
        with conn.cursor() as cursor:
            query = "SELECT id, stock_short_name, amount, price FROM transactions WHERE stock_short_name = %s ORDER BY id DESC LIMIT 5"
            cursor.execute(query, (stock_symbol,))
            last_5_stock_transactions = cursor.fetchall()

        # Display the last 5 transactions
        print("Recent transactions:")
        for transaction in last_5_stock_transactions:
            print(f"\nStock: {transaction['stock_short_name']}, Amount: {transaction['amount']}, Price: {transaction['price']}")
        
    except Exception as e:
        print("An error occurred:", e)

    while True:
        choice = input('''
Please choose an option:
1 - View the list of available shares
2 - Check Share Ratio
3 - Buy Share
4 - Sell Share
5 - Check pending purchase requests
6 - Check pending sales requests
7 - Return to Market Menu
8 - Exit program
or enter the action symbol for which you wish to perform more actions: \n''')

        if choice == "1":
            show_available_shares(user)
            break
        elif choice == "2":
            share_ratio(stock_symbol)
        elif choice == "3":
            buy_share(user, stock_symbol)
            break
        elif choice == "4":
            sell_share(user, stock_symbol)
            break
        elif choice == "5":
            purchase_market = markets[0]
            purchase_market.check_purches_requests_state(stock_symbol)
        elif choice == "6":
            sales_market = markets[1]
            sales_market.check_sales_requests_state(stock_symbol)
        elif choice == "7":
            break
        elif choice == "8":
            close_stock_market()
            logout(user.id)
        elif choice.upper() in stocks_dict:
            continue
        else:
            print("Invalid choice. Please select a valid option.")



def share_ratio(share_name):
    while True:
        try:
            time_delta_input = input("Enter the number of days to check for stock ratio (e.g., '30', '7', 'all'), or type 'return' to return to the Share info: ")

            if time_delta_input.lower() == "return":
                display_stock_details(share_name)
                return

            if time_delta_input.lower() == "all":
                start_date = None
            else:
                time_delta = int(time_delta_input)
                start_date = datetime.now() - timedelta(days=time_delta)

            break  # Wyjście z pętli while dotyczącej wyboru przedziału czasowego

        except ValueError:
            print("Invalid input. Please enter a valid number, 'all', or 'menu'.")

    while True:
        plot_choice = input("Do you want to view the ratio as a list or a plot? Type 'list', 'plot', or 'return' to return to the Share info: ")

        if plot_choice.lower() == "return":
            break
        
        elif plot_choice.lower() == "list" or plot_choice.lower() == "plot":
            with conn.cursor() as cursor:
                query = """
                SELECT DATE(date) AS day, 
                    SUM(value) AS total_value, 
                    SUM(amount) AS total_amount
                FROM transactions 
                WHERE stock_short_name = %s
                AND (%s IS NULL OR date >= %s)
                GROUP BY day
                """
                cursor.execute(query, (share_name, start_date, start_date))
                result = cursor.fetchall()

            if plot_choice.lower() == "list":
                generate_list(result)
                break
            else:
                generate_plot(result)
                break

        else:
            print("Invalid choice. Please enter 'list', 'plot', or 'menu'.")



def buy_share(user, stock_symbol):
    print(f"Your current balance is ${user.deposit}.")
    
    while True:
        try:
            quantity_selection = input("Enter the quantity of shares you want to buy (or type 'cancel' to return to the menu): ")
            
            if quantity_selection.lower() == "cancel":
                print("Transaction cancelled.")
                display_stock_details(stock_symbol, user)
                break
            
            quantity_selection = int(quantity_selection)
            
            if quantity_selection <= 0:
                print("Please enter a valid quantity greater than zero.")
                continue

            price_selection = input("Enter the price per share you wish to buy for (or type 'cancel' to return to the menu): ")
            
            if price_selection.lower() == "cancel":
                print("Transaction cancelled.")
                display_stock_details(stock_symbol, user)
                break
            
            price_selection = float(price_selection)
            
            if price_selection <= 0:
                print("Please enter a valid price greater than zero.")
                continue
            
            total_cost = quantity_selection * price_selection
            
            if total_cost > user.deposit:
                print("Insufficient funds. Please enter a valid quantity and price.")
                continue
            
            print("\nIf there are no shares available for sale at or below the selected price,")
            print("your purchase request will be added to the queue.")
            print("Please note that if there are not enough shares available for purchase at the requested price,")
            print("the purchase operation may be executed in parts, if possible.")
            confirm_purchase = input(f"Are you sure you want to purchase {quantity_selection} shares of {stock_symbol} for ${total_cost}? ('yes' to confirm): ")
            
            if confirm_purchase.lower() == "yes":
                # booking founds
                user.deposit -= total_cost
                user.frozen_funds += total_cost

                sales_market = markets[1]
                lefted_amount, purchase_values = sales_market.shares_are_being_sold(stock_symbol, price_selection, quantity_selection, user.id)
                
                if lefted_amount < 0 or purchase_values > user.frozen_funds:
                    print("Error, sold to many shares")
                elif lefted_amount > 0:
                    purchase_market = markets[0]
                    purchase_market.add_purchase_to_market(stock_symbol, price_selection, lefted_amount, user.id)
                user.frozen_funds -= purchase_values
                display_stock_details(stock_symbol, user)
                break
            else:
                print("Purchase cancelled.")
                display_stock_details(stock_symbol, user)
                break

        except ValueError:
            print("Invalid input. Please enter a valid quantity and price.")



def sell_share(user, stock_symbol):
    try:
        with conn.cursor() as cursor:
            select_query = "SELECT user_id, share_name, free_amount, occupied_amount FROM wallet_state WHERE user_id = %s AND share_name = %s"
            cursor.execute(select_query, (user.id, stock_symbol))
            seller_shares = cursor.fetchone()

    except Exception as e:
        print("An error occurred:", e)
    

    if seller_shares is None:
        print(f"\nYou do not own shares in this company.\nBack to {stock_symbol} share menu\n")
        display_stock_details(stock_symbol, user)

    else:
        print(f"In your stock portfolio, you have {seller_shares['free_amount']} available shares and {seller_shares['occupied_amount']} shares in the queue for sale of company {stock_symbol}.")

        while True:
            try:
                quantity_selection = input(f"Enter the quantity of shares you want to sell (or type 'cancel' to return to the menu, or type 'all' to sell all free shares of company {stock_symbol}): ")
                
                if quantity_selection.lower() == "cancel":
                    print("Transaction cancelled.")
                    return
                
                elif quantity_selection.lower() == "all":
                    quantity_selection = int(seller_shares['free_amount'])
                
                else:
                    quantity_selection = int(quantity_selection)
                
                if quantity_selection <= 0:
                    print("Please enter a valid quantity greater than zero.")
                    continue
                
                if quantity_selection > seller_shares['free_amount']:
                    print("Please enter a valid quantity, not exceeding the available shares you have.")
                    continue

                price_selection = input("Enter the price per share you wish to sell for (or type 'cancel' to return to the menu): ")
                
                if price_selection.lower() == "cancel":
                    print("Transaction cancelled.")
                    display_stock_details(stock_symbol, user)
                    break
                
                price_selection = float(price_selection)
                
                if price_selection <= 0:
                    print("Please enter a valid price greater than zero.")
                    continue
                
                total_cost = quantity_selection * price_selection

                print("\nIf there is no demand to buy shares at the selected price,")
                print("the request to sell will be added to the queue.")
                print("Please note that if there is not enough demand to buy the indicated number of shares at the requested price,")
                print("the sell operation can be performed in parts, if possible.")
                confirm_purchase = input(f"Are you sure you want to sell {quantity_selection} shares of {stock_symbol} for ${total_cost}? ('yes' to confirm): ")
                
                if confirm_purchase.lower() == "yes":
                    purchase_market = markets[0]
                    lefted_amount, sales_values = purchase_market.someone_sell_shares(stock_symbol, price_selection, quantity_selection, user.id)
                    
                    if lefted_amount < 0:
                        print("Error, sold to many shares")
                    elif lefted_amount > 0:
                        sales_market = markets[1]
                        sales_market.add_sale_to_market(stock_symbol, price_selection, lefted_amount, user.id)
                    display_stock_details(stock_symbol, user)
                    break
                else:
                    print("Sales cancelled.")
                    display_stock_details(stock_symbol, user)
                    break

            except ValueError:
                print("Invalid input. Please enter a valid quantity and price.")




# helping methods
def show_available_shares(user):
    print("Below is a list of all the available shares on our stock market.")
    display_stocks(stocks_dict)
    
    while True:
        check_stock = input("To find out the details of a specific stock, enter its symbol. Alternatively, press 1 to return to the market menu: ")
        if check_stock == "1":
            break
        elif check_stock.upper() in stocks_dict:
            display_stock_details(check_stock.upper(), user)
            break
        else:
            print("Invalid choice. Please select a valid option.")


def generate_list(result):
    for entry in result:
        print(f"Date: {entry['day']}, Average Price: {entry['total_value'] / entry['total_amount']}, Total Value: {entry['total_value']}, Total Amount: {entry['total_amount']}")



def generate_plot(result):
    dates = [entry['day'] for entry in result]
    total_values = [entry['total_value'] for entry in result]
    total_amounts = [entry['total_amount'] for entry in result]
    average_prices = [entry['total_value'] / entry['total_amount'] for entry in result]

    plt.figure(figsize=(10, 6))
    plt.plot(dates, total_values, label='Total Value')
    plt.plot(dates, total_amounts, label='Total Amount')
    plt.plot(dates, average_prices, label='Average Price')
    plt.xlabel('Date')
    plt.ylabel('Value/Amount')
    plt.title('Stock Ratio Over Time')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

    # Display additional table
    print("\nDate\t\tAverage Price\tTotal Value\tTotal Amount")
    print("----------------------------------------------")
    for entry in result:
        print(f"{entry['day']}\t{entry['total_value'] / entry['total_amount']:.2f}\t\t{entry['total_value']:.2f}\t\t{entry['total_amount']}")