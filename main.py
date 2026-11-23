"""Command-line entry point for the Library Management System.

Run the program from the project folder with:

    python main.py

This module only deals with the user interface: printing the menu,
reading input and showing results or error messages. All library rules
live in library.py.
"""

import csv
import sys
from pathlib import Path

from library import Library, LibraryError

# The data folder sits next to this file, so the program works no matter
# which directory it is started from.
DATA_DIR = Path(__file__).resolve().parent / "data"

BOOK_HEADER = (f"{'ISBN':<14} {'Title':<30} {'Author':<22} "
               f"{'Year':<5} Status")
MEMBER_HEADER = f"{'ID':<8} {'Name':<24} {'Email':<30} Loans"
HISTORY_HEADER = (f"{'No.':<5} {'ISBN':<14} {'Member':<8} "
                  f"{'Borrowed':<11} {'Returned':<11} Status")


# ----------------------------------------------------------------------
# Small input/output helpers
# ----------------------------------------------------------------------
def prompt_text(message):
    """Keep asking until the user types something that is not blank."""
    while True:
        answer = input(message).strip()
        if answer:
            return answer
        print("  This field is required. Please try again.")


def print_table(header, items, empty_message):
    """Print a header line and one line per item, or a message if empty."""
    if not items:
        print(empty_message)
        return
    print(header)
    print("-" * len(header))
    for item in items:
        print(item)
    print(f"({len(items)} record(s))")


# ----------------------------------------------------------------------
# One function per menu option
# ----------------------------------------------------------------------
def show_all_books(library):
    """Menu option 1: list the whole catalogue."""
    print_table(BOOK_HEADER, library.get_all_books(),
                "The catalogue is empty.")


def add_book(library):
    """Menu option 2: ask for book details and add the book."""
    isbn = prompt_text("ISBN: ")
    title = prompt_text("Title: ")
    author = prompt_text("Author: ")
    year = prompt_text("Publication year: ")
    book = library.add_book(isbn, title, author, year)
    print(f"Book added: '{book.title}' (ISBN {book.isbn}).")


def search_books(library):
    """Menu option 3: search by title, author, ISBN or any field."""
    field_choices = {"1": "title", "2": "author", "3": "isbn", "4": "all"}
    print("Search by: 1) Title  2) Author  3) ISBN  4) Any field")
    field = field_choices.get(input("Choose 1-4: ").strip())
    if field is None:
        raise ValueError("Please choose a number from 1 to 4.")

    query = prompt_text("Search term: ")
    results = library.search_books(query, field)
    print_table(BOOK_HEADER, results, f"No books matched '{query}'.")


def register_member(library):
    """Menu option 4: ask for member details and register them."""
    member_id = prompt_text("Member ID (e.g. M004): ")
    name = prompt_text("Full name: ")
    email = prompt_text("Email: ")
    member = library.register_member(member_id, name, email)
    print(f"Member registered: {member.name} ({member.member_id}).")


def show_members(library):
    """Menu option 5: list all registered members."""
    print_table(MEMBER_HEADER, library.get_all_members(),
                "No members are registered yet.")


def borrow_book(library):
    """Menu option 6: lend a book to a member."""
    isbn = prompt_text("ISBN of the book: ")
    member_id = prompt_text("Member ID: ")
    record = library.borrow_book(isbn, member_id)
    title = library.find_book(record.isbn).title
    print(f"Success: '{title}' borrowed by {record.member_id} "
          f"(transaction #{record.transaction_id}).")


def return_book(library):
    """Menu option 7: accept a returned book."""
    isbn = prompt_text("ISBN of the book: ")
    member_id = prompt_text("Member ID: ")
    record = library.return_book(isbn, member_id)
    title = library.find_book(record.isbn).title
    print(f"Success: '{title}' returned by {record.member_id} after "
          f"{record.days_on_loan()} day(s).")


def show_history(library):
    """Menu option 8: show all transactions or those of one member."""
    member_id = input("Member ID (press Enter to show everyone): ").strip()
    history = library.get_history(member_id or None)
    print_table(HISTORY_HEADER, history, "No borrowing history found.")


def show_available_books(library):
    """Menu option 9: list only books that can be borrowed now."""
    print_table(BOOK_HEADER, library.get_available_books(),
                "No books are available at the moment.")


# Each menu number maps to (label, function). Option 10 has no function
# because it is handled directly by the menu loop.
MENU_OPTIONS = {
    "1": ("Display all books", show_all_books),
    "2": ("Add a new book", add_book),
    "3": ("Search for a book", search_books),
    "4": ("Register a library member", register_member),
    "5": ("Display all members", show_members),
    "6": ("Borrow a book", borrow_book),
    "7": ("Return a book", return_book),
    "8": ("View borrowing history", show_history),
    "9": ("View available books", show_available_books),
    "10": ("Exit", None),
}
EXIT_CHOICE = "10"


def print_menu():
    """Print the numbered main menu."""
    print("\n========== LIBRARY MENU ==========")
    for number, (label, _) in MENU_OPTIONS.items():
        print(f"{number:>2}. {label}")


def run_menu(library):
    """Show the menu repeatedly until the user chooses to exit.

    Errors raised by a menu option are caught here, so a mistake never
    crashes the program; the user sees a message and the menu again.
    """
    while True:
        print_menu()
        choice = input("Select an option (1-10): ").strip()

        if choice == EXIT_CHOICE:
            print("Goodbye! All changes have been saved.")
            break

        option = MENU_OPTIONS.get(choice)
        if option is None:
            print(f"'{choice}' is not a valid option. "
                  "Please enter a number from 1 to 10.")
            continue

        label, action = option
        print(f"\n--- {label} ---")
        try:
            action(library)
        except LibraryError as error:
            print(f"Error: {error}")
        except ValueError as error:
            print(f"Invalid input: {error}")
        except OSError as error:
            print(f"File error: changes could not be saved ({error}).")


def main():
    """Load the library data and start the menu. Returns an exit code."""
    print("Welcome to the Library Management System")
    try:
        library = Library(DATA_DIR)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Could not load the library data: {error}")
        return 1

    for warning in library.warnings:
        print(f"Warning: {warning}")
    print(f"Loaded {len(library.books)} book(s), {len(library.members)} "
          f"member(s) and {len(library.transactions)} transaction(s).")

    try:
        run_menu(library)
    except (KeyboardInterrupt, EOFError):
        # Ctrl+C or end of input: every change was already saved.
        print("\nProgram closed. All completed changes were saved.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
