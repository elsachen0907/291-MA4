# Name: Elsa Chen

import sqlite3
import matplotlib.pyplot as plt
import time
import random
# import numpy as np

connection = None
cursor = None
random_PostalCode = None

def multi_bar_chart(values1, values2, values3, labels, title):
    # if lists empty print warning
    if len(values1) < 1 or len(values2) < 1 or len(values3) < 1:
        print('Warning: empty input so generated plot will be empty')

    width = 0.35
    fig, ax = plt.subplots()
    bottoms = [a+b for a,b in zip(values1, values2)]
    ax.bar(labels, values1, width, label="Uninformed")
    ax.bar(labels, values2, width, label="Self-Optimized", bottom=values1)
    ax.bar(labels, values3, width, label="User-Optimized", bottom=bottoms)


    # label x and y axis
    plt.xticks(range(len(labels)), labels)
    plt.legend()

    # give plot a title
    plt.title(title)

    # save plot to file
    # we'll use passed title to give file name
    path = './Q3A3chart.png'
    plt.savefig(path)
    print('Chart saved to file {}'.format(path))

    # close figure so it doesn't display
    plt.close()
    return


def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return


def get_random_PostalCode():
    global random_PostalCode
    cursor.execute('SELECT DISTINCT customer_postal_code FROM Customers')
    rows = cursor.fetchall()
    distinct_postal_code = []
    for i in rows:
        distinct_postal_code.append(i[0])
    random_PostalCode = random.choice(distinct_postal_code)
    return random_PostalCode

def run50_query():
    global connection, cursor
    start = time.time() 
    for i in range(50):
        random_PostalCode = get_random_PostalCode()
        cursor.execute('''SELECT AVG(size) 
    FROM Customers as C, Orders as X, 
    (SELECT O.order_id, COUNT(order_item_id) as size
    FROM Orders as O, Order_items as I 
    WHERE O.order_id = I.order_id 
    GROUP BY O.order_id) as T
    WHERE C.customer_postal_code = :random_postal_code
    AND T.order_id = X.order_id
    AND C.customer_id = X.customer_id;''',{"random_postal_code": random_PostalCode})
    end = time.time()
    result = end - start
    return result
    


