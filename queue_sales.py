from actions_transactions import make_transaction, update_seller_deposit
from classes import Transactions

import json
from threading import Lock

class ShareToSellNode:
    _id = 1

    @classmethod
    def id(cls):
        return cls._id

    @classmethod
    def set_id(cls, value):
        cls._id = value

    def __init__(self, share_name, price, amount, seller_id, node_id=None, next_node=None):
        self._share_name = share_name
        self._price = price
        self._amount = amount
        self._seller_id = seller_id
        self._next_node = next_node

        if node_id is None:
            self.id = ShareToSellNode.id()
            ShareToSellNode._id += 1
        else:
            self.id = node_id


    def __repr__(self):
        return f"Sales transaction ID{self.id}: {self._share_name} {self._amount} {self._price}"

    @property
    def seller_id(self):
        return self._seller_id

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


class SalesShareQueue:
    def __init__(self, share_name, price, amount, seller_id, node_id):
        self.head = ShareToSellNode(share_name, price, amount, seller_id, node_id)
        self.tail = ShareToSellNode(share_name, price, amount, seller_id, node_id)
        self.size = 1

    def get_size(self):
        return self.size
    
    def is_empty(self):
        return self.size == 0

    def enqueue(self, share_name, price, amount, seller_id, node_id):
        new_node = ShareToSellNode(share_name, price, amount, seller_id, node_id)
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


    def del_from_sale_q(self, id):
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


    def someone_buys_shares(self, price, amount, buyer_id):
        made_trades = []
        current_node = self.head
        while current_node and amount > 0:
            if current_node.price <= price:
                if current_node.seller_id == buyer_id:
                    print("Encountered your own shares in the queue. Transaction cannot be processed.")
                    print("You can always go to your portfolio and remove the transaction from the queue.")
                    continue
                if current_node.amount >= amount:
                    trade_value = amount * current_node.price
                    if update_seller_deposit(current_node.seller_id, trade_value):
                        current_node.update_amount(amount)
                        make_transaction(current_node.share_name, amount, current_node.seller_id, buyer_id)
                        new_transaction = Transactions(current_node.share_name, amount, current_node.price, current_node.seller_id, buyer_id)
                        made_trades.append([amount, current_node.price])
                        amount = 0  # Kupienie wszystkich akcji, więc ustawiamy amount na 0

                    if current_node.amount == 0:
                        # Usuwanie węzła, jeśli wszystkie akcje zostały zakupione
                        self.del_from_sale_q(current_node.id)

                    return made_trades
                else:
                    trade_value = current_node.amount * current_node.price
                    if update_seller_deposit(current_node.seller_id, trade_value):
                        make_transaction(current_node.share_name, current_node.amount, current_node.seller_id, buyer_id)
                        new_transaction = Transactions(current_node.share_name, current_node.amount, current_node.price, current_node.seller_id, buyer_id)
                        made_trades.append([current_node.amount, current_node.price])
                        amount -= current_node.amount
                        self.del_from_sale_q(current_node.id)

            current_node = current_node.next_node
        
        return made_trades

    def print_user_sales_requests(self, seller_id):
        user_s_transactions = {}
        current_node = self.head
        while current_node:
            if current_node.seller_id == seller_id:
                user_s_transactions[str(current_node.id)] = [current_node.share_name, current_node.id, current_node.price, current_node.amount]
            current_node = current_node.next_node
        
        return user_s_transactions




