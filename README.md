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
