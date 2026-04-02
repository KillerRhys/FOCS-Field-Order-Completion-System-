""" Field Order Completion System
    Coded by TechGYQ
    www.mythosworks.com
    OC:2026.03.28-1300 """


# Imports
import db
from datetime import datetime
import sys
import sqlite3
LOGO = r"""
           _____                   _______                   _____                    _____          
         /\    \                 /::\    \                 /\    \                  /\    \         
        /::\    \               /::::\    \               /::\    \                /::\    \        
       /::::\    \             /::::::\    \             /::::\    \              /::::\    \       
      /::::::\    \           /::::::::\    \           /::::::\    \            /::::::\    \      
     /:::/\:::\    \         /:::/~~\:::\    \         /:::/\:::\    \          /:::/\:::\    \     
    /:::/__\:::\    \       /:::/    \:::\    \       /:::/  \:::\    \        /:::/__\:::\    \    
   /::::\   \:::\    \     /:::/    / \:::\    \     /:::/    \:::\    \       \:::\   \:::\    \   
  /::::::\   \:::\    \   /:::/____/   \:::\____\   /:::/    / \:::\    \    ___\:::\   \:::\    \  
 /:::/\:::\   \:::\    \ |:::|    |     |:::|    | /:::/    /   \:::\    \  /\   \:::\   \:::\    \ 
/:::/  \:::\   \:::\____\|:::|____|     |:::|    |/:::/____/     \:::\____\/::\   \:::\   \:::\____\
\::/    \:::\   \::/    / \:::\    \   /:::/    / \:::\    \      \::/    /\:::\   \:::\   \::/    /
 \/____/ \:::\   \/____/   \:::\    \ /:::/    /   \:::\    \      \/____/  \:::\   \:::\   \/____/ 
          \:::\    \        \:::\    /:::/    /     \:::\    \               \:::\   \:::\    \     
           \:::\____\        \:::\__/:::/    /       \:::\    \               \:::\   \:::\____\    
            \::/    /         \::::::::/    /         \:::\    \               \:::\  /:::/    /    
             \/____/           \::::::/    /           \:::\    \               \:::\/:::/    /     
                                \::::/    /             \:::\    \               \::::::/    /      
                                 \::/____/               \:::\____\               \::::/    /       
                                  ~~                      \::/    /                \::/    /        
                                                           \/____/                  \/____/
    Field                       Order                    Completion                System                                                                                                                                                                          
    """


HELP = """
Field Order Completion System Help:
submit - submits an order using a series of prompts all fields must be accounted for!

all - will query your records and return all stored work orders. 

find - will use a system of editable prompts to search work orders.

help - this beautifully designed menu is to the rescue!

quit - closes out of FOCS after final database check.

"""


def main():
    connection = db.connect_db()
    cursor = connection.cursor()
    db.create_work_orders_table(connection, cursor)
    print(LOGO)

    while True:
        try:
            command = input("Please enter a command: [submit, all, find, help, quit]: ").strip().lower()

            if command == "quit":
                connection.close()
                sys.exit()

            elif command == "help":
                print(HELP)

            elif command == "all":
                results = db.fetch_orders(cursor)
                if not results:
                    print("No results!")
                else:
                    print(f"--- {len(results)} Work Orders Found! ---")
                    for result in results:
                        print(result)

            elif command == "submit":
                try:
                    order_number = input("Please enter the order number: ")
                    customer_name = input("Customer's name: ")
                    address = input("Customer's address: ")
                    date = datetime.now().strftime("%Y.%m.%d")
                    arrival_time = input("Arrival time: ")
                    end_time = input("End time: ")
                    meter_number = input("Meter number serviced: ")
                    ert_number = input("Corresponding ERT number: ")
                    read = input("Current read of unit: ")
                    notes = input("Please enter detailed notes on your work: ")

                    db.submit_order(connection, cursor, order_number, customer_name, address, date, arrival_time,
                                    end_time, meter_number, ert_number, read, notes)
                    print("Order submitted!")
                except sqlite3.IntegrityError as duplicate:
                    print(
                        f"\nThis order number is already used in the work orders, please double check and try again!"
                        f" {duplicate}")

            elif command == "find":

                print("Fill in fields to filter by, or leave blank to skip:")

                # 1. Collect all raw inputs into a dictionary

                raw_data = {

                    "order_number": input("Order number: "),

                    "customer_name": input("Customer name: "),

                    "address": input("Address: "),

                    "date": input(f"Date: "),

                    "arrival_time": input("Arrival time: "),

                    "end_time": input("End time"),

                    "meter_number": input("Meter number: "),

                    "ert_number": input("ERT number: "),

                    "read": input("Meter read: "),

                    "notes": input("Tech notes: ")
                }

                # 2. Filter out any keys where the user just pressed Enter (empty string)

                search_criteria = {k: v for k, v in raw_data.items() if v.strip() != ""}

                # 3. Call your dynamic search function

                results = db.data_search(cursor, search_criteria)

                # 4. Display results

                print(f"\n--- Found {len(results)} Matching Work Orders ---")

                for row in results:
                    print(row)

            else:
                print("\nThat is not a valid command. Please choose: submit, all, find, help, or quit.\n")

        except KeyboardInterrupt:
            print("\nExiting FOCS... Goodbye.")
            connection.close()
            break

        except EOFError:
            print("\nExiting FOCS... Goodbye.")
            connection.close()
            break


if __name__ == "__main__":
    main()
