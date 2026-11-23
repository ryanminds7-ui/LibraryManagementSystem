"""The Library class: manages books, members, loans and CSV persistence.

Library is the "controller" of the application. The menu in main.py only
talks to Library; Library in turn creates and updates Book, Member and
Transaction objects and saves them through the storage module.
"""

from datetime import date
from pathlib import Path

from book import SEARCH_FIELDS, Book
from member import Member
from storage import backup_file, load_rows, save_rows
from transaction import Transaction
from validation import normalise_isbn, require_text, validate_member_id

BOOK_FIELDS = ["isbn", "title", "author", "year", "available"]
MEMBER_FIELDS = ["member_id", "name", "email", "borrowed_isbns"]
TRANSACTION_FIELDS = ["transaction_id", "isbn", "member_id",
                      "borrow_date", "return_date"]


class LibraryError(Exception):
    """Raised when an operation breaks a library rule.

    Examples: borrowing a book that is on loan, registering a duplicate
    member ID, or returning a book the member never borrowed.
    """


class Library:
    """Coordinates every library operation and keeps the CSV files updated.

    Attributes:
        data_dir (Path): Folder containing the three CSV files.
        books (dict[str, Book]): Books indexed by ISBN.
        members (dict[str, Member]): Members indexed by member ID.
        transactions (list[Transaction]): Full borrowing history.
        warnings (list[str]): Problems found while loading the CSV files.
    """

    BOOKS_FILE = "books.csv"
    MEMBERS_FILE = "members.csv"
    TRANSACTIONS_FILE = "transactions.csv"

    def __init__(self, data_dir):
        """Create the library and load any saved data from data_dir."""
        self.data_dir = Path(data_dir)
        self.books = {}
        self.members = {}
        self.transactions = []
        self.warnings = []
        self.load_data()

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    def load_data(self):
        """Load books, members and transactions from the CSV files.

        Missing files are created and empty files give empty collections.
        Invalid rows are skipped and described in self.warnings, so one
        bad line does not stop the whole program from starting.

        Raises:
            ValueError: If a file is missing a required column.
            OSError: If a file cannot be read.
        """
        self.warnings = []
        books = self._load_objects(self.BOOKS_FILE, BOOK_FIELDS,
                                   Book.from_dict)
        members = self._load_objects(self.MEMBERS_FILE, MEMBER_FIELDS,
                                     Member.from_dict)
        self.books = self._index_unique(books, "isbn", self.BOOKS_FILE)
        self.members = self._index_unique(members, "member_id",
                                          self.MEMBERS_FILE)
        self.transactions = self._load_objects(self.TRANSACTIONS_FILE,
                                               TRANSACTION_FIELDS,
                                               Transaction.from_dict)

    def save_data(self):
        """Write all books, members and transactions to their CSV files.

        Raises:
            OSError: If any file cannot be written.
        """
        save_rows(self.data_dir / self.BOOKS_FILE, BOOK_FIELDS,
                  [book.to_dict() for book in self.books.values()])
        save_rows(self.data_dir / self.MEMBERS_FILE, MEMBER_FIELDS,
                  [member.to_dict() for member in self.members.values()])
        save_rows(self.data_dir / self.TRANSACTIONS_FILE, TRANSACTION_FIELDS,
                  [record.to_dict() for record in self.transactions])

    def _load_objects(self, file_name, fieldnames, factory):
        """Turn each CSV row into an object using factory (a from_dict).

        Rows that cannot be converted are skipped with a warning. Because
        the next save would overwrite the file without those rows, the
        original file is first copied to a .bak backup.
        """
        file_path = self.data_dir / file_name
        objects = []
        skipped_rows = 0
        rows = load_rows(file_path, fieldnames)
        # Line 1 of the file is the header, so data starts on line 2.
        for line_number, row in enumerate(rows, start=2):
            try:
                objects.append(factory(row))
            except (ValueError, TypeError) as error:
                skipped_rows += 1
                self.warnings.append(f"{file_name} line {line_number} "
                                     f"skipped: {error}")

        if skipped_rows > 0:
            self._backup_with_warning(file_name)
        return objects

    def _index_unique(self, objects, attribute, file_name):
        """Build a dictionary keyed by attribute, ignoring duplicate keys."""
        indexed = {}
        duplicates_found = False
        for item in objects:
            key = getattr(item, attribute)
            if key in indexed:
                duplicates_found = True
                self.warnings.append(f"{file_name}: duplicate {attribute} "
                                     f"'{key}' ignored.")
            else:
                indexed[key] = item

        if duplicates_found:
            self._backup_with_warning(file_name)
        return indexed

    def _backup_with_warning(self, file_name):
        """Back up a data file that contained rows which were not loaded."""
        backup_path = backup_file(self.data_dir / file_name)
        message = (f"The original {file_name} was copied to "
                   f"{backup_path.name} so no data is lost.")
        if message not in self.warnings:
            self.warnings.append(message)

    # ------------------------------------------------------------------
    # Books and members
    # ------------------------------------------------------------------
    def add_book(self, isbn, title, author, year):
        """Validate and add a new book, then save.

        Raises:
            ValueError: If any field is invalid.
            LibraryError: If a book with the same ISBN already exists.
        """
        book = Book(isbn, title, author, year)
        if book.isbn in self.books:
            raise LibraryError(f"A book with ISBN {book.isbn} already exists.")
        self.books[book.isbn] = book
        self.save_data()
        return book

    def register_member(self, member_id, name, email):
        """Validate and register a new member, then save.

        Raises:
            ValueError: If any field is invalid.
            LibraryError: If the member ID is already in use.
        """
        member = Member(member_id, name, email)
        if member.member_id in self.members:
            raise LibraryError(f"Member ID {member.member_id} is already "
                               "registered.")
        self.members[member.member_id] = member
        self.save_data()
        return member

    def find_book(self, isbn):
        """Return the book with this ISBN.

        Raises:
            LibraryError: If no such book exists.
        """
        key = normalise_isbn(isbn)
        book = self.books.get(key)
        if book is None:
            raise LibraryError(f"No book found with ISBN {key}.")
        return book

    def find_member(self, member_id):
        """Return the member with this ID.

        Raises:
            LibraryError: If no such member exists.
        """
        key = validate_member_id(member_id)
        member = self.members.get(key)
        if member is None:
            raise LibraryError(f"No member found with ID {key}.")
        return member

    def search_books(self, query, field="all"):
        """Return books whose title, author or ISBN contains the query.

        Raises:
            ValueError: If the query is blank or the field is unknown.
        """
        query = require_text(query, "Search term")
        if field not in SEARCH_FIELDS:
            raise ValueError(f"Cannot search by '{field}'.")
        return [book for book in self.get_all_books()
                if book.matches(query, field)]

    def get_all_books(self):
        """Return every book, sorted alphabetically by title."""
        return sorted(self.books.values(), key=lambda book: book.title.lower())

    def get_available_books(self):
        """Return only the books that are currently on the shelf."""
        return [book for book in self.get_all_books() if book.is_available()]

    def get_all_members(self):
        """Return every member, sorted by member ID."""
        return sorted(self.members.values(),
                      key=lambda member: member.member_id)

    # ------------------------------------------------------------------
    # Borrowing and returning
    # ------------------------------------------------------------------
    def borrow_book(self, isbn, member_id, borrow_date=None):
        """Lend a book to a member and record a new transaction.

        Args:
            isbn (str): ISBN of the book to borrow.
            member_id (str): ID of the borrowing member.
            borrow_date (date, optional): Defaults to today; tests pass a
                fixed date so results are predictable.

        Returns:
            Transaction: The newly created record.

        Raises:
            LibraryError: If the book or member does not exist, the book is
                already on loan, or the member has reached the loan limit.
        """
        book = self.find_book(isbn)
        member = self.find_member(member_id)

        if not book.is_available():
            raise LibraryError(f"'{book.title}' is already on loan and "
                               "cannot be borrowed.")
        elif not member.can_borrow():
            raise LibraryError(f"{member.name} has reached the limit of "
                               f"{Member.MAX_LOANS} books on loan.")

        transaction = Transaction(self._next_transaction_id(), book.isbn,
                                  member.member_id,
                                  borrow_date or date.today())
        book.mark_borrowed()
        member.add_loan(book.isbn)
        self.transactions.append(transaction)
        self.save_data()
        return transaction

    def return_book(self, isbn, member_id, return_date=None):
        """Accept a returned book and close its open transaction.

        Returns:
            Transaction: The record that has just been closed.

        Raises:
            LibraryError: If the book or member does not exist, or this
                member does not currently have this book on loan.
            ValueError: If return_date is before the borrow date.
        """
        book = self.find_book(isbn)
        member = self.find_member(member_id)

        if not member.has_borrowed(book.isbn):
            raise LibraryError(f"{member.name} ({member.member_id}) does not "
                               f"have '{book.title}' on loan.")

        transaction = self._find_open_transaction(book.isbn, member.member_id)
        if transaction is None:
            # Only possible if the CSV files were edited by hand.
            raise LibraryError("No open borrowing record was found for this "
                               "book. Please check the data files.")

        transaction.close(return_date)
        book.mark_returned()
        member.remove_loan(book.isbn)
        self.save_data()
        return transaction

    def get_history(self, member_id=None):
        """Return all transactions, or only those of one member.

        Raises:
            LibraryError: If a member ID is given but does not exist.
        """
        if member_id is None:
            return list(self.transactions)
        member = self.find_member(member_id)
        return [record for record in self.transactions
                if record.member_id == member.member_id]

    def _find_open_transaction(self, isbn, member_id):
        """Return the open transaction for this book and member, or None."""
        for record in self.transactions:
            if (record.isbn == isbn and record.member_id == member_id
                    and record.is_open()):
                return record
        return None

    def _next_transaction_id(self):
        """Return the next unused transaction number."""
        highest = max((record.transaction_id for record in self.transactions),
                      default=0)
        return highest + 1
