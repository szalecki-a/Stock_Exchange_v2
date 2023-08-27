from actions_transactions import make_transaction, update_seller_deposit
from classes import Transactions

import json
from threading import Lock

class ShareToBuyNode:
    _id = 1

    @classmethod
    def id(cls):
        return cls._id

    @classmethod
    def set_id(cls, value):
        cls._id = value

    def __init__(self, share_name, price, amount, user_id, node_id = None, next_node=None):
        self._share_name = share_name
        self._price = price
        self._amount = amount
        self._user_id = user_id
        self._next_node = next_node

        if node_id is None:
            self.id = ShareToBuyNode.id()
            ShareToBuyNode._id += 1
        else:
            self.id = node_id

    def __repr__(self):
        return f"Purchase transaction ID{self.id}: {self._share_name} {self._amount} {self._price}"

    @property
    def user_id(self):
        return self._user_id

    @property
    def share_name(self):
        return self._share_name

    @property
    def price(self):
        return self._price

    @property
    def amount(self):
        return self._amount

    @property
    def next_node(self):
        return self._next_node

    @next_node.setter
    def next_node(self, next_node):
        self._next_node = next_node

    def update_amount(self, sale_amount):
        self._amount -= sale_amount


class BuyShareQueue:
    def __init__(self, share_name, price, amount, user_id, node_id):
        init_node = ShareToBuyNode(share_name, price, amount, user_id, node_id)
        self.head = init_node
        self.tail = init_node
        self.size = 1

    def get_size(self):
        return self.size
    
    def is_empty(self):
        return self.size == 0

    def enqueue(self, share_name, price, amount, user_id, node_id):
        new_node = ShareToBuyNode(share_name, price, amount, user_id, node_id)
        if self.is_empty():
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next_node = new_node
            self.tail = new_node
        self.size += 1


    def dequeue(self):
        current_head = self.head
        if self.size == 1:
            self.head = None
            self.tail = None
        else:
            self.head = self.head.next_node
        self.size -= 1
        return current_head


    def del_from_buy_q(self, id):
        current_node = self.head
        if current_node.id == id:
            self.dequeue()
            return current_node.price, current_node.amount
        else:
            next_node = current_node.next_node
            while current_node:
                if next_node.id == id:
                    current_node.next_node = next_node.next_node
                    return
                current_node, next_node = next_node, next_node.next_node
        
        return "Can't find transaction"


    def buying_shares_from_queue(self, price, amount, seller_id):
        made_trades = []
        current_node = self.head
        while current_node and amount > 0:
            if current_node.price <= price:
                if current_node.user_id == seller_id:
                    print("Encountered your own shares in the queue. Transaction cannot be processed.")
                    print("You can always go to your portfolio and remove the transaction from the queue.")
                    continue
                if current_node.amount >= amount:
                    trade_value = amount * current_node.price
                    if update_seller_deposit(seller_id, trade_value):
                        current_node.update_amount(amount)
                        make_transaction(current_node.share_name, amount, seller_id, current_node.user_id)
                        new_transaction = Transactions(current_node.share_name, amount, current_node.price, seller_id, current_node.user_id)
                        made_trades.append([amount, current_node.price])
                        amount = 0  # Kupienie wszystkich akcji, więc ustawiamy amount na 0
                    
                    if current_node.amount == 0:
                        # Usuwanie węzła, jeśli wszystkie akcje zostały zakupione
                        self.del_from_buy_q(current_node.id)
                    
                    return made_trades
                else:
                    trade_value = current_node.amount * current_node.price
                    if update_seller_deposit(seller_id, trade_value):
                        make_transaction(current_node.share_name, current_node.amount, seller_id, current_node.user_id)
                        new_transaction = Transactions(current_node.share_name, current_node.amount, current_node.price, seller_id, current_node.user_id)
                        made_trades.append([current_node.amount, current_node.price])
                        amount -= current_node.amount
                        self.del_from_buy_q(current_node.id)
            
            current_node = current_node.next_node
        
        return made_trades
    

    def print_user_purchase_requests(self, buyer_id):
        user_p_transactions = {}
        current_node = self.head
        while current_node:
            if current_node.user_id == buyer_id:
                user_p_transactions[str(current_node.id)] = [current_node.share_name, current_node.id, current_node.price, current_node.amount]
            current_node = current_node.next_node
        return user_p_transactions
        


