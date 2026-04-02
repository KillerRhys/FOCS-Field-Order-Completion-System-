# FOCS - Field Order Completion System

FOCS is a Python and SQLite command-line application for storing and searching completed field work orders. It was built as a practical internal-tool style project to practice CRUD operations, database design, and clean CLI workflows.

## Why I Built This

I built FOCS to create a small but realistic tool based on a field workflow I already understand. Instead of building a toy app, I wanted something that reflected real record-keeping needs while helping me practice Python, SQLite, and structured program design.

## Features

- Create and store completed work orders
- Save data in a local SQLite database
- View all stored work orders
- Search work orders by one or more fields
- Prevent duplicate order numbers
- Run through a simple command-line interface

## Tech Stack

- Python 3
- SQLite3
- Standard library modules:
  - `sqlite3`
  - `os`
  - `datetime`

## Project Structure

```text
FOCS/
├── app.py
├── db.py
├── README.md
├── .gitignore
└── data/
```

## Setup
- Install Python 3.11 or newer
- Clone this repository
- Open the project folder in your terminal

## Run the App
- python app.py

## Commands:
- submit
  Prompts for a new work order and saves it to the database.

- all
  Displays all stored work orders.

- find
  Searches work orders using one or more optional fields.

- help
  Displays the help menu.

- quit
  Exits the application.

## Example Workflow:
```text
Please enter a command: [submit, all, find, help, quit]: submit
Please enter the order number: 751812
Customer's name: Cleveland Brown
Customer's address: 33 Spooner St
Arrival time: 10:52
End time: 12:50
Meter number serviced: 3005671
Corresponding ERT number: 80904566
Current read of unit: 0250
Please enter detailed notes on your work: Rebuilt meter set due to damage.
Work order submitted successfully.
```

## What I Learned
This project helped me practice and improve:

- creating and connecting to a SQLite database
- designing a simple schema for stored records
- writing parameterized SQL inserts
- building dynamic search queries from user input
- separating database logic from application flow
- handling invalid input and duplicate records more cleanly
- organizing Python code into reusable functions and modules

## Future Improvements

Some next-step improvements I may add later include:

- cleaner formatted output for work order records
- stronger validation for times and required fields
- export options for saved work orders
- more flexible search behavior
- additional tables for related data, such as customers or meters

## Notes
FOCS is intentionally small in scope. The goal was not to build a full-field management platform, but to create a clean, practical portfolio project that realistically demonstrates Python, SQLite, and CLI design.
