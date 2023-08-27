from tcp_connection import conn
from live_data import markets

           
def view_deposit(user):
    print(f"\nMoney wallet:   you have ${user.deposit} of free money and ${user.frozen_funds} of frozen money (queued to buy shares).")
    check_portfolio(user)


def view_trade_history(user):
    check_history(user)


def view_pending_requests(user):
    p_dict, s_dict = check_requests(user)
    if len(p_dict) != 0 or len(s_dict) != 0:
        del_req = input("\nType 'del' if you want to remove a request from the queue, to continue type anything else: ")
        if del_req == "del":
            handle_request_deletion(p_dict, s_dict, user)


def handle_request_deletion(p_dict, s_dict, user):
    print("\nWhat type of request do you want to remove.")
    print("Press 'p' to delete a purchase request, 's' to delete a sell request,")
    req_type = input("type 'all' to delete all your requests, or type 'cancel' to cancel deleting a transaction request: ")

    if req_type == "cancel":
        print("Deleting a transaction request canceled")
    
    elif req_type == "p":
        purchase_market = markets[0]
        delete_single_requests(p_dict, purchase_market, user)
    elif req_type == "s":
        sales_market = markets[1]
        delete_single_requests(s_dict, sales_market, user)
    elif req_type == "all":
        purchase_market = markets[0]
        sales_market = markets[1]
        delete_all_requests(p_dict, s_dict, purchase_market, sales_market, user)
    else:
        print("Invalid choice. Please select a valid option.")


def delete_single_requests(request_dict, market, user):
    while True:
        req_to_del = input("Enter the request ID you want to delete (or type 'cancel' to cancel deleting a transaction request): ")
        if req_to_del in request_dict:
            req_data = request_dict[req_to_del]
            market.del_share_from_market(req_data[0], req_data[1], req_data[2], req_data[3])
            restore_fozen_funds(user, req_data[2] * req_data[3])
            break
        elif req_to_del == "cancel":
            print("Deleting a transaction request canceled")
            break
        else:
            print("Invalid input. Please enter a valid ID.")


def delete_all_requests(p_dict, s_dict, purchase_market, sales_market, user):
    unfrezzing_funds = 0
    if s_dict:
        for request_data in s_dict.values():
            sales_market.del_share_from_market(request_data[0], request_data[1], request_data[2], request_data[3])
    if p_dict:
        for request_data in p_dict.values():
            purchase_market.del_share_from_market(request_data[0], request_data[1], request_data[2], request_data[3])
            unfrezzing_funds += request_data[2] * request_data[3]
        restore_fozen_funds(user, unfrezzing_funds)
    

def restore_fozen_funds(user, unfrezzing_funds):
    if user.frozen_funds >= unfrezzing_funds:
        user.frozen_funds -= unfrezzing_funds
        user.deposit += unfrezzing_funds
        print(f"The ${unfrezzing_funds} has been unfrozen and returned to your deposit")


def check_portfolio(user):
    with conn.cursor() as cursor:
        query = "SELECT user_id, share_name, free_amount, occupied_amount FROM wallet_state WHERE user_id = %s"
        cursor.execute(query, (user.id,))
        result = cursor.fetchall()
    
    if len(result) == 0:
        print(f"Shares wallet:   You do not own any shares.\n")
    
    else:
        print("Shares wallet:")
        for share in result:
            if share[3] > 0:
                print(f"{share[1]}:   {share[2] + share[3]} ({share[3]} in queue for sale.)")
            else:
                print(f"{share[1]}:   {share[2]}")


def check_history(user):
    try:
        with conn.cursor() as cursor:
            purchase_transactions = "SELECT stock_short_name, amount, price, value, date, buyer_id FROM transactions WHERE buyer_id = %s"
            sales_transactions = "SELECT stock_short_name, amount, price, value, date, seller_id FROM transactions WHERE seller_id = %s"
            cursor.execute(purchase_transactions, (user.id,))
            purchase = cursor.fetchall()

            cursor.execute(sales_transactions, (user.id,))
            sales = cursor.fetchall()
    
    except Exception as e:
        print("An error occurred:", e)
        return
    
    print("- purchase history:")
    if not purchase:
        print("You haven't bought any shares yet.")
    else:
        print("\nShare symbol\t\tValue\tPrice\tTotal Amount\tDate")
        print("----------------------------------------------")
        for entry in purchase:
            print(f"{entry[0]}\t\t{entry[3]}\t{entry[2]}\t\t{entry[1]}\t\t{entry[4]}")
    
    print("\n- sales history:")
    if not sales:
        print("You haven't sold any shares yet.\n")
    else:
        print("\nShare symbol\t\tValue\tPrice\tTotal Amount\tDate")
        print("----------------------------------------------")
        for entry in sales:
            print(f"{entry[0]}\t\t{entry[3]}\t{entry[2]}\t\t{entry[1]}\t\t{entry[4]}")


def check_requests(user):
    purchase_market = markets[0]
    p_dict = purchase_market.check_user_purchase_requests(user.id)
    if len(p_dict) == 0:
        print("You have no purchase requests in the queue.")
    else:
        print("Your purchase requests:")
        for purchase_request_id, purchase_request_data in p_dict.items():
            print(f"Purchase request ID - {purchase_request_data[1]}:    Share: {purchase_request_data[0]}    Number of shares: {purchase_request_data[3]}    Price: {purchase_request_data[2]}")

    sales_market = markets[1]
    s_dict = sales_market.check_user_sales_requests(user.id)
    if len(s_dict) == 0:
        print("\nNone of your shares are queued up for sale")
    else:
        print("\nYour sales requests:")
        for sale_request_id, sale_request_data in p_dict.items():
            print(f"Sale request ID - {sale_request_data[1]}:    Share: {sale_request_data[0]}    Number of shares: {sale_request_data[3]}    Price: {sale_request_data[2]}")

    return p_dict, s_dict