# scenario 1
def uninformed():
    global connection, cursor
    # disable the SQLites' auto indexing
    cursor.execute('PRAGMA automatic_index = FALSE;')
    
    # drop all the FK/PKs for all 3 tables
    cursor.execute('''CREATE TABLE IF NOT EXISTS "NewCustomers" (
        "customer_id" TEXT, 
        "customer_postal_code" INTEGER);''')
    cursor.execute('''INSERT INTO NewCustomers SELECT customer_id, customer_postal_code FROM Customers;''')
    cursor.execute('''ALTER TABLE Customers RENAME TO CustomersOri; ''')
    cursor.execute('''ALTER TABLE NewCustomers RENAME TO Customers;''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS "NewOrders" (
        "order_id" TEXT, 
        "customer_id" TEXT);''')
    cursor.execute('''INSERT INTO NewOrders SELECT order_id, customer_id FROM Orders;''')
    cursor.execute('''ALTER TABLE Orders RENAME TO OrdersOri; ''')
    cursor.execute('''ALTER TABLE NewOrders RENAME TO Orders;''')    
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS "NewOrder_items" (
        "order_id" TEXT,
        "order_item_id" INTEGER,
        "product_id" TEXT,
        "seller_id" TEXT);''')
    cursor.execute('''INSERT INTO NewOrder_items SELECT order_id, order_item_id, product_id, seller_id FROM Order_items;''')
    cursor.execute('''ALTER TABLE Order_items RENAME TO Order_itemsOri;''')
    cursor.execute('''ALTER TABLE NewOrder_items RENAME TO Order_items;''')

    # connection.commit()
    return

# scenario 2
def self_optimized():
    global connection, cursor
    # enable the auto-indexing for scenario 2
    cursor.execute('PRAGMA automatic_index = TRUE;')
    cursor.execute('''DROP TABLE Customers;''')
    cursor.execute('''ALTER TABLE CustomersOri RENAME TO Customers;''')

    cursor.execute('''DROP TABLE Orders;''')
    cursor.execute('''ALTER TABLE OrdersOri RENAME TO Orders;''')

    cursor.execute('''DROP TABLE Order_items;''')
    cursor.execute('''ALTER TABLE Order_itemsOri RENAME TO Order_items;''')
       
    # connection.commit()
    return


# scenario 3
def user_optimized():
    global connection, cursor
    cursor.execute('PRAGMA automatic_index = FASLE;')

    cursor.execute('''CREATE TABLE IF NOT EXISTS "NewCustomers" (
        "customer_id" TEXT, 
        "customer_postal_code" INTEGER,
        PRIMARY KEY("customer_id"));''')
    cursor.execute('''INSERT INTO NewCustomers SELECT customer_id, customer_postal_code FROM Customers;''')
    cursor.execute('''ALTER TABLE Customers RENAME TO CustomersOriginal; ''')
    cursor.execute('''ALTER TABLE NewCustomers RENAME TO Customers;''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS "NewOrders" (
        "order_id" TEXT, 
        "customer_id" TEXT, 
        PRIMARY KEY("order_id"));''')
    cursor.execute('''INSERT INTO NewOrders SELECT order_id, customer_id FROM Orders;''')
    cursor.execute('''ALTER TABLE Orders RENAME TO OrdersOriginal; ''')
    cursor.execute('''ALTER TABLE NewOrders RENAME TO Orders;''')    
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS "NewOrder_items" (
        "order_id" TEXT,
        "order_item_id" INTEGER, 
        "product_id" TEXT,	
        "seller_id" TEXT, 
    PRIMARY KEY("order_id", "order_item_id", "product_id", "seller_id"), 
    FOREIGN KEY(seller_id) REFERENCES Sellers(seller_id)
	FOREIGN KEY(order_id) REFERENCES Orders(order_id));''')
    cursor.execute('''INSERT INTO NewOrder_items SELECT order_id, order_item_id, product_id, seller_id FROM Order_items;''')
    cursor.execute('''ALTER TABLE Order_items RENAME TO Order_itemsOriginal;''')
    cursor.execute('''ALTER TABLE NewOrder_items RENAME TO Order_items;''')

    # create the index here
    cursor.execute('CREATE INDEX Idx1 ON  Orders (order_id, customer_id);')
    # cursor.execute('CREATE INDEX Idx2 ON  Orders (customer_id);')
    return

   
def db_uninformed(path):
    global connection, cursor
    connect(path)
    uninformed()
    time_taken = run50_query()
    # uninformed()
    connection.commit()
    connection.close()
    return time_taken

def db_self_optimized(path):
    global connection, cursor
    connect(path)
    # cursor.execute('PRAGMA automatic_index = TRUE')
    self_optimized()
    time_taken = run50_query()
    connection.commit()
    connection.close()
    return time_taken

def db_user_optimized(path):
    global connection, cursor
    connect(path)
    user_optimized()
    time_taken = run50_query()
    connection.commit()
    connection.close()
    return time_taken


def main():
    global connection, cursor
    paths = ["./A3Small.db", "./A3Medium.db", "./A3Large.db"]
    uninformed_time = []
    self_optimized_time = []
    user_optimized_time = []

    for path in paths:
        uninformed_ms = db_uninformed(path) * 1000
        uninformed_time.append(uninformed_ms)
        self_optimized_ms = db_self_optimized(path) * 1000
        self_optimized_time.append(self_optimized_ms)
        user_optimized_ms = db_user_optimized(path) * 1000
        user_optimized_time.append(user_optimized_ms)

    labels = ['SmallDB', 'MediumDB', 'LargeDB']
    
    # use log to plot the y values(reasons explained in README)
    import math
    for i in range(3):
        uninformed_time[i] = math.log(uninformed_time[i] ) 
        self_optimized_time[i] = math.log(self_optimized_time[i] ) 
        user_optimized_time[i] = math.log(user_optimized_time[i] ) 

    # print out the time in log(ms)
    print(uninformed_time)
    print(self_optimized_time)
    print(user_optimized_time)
    multi_bar_chart(uninformed_time, self_optimized_time, user_optimized_time, labels, 'Q3 (Runtime in log(ms))')
    return

if __name__ == "__main__":
    main()