class bst_purchase:
    def __init__(self, price, amount):
        self.price = price
        self.amount = amount
        self.left = None
        self.right = None

    def add_to_buy(self, price, amount):
        if price < self.price:
            if self.left is None:
                self.left = bst_purchase(price, amount)
            else:
                self.left.add_to_buy(price, amount)
        elif price == self.price:
            self.amount += amount
        else:
            if self.right is None:
                self.right = bst_purchase(price, amount)
            else:
                self.right.add_to_buy(price, amount)

    def reduce_quantity(self, price, amount):
        if price == self.price:
            self.amount -= amount
            if self.amount == 0:
                return self._delete_recursive(self)

        if price < self.price:
            if self.left is not None:
                self.left = self.left.reduce_quantity(price, amount)
        if price > self.price:
            if self.right is not None:
                self.right = self.right.reduce_quantity(price, amount)
        
        return self

    def _delete_recursive(self, current_node):
        if current_node is None:
            return None

        if current_node.left is None:
            return current_node.right
        elif current_node.right is None:
            return current_node.left
        else:
            min_right_subtree = self._find_min_node(current_node.right)
            current_node.price = min_right_subtree.price
            current_node.amount = min_right_subtree.amount
            current_node.right = self._delete_recursive(current_node.right)

        return current_node

    def _find_min_node(self, node):
        current_node = node
        while current_node.left:
            current_node = current_node.left
        return current_node

    def list_prices(self):
        prices = []
        self._reverse_inorder_traversal(self, prices)
        print("5 Highest Prices:")
        for price, amount in prices[:5]:
            print(f"Price: {price}$ - in number: {amount}")

    def _reverse_inorder_traversal(self, node, prices):
        if node is not None:
            self._reverse_inorder_traversal(node.right, prices)
            prices.append([node.price, node.amount])
            self._reverse_inorder_traversal(node.left, prices)


class PurchaseStockMap:
    def __init__(self):
        self.stock_dict = {}
        self.stock_lock = Lock()

    def add_purchase_to_market(self, share_name, price, amount, user_id, node_id = None):
        with self.stock_lock:
            if share_name not in self.stock_dict:
                self.stock_dict[share_name] = [BuyShareQueue(share_name, price, amount, user_id, node_id), bst_purchase(price, amount)]
            else:
                share_queue = self.stock_dict[share_name]
                share_queue[0].enqueue(share_name, price, amount, user_id, node_id)
                share_queue[1].add_to_buy(price, amount)
    
    def del_share_from_market(self, share_name, id, price, amount):
        with self.stock_lock:
            if share_name in self.stock_dict:
                queue = self.stock_dict[share_name]
                queue[0].del_from_buy_q(id)
                queue[1].reduce_quantity(price, amount)
    

    def someone_sell_shares(self, share_name, price, amount, seller_id):
        trades_value = 0
        with self.stock_lock:
            if share_name in self.stock_dict:
                queue = self.stock_dict[share_name]
                trades = queue[0].buying_shares_from_queue(price, amount, seller_id)
                if trades:
                    for trade in trades:
                        queue[1].reduce_quantity(trade[1], trade[0])
                        amount -= trade[0]
                        trades_value += trade[1] * trade[0]
                
        return amount, trades_value

    def check_purches_requests_state(self, share_name):
        if share_name.upper() in self.stock_dict:
            queue = self.stock_dict[share_name]
            queue[1].list_prices()
        else:
            print("The queue is empty.")


    def check_user_purchase_requests(self, buyer_id):
        p_r_list = {}  # Inicjalizacja pustego słownika przed pętlą
        
        for share_name, (p_queue, bst) in self.stock_dict.items():
            p_r_list.update(p_queue.print_user_purchase_requests(buyer_id))

        return p_r_list


    def save_state(self, filename):
        state_data = {}
        save_id = ShareToBuyNode.id()
        state_data["starting_id"] = save_id
        
        for share_name, (queue, bst) in self.stock_dict.items():
            queue_data = []
            current_queue_node = queue.head
            while current_queue_node:
                queue_data.append({
                    "share_name": current_queue_node.share_name,
                    "price": current_queue_node.price,
                    "amount": current_queue_node.amount,
                    "user_id": current_queue_node.user_id,
                    "node_id": current_queue_node.id,
                })
                current_queue_node = current_queue_node.next_node
            
            bst_data = []
            def traverse_bst(node):
                if node:
                    bst_data.append({
                        "price": node.price,
                        "amount": node.amount,
                    })
                    traverse_bst(node.left)
                    traverse_bst(node.right)
            
            traverse_bst(bst)
            
            state_data[share_name] = {
                "queue": queue_data,
                "bst": bst_data,
            }
        
        with open(filename, 'w') as file:
            json.dump(state_data, file, indent=4)
    

    @classmethod
    def load_state(cls, filename):
        try:
            with open(filename, 'r') as file:
                json_dict = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            json_dict = {}  # pusty słownik, jeśli plik nie istnieje lub jest pusty

        starting_id = json_dict.get("starting_id", 1)
        ShareToBuyNode.set_id(starting_id)
        purchase_stock_map = cls()

        for share_name, data in json_dict.items():
            if share_name == "starting_id":
                continue
            
            for node_data in data.get("queue", []):
                share_name = node_data.get("share_name")
                price = node_data.get("price")
                amount = node_data.get("amount")
                user_id = node_data.get("user_id")
                node_id = node_data.get("node_id")
                purchase_stock_map.add_purchase_to_market(share_name, price, amount, user_id, node_id)
            
        return purchase_stock_map