class bst_sales:
    def __init__(self, price, amount):
        self.price = price
        self.amount = amount
        self.left = None
        self.right = None

    def __repr__(self):
        return "tree"

    def add_to_sale(self, price, amount):
        if price < self.price:
            if self.left is None:
                self.left = bst_sales(price, amount)
            else:
                self.left.add_to_sale(price, amount)
        elif price == self.price:
            self.amount += amount
        else:
            if self.right is None:
                self.right = bst_sales(price, amount)
            else:
                self.right.add_to_sale(price, amount)

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
        self._inorder_traversal(self, prices)
        print("5 Lowest Prices:")
        for price, amount in prices[:5]:
            print(f"Price: {price}$ - in number: {amount}")

    def _inorder_traversal(self, node, prices):
        if node is not None:
            self._inorder_traversal(node.left, prices)
            prices.append([node.price, node.amount])
            self._inorder_traversal(node.right, prices)

    # I know it's a long comment, but the funckia might be useful one day
    # def remove_zero_amount_nodes(self):
    #     return self._remove_zero_amount_nodes_recursive(self)

    # def _remove_zero_amount_nodes_recursive(self, current_node):
    #     if current_node is None:
    #         return None
        
    #     current_node.left = self._remove_zero_amount_nodes_recursive(current_node.left)
    #     current_node.right = self._remove_zero_amount_nodes_recursive(current_node.right)
        
    #     if current_node.amount == 0:
    #         return self._delete_recursive(current_node)
        
    #     return current_node


class SalesStockMap:
    def __init__(self):
        self.stock_dict = {}
        self.stock_lock = Lock()
        
    def add_sale_to_market(self, share_name, price, amount, seller_id, node_id = None):
        with self.stock_lock:
            if share_name not in self.stock_dict:
                self.stock_dict[share_name] = [SalesShareQueue(share_name, price, amount, seller_id, node_id), bst_sales(price, amount)]
            else:
                share_queue = self.stock_dict[share_name]
                share_queue[0].enqueue(share_name, price, amount, seller_id, node_id)
                share_queue[1].add_to_sale(price, amount)
    
    def del_share_from_market(self, share_name, id, price, amount):
        with self.stock_lock:
            if share_name in self.stock_dict:
                queue = self.stock_dict[share_name]
                queue[0].del_from_sale_q(id)
                queue[1].reduce_quantity(price, amount)
    

    def shares_are_being_sold(self, share_name, price, amount, buyer_id):
        trades_value = 0
        with self.stock_lock:
            if share_name in self.stock_dict:
                queue = self.stock_dict[share_name]
                trades = queue[0].someone_buys_shares(price, amount, buyer_id)
                if trades:
                    for trade in trades:
                        queue[1].reduce_quantity(trade[1], trade[0])
                        amount -= trade[0]
                        trades_value += trade[1] * trade[0]
        
        return amount, trades_value

    def check_sales_requests_state(self, share_name):
        if share_name.upper() in self.stock_dict:
            queue = self.stock_dict[share_name]
            queue[1].list_prices()
        else:
            print("The queue is empty.")

    
    def check_user_sales_requests(self, seller_id):
        s_r_dict = {}  # Inicjalizacja pustego słownika przed pętlą
    
        for share_name, (s_queue, bst) in self.stock_dict.items():
            s_r_dict.update(s_queue.print_user_sales_requests(seller_id))
        
        return s_r_dict


    def save_state(self, filename):
        state_data = {}
        save_id = ShareToSellNode.id()
        state_data["starting_id"] = save_id
        
        for share_name, (queue, bst) in self.stock_dict.items():
            queue_data = []
            current_queue_node = queue.head
            while current_queue_node:
                queue_data.append({
                    "share_name": current_queue_node.share_name,
                    "price": current_queue_node.price,
                    "amount": current_queue_node.amount,
                    "seller_id": current_queue_node.seller_id,
                    "node_id": current_queue_node.id,
                })
                current_queue_node = current_queue_node.next_node
            
            # bst = bst.remove_zero_amount_nodes() # na tym etapie niepotrzebne, ale może się przydać
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
        ShareToSellNode.set_id(starting_id)
        sales_stock_map = cls()

        for share_name, data in json_dict.items():
            if share_name == "starting_id":
                continue

            for node_data in data.get("queue", []):
                share_name = node_data.get("share_name")
                price = node_data.get("price")
                amount = node_data.get("amount")
                user_id = node_data.get("user_id")
                node_id = node_data.get("node_id")
                sales_stock_map.add_sale_to_market(share_name, price, amount, user_id, node_id)

        return sales_stock_map
