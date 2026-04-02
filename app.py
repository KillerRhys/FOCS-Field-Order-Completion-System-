""" Field Order Completion System
    Coded by TechGYQ
    www.mythosworks.com
    OC:2026.03.28-1300
"""

import sqlite3
from datetime import datetime

import db

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
Field Order Completion System Help

submit - create and store a new work order
all    - display all stored work orders
find   - search work orders by one or more fields
help   - show this help menu
quit   - exit FOCS
"""


def display_order(row):
    print("-" * 60)
    print(f"Record ID     : {row[0]}")
    print(f"Order Number  : {row[1]}")
    print(f"Customer Name : {row[2]}")
    print(f"Address       : {row[3]}")
    print(f"Date          : {row[4]}")
    print(f"Arrival Time  : {row[5]}")
    print(f"End Time      : {row[6]}")
    print(f"Meter Number  : {row[7]}")
    print(f"ERT Number    : {row[8]}")
    print(f"Meter Read    : {row[9]}")
    print(f"Notes         : {row[10]}")


def display_orders(rows, heading, empty_message="No work orders found."):
    print(f"\n{heading}")
    print("=" * len(heading))

    if not rows:
        print(empty_message)
        return

    print(f"{len(rows)} record(s) found.\n")
    for row in rows:
        display_order(row)
    print("-" * 60)


def main():
    connection = db.connect_db()
    cursor = connection.cursor()
    db.create_work_orders_table(connection, cursor)

    print(LOGO)
    print("Type 'help' to view available commands.\n")

    try:
        while True:
            command = input(
                "Please enter a command: [submit, all, find, help, quit]: "
            ).strip().lower()

            if command == "quit":
                print("Exiting FOCS... Goodbye.")
                break

            elif command == "help":
                print(HELP)

            elif command == "all":
                results = db.fetch_orders(cursor)
                display_orders(results, "All Work Orders")

            elif command == "submit":
                order_number = input("Please enter the order number: ").strip()
                customer_name = input("Customer's name: ").strip()
                address = input("Customer's address: ").strip()
                date = datetime.now().strftime("%Y.%m.%d")
                arrival_time = input("Arrival time: ").strip()
                end_time = input("End time: ").strip()
                meter_number = input("Meter number serviced: ").strip()
                ert_number = input("Corresponding ERT number: ").strip()
                read = input("Current read of unit: ").strip()
                notes = input("Please enter detailed notes on your work: ").strip()

                required_fields = [
                    order_number,
                    customer_name,
                    address,
                    arrival_time,
                    end_time,
                    meter_number,
                    ert_number,
                    read,
                    notes,
                ]

                if any(field == "" for field in required_fields):
                    print("Submission cancelled. All fields are required.")
                    continue

                try:
                    db.submit_order(
                        connection,
                        cursor,
                        order_number,
                        customer_name,
                        address,
                        date,
                        arrival_time,
                        end_time,
                        meter_number,
                        ert_number,
                        read,
                        notes,
                    )
                    print("Work order submitted successfully.")
                except sqlite3.IntegrityError:
                    print("That order number already exists. Please use a unique order number.")
                except sqlite3.Error as error:
                    print(f"Database error: {error}")

            elif command == "find":
                print("Fill in any fields you want to search by. Leave blank to skip.\n")

                raw_data = {
                    "order_number": input("Order number: ").strip(),
                    "customer_name": input("Customer name: ").strip(),
                    "address": input("Address: ").strip(),
                    "date": input("Date (YYYY.MM.DD): ").strip(),
                    "arrival_time": input("Arrival time: ").strip(),
                    "end_time": input("End time: ").strip(),
                    "meter_number": input("Meter number: ").strip(),
                    "ert_number": input("ERT number: ").strip(),
                    "read": input("Meter read: ").strip(),
                    "notes": input("Tech notes: ").strip(),
                }

                search_criteria = {key: value for key, value in raw_data.items() if value != ""}

                if not search_criteria:
                    print("No filters entered. Showing all work orders.")
                    results = db.fetch_orders(cursor)
                    display_orders(results, "All Work Orders")
                else:
                    results = db.data_search(cursor, search_criteria)
                    display_orders(results, "Search Results", "No matching work orders found.")

            else:
                print("That is not a valid command. Please choose: submit, all, find, help, or quit.")

    except KeyboardInterrupt:
        print("\nExiting FOCS... Goodbye.")
    except EOFError:
        print("\nExiting FOCS... Goodbye.")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
