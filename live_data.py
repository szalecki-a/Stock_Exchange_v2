logged_in_users = {}

markets = []


from threading import Lock
sales_market_lock = Lock()
purchase_market_lock = Lock()

def access_sales_market(func):
    def wrapper(*args, **kwargs):
        with sales_market_lock:
            return func(*args, **kwargs)
    return wrapper

def access_purchase_market(func):
    def wrapper(*args, **kwargs):
        with purchase_market_lock:
            return func(*args, **kwargs)
    return wrapper