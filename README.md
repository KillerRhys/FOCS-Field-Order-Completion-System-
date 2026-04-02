Welcome to FOCS: Field Order Completion Systems

FOCS is a small CLI tool to help on-the-go field techs keep track of their own work orders/notes for
their own records. It's not meant to be all-encompassing, but can easily be edited/modified to add the 
fields/data you may need for the role you are working. Maybe someone can find a use for it. This was a 
learning tool that I structured around a modicum of knowledge I've acquired over the last nine years or so.

This was an hour-long project to teach myself some SQL and CRUD methodologies. I chose to build a similar
system I've used for years, so I had a working familiarity to build against.

Simplified work order database & table with beginner-friendly CLI to submit/search orders.

Requirements:
Python 3.11 & SQLite3

Setup:
- install Python 3.11 & SQLlite 3
- clone repo

To Run:
- launch from app.py

FOCS: Commands

- submit - submits an order using a series of prompts all fields must be accounted for!

- all - will query your records and return all stored work orders. 

- find - will use a system of editable prompts to search work orders.

- help - this beautifully designed menu is to the rescue!

- quit - closes out of FOCS after final database check.

This was a small starter project to learn how to execute SQL queries in Python!
