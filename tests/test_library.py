"""Unit tests for the Library Management System.

Run from the project folder with:

    python -m unittest -v

Every test uses a temporary folder for its CSV files, so the real sample
data in data/ is never changed by the tests.
"""

import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

# Make the project folder importable when this file is run directly.
PROJECT_DIR = Path(__file__).resolve().parent.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from book import Book  # noqa: E402
from library import Library, LibraryError  # noqa: E402
from member import Member  # noqa: E402
from transaction import Transaction  # noqa: E402

ISBN_PYTHON = "9781593279288"
ISBN_CLEAN = "9780132350884"


class TestBook(unittest.TestCase):
    """Tests for the Book class on its own."""

    def test_isbn_hyphens_are_removed(self):
        book = Book("978-1-59327-928-8", "Python Crash Course",
                    "Eric Matthes", 2019)
        self.assertEqual(book.isbn, ISBN_PYTHON)
        self.assertTrue(book.is_available())

    def test_invalid_fields_are_rejected(self):
        with self.assertRaises(ValueError):
            Book("12345", "Title", "Author", 2000)          # short ISBN
        with self.assertRaises(ValueError):
            Book(ISBN_PYTHON, "   ", "Author", 2000)        # blank title
        with self.assertRaises(ValueError):
            Book(ISBN_PYTHON, "Title", "Author", "twenty")  # not a number
        with self.assertRaises(ValueError):
            Book(ISBN_PYTHON, "Title", "Author", 3000)      # future year

    def test_cannot_borrow_twice_or_return_when_available(self):
        book = Book(ISBN_PYTHON, "Python Crash Course", "Eric Matthes", 2019)
        book.mark_borrowed()
        with self.assertRaises(ValueError):
            book.mark_borrowed()
        book.mark_returned()
        with self.assertRaises(ValueError):
            book.mark_returned()

    def test_matches_is_case_insensitive(self):
        book = Book(ISBN_PYTHON, "Python Crash Course", "Eric Matthes", 2019)
        self.assertTrue(book.matches("CRASH", "title"))
        self.assertTrue(book.matches("matthes", "author"))
        self.assertTrue(book.matches("978-1593", "isbn"))
        self.assertFalse(book.matches("Matthes", "title"))

    def test_dictionary_round_trip(self):
        book = Book(ISBN_PYTHON, "Python Crash Course", "Eric Matthes", 2019,
                    available=False)
        copy = Book.from_dict(book.to_dict())
        self.assertEqual(copy.to_dict(), book.to_dict())


class TestMember(unittest.TestCase):
    """Tests for the Member class on its own."""

    def test_invalid_email_and_id_are_rejected(self):
        with self.assertRaises(ValueError):
            Member("M001", "Anna", "not-an-email")
        with self.assertRaises(ValueError):
            Member("M-001", "Anna", "anna@example.com")

    def test_loan_limit(self):
        member = Member("m001", "Anna", "anna@example.com")
        self.assertEqual(member.member_id, "M001")  # stored in upper case
        for number in range(Member.MAX_LOANS):
            member.add_loan(f"isbn{number}")
        self.assertFalse(member.can_borrow())
        with self.assertRaises(ValueError):
            member.add_loan("one-too-many")

    def test_remove_loan_that_does_not_exist(self):
        member = Member("M001", "Anna", "anna@example.com")
        with self.assertRaises(ValueError):
            member.remove_loan(ISBN_PYTHON)

    def test_dictionary_round_trip_keeps_loans(self):
        member = Member("M001", "Anna", "anna@example.com",
                        [ISBN_PYTHON, ISBN_CLEAN])
        copy = Member.from_dict(member.to_dict())
        self.assertEqual(copy.borrowed_isbns, [ISBN_PYTHON, ISBN_CLEAN])


class TestTransaction(unittest.TestCase):
    """Tests for the Transaction class on its own."""

    def test_close_and_days_on_loan(self):
        record = Transaction(1, ISBN_PYTHON, "M001", date(2026, 1, 1))
        self.assertTrue(record.is_open())
        record.close(date(2026, 1, 15))
        self.assertFalse(record.is_open())
        self.assertEqual(record.days_on_loan(), 14)
        self.assertEqual(record.status(), "Returned")

    def test_cannot_close_twice_or_before_borrow_date(self):
        record = Transaction(1, ISBN_PYTHON, "M001", date(2026, 1, 10))
        with self.assertRaises(ValueError):
            record.close(date(2026, 1, 5))
        record.close(date(2026, 1, 12))
        with self.assertRaises(ValueError):
            record.close(date(2026, 1, 13))


class LibraryTestCase(unittest.TestCase):
    """Base class: gives every test an empty library in a temp folder."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_dir.name)
        self.library = Library(self.data_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def add_sample_data(self):
        """Add two books and two members used by several tests."""
        self.library.add_book(ISBN_PYTHON, "Python Crash Course",
                              "Eric Matthes", 2019)
        self.library.add_book(ISBN_CLEAN, "Clean Code",
                              "Robert C. Martin", 2008)
        self.library.register_member("M001", "Anna Schmidt",
                                     "anna@example.com")
        self.library.register_member("M002", "David Okafor",
                                     "david@example.com")


class TestAddingAndRegistering(LibraryTestCase):
    """Adding books, registering members and duplicate records."""

    def test_add_book(self):
        book = self.library.add_book(ISBN_PYTHON, "Python Crash Course",
                                     "Eric Matthes", "2019")
        self.assertIn(ISBN_PYTHON, self.library.books)
        self.assertEqual(book.year, 2019)

    def test_duplicate_isbn_is_rejected_even_with_hyphens(self):
        self.library.add_book(ISBN_PYTHON, "Python Crash Course",
                              "Eric Matthes", 2019)
        with self.assertRaises(LibraryError):
            self.library.add_book("978-1-59327-928-8", "Another Title",
                                  "Someone", 2020)
        self.assertEqual(len(self.library.books), 1)

    def test_register_member(self):
        self.library.register_member("M001", "Anna Schmidt",
                                     "Anna@Example.com")
        member = self.library.find_member("m001")
        self.assertEqual(member.email, "anna@example.com")

    def test_duplicate_member_id_is_rejected(self):
        self.library.register_member("M001", "Anna", "anna@example.com")
        with self.assertRaises(LibraryError):
            self.library.register_member("m001", "Other", "o@example.com")

    def test_invalid_input_is_not_saved(self):
        with self.assertRaises(ValueError):
            self.library.add_book("", "Title", "Author", 2000)
        with self.assertRaises(ValueError):
            self.library.register_member("M009", "", "x@example.com")
        self.assertEqual(self.library.books, {})
        self.assertEqual(self.library.members, {})


class TestSearching(LibraryTestCase):
    """Searching by title, author and ISBN."""

    def setUp(self):
        super().setUp()
        self.add_sample_data()

    def test_search_by_each_field(self):
        by_title = self.library.search_books("clean", "title")
        by_author = self.library.search_books("matthes", "author")
        by_isbn = self.library.search_books("9780132", "isbn")
        self.assertEqual([b.isbn for b in by_title], [ISBN_CLEAN])
        self.assertEqual([b.isbn for b in by_author], [ISBN_PYTHON])
        self.assertEqual([b.isbn for b in by_isbn], [ISBN_CLEAN])

    def test_search_all_fields_and_no_results(self):
        self.assertEqual(len(self.library.search_books("c", "all")), 2)
        self.assertEqual(self.library.search_books("Tolkien"), [])

    def test_invalid_search_input(self):
        with self.assertRaises(ValueError):
            self.library.search_books("   ")
        with self.assertRaises(ValueError):
            self.library.search_books("python", "publisher")


class TestBorrowingAndReturning(LibraryTestCase):
    """Borrowing and returning rules."""

    def setUp(self):
        super().setUp()
        self.add_sample_data()

    def test_borrow_available_book(self):
        record = self.library.borrow_book(ISBN_PYTHON, "M001",
                                          date(2026, 11, 1))
        self.assertEqual(record.transaction_id, 1)
        self.assertFalse(self.library.find_book(ISBN_PYTHON).is_available())
        self.assertTrue(self.library.find_member("M001")
                        .has_borrowed(ISBN_PYTHON))
        self.assertNotIn(self.library.find_book(ISBN_PYTHON),
                         self.library.get_available_books())

    def test_borrow_unavailable_book(self):
        self.library.borrow_book(ISBN_PYTHON, "M001")
        with self.assertRaises(LibraryError):
            self.library.borrow_book(ISBN_PYTHON, "M002")
        self.assertEqual(len(self.library.transactions), 1)

    def test_borrow_unknown_book_or_member(self):
        with self.assertRaises(LibraryError):
            self.library.borrow_book("9780000000000", "M001")
        with self.assertRaises(LibraryError):
            self.library.borrow_book(ISBN_PYTHON, "M999")

    def test_loan_limit_is_enforced(self):
        for number in range(Member.MAX_LOANS):
            isbn = f"978000000000{number}"
            self.library.add_book(isbn, f"Book {number}", "Author", 2000)
            self.library.borrow_book(isbn, "M001")
        with self.assertRaises(LibraryError):
            self.library.borrow_book(ISBN_PYTHON, "M001")

    def test_return_borrowed_book(self):
        self.library.borrow_book(ISBN_PYTHON, "M001", date(2026, 11, 1))
        record = self.library.return_book(ISBN_PYTHON, "M001",
                                          date(2026, 11, 8))
        self.assertEqual(record.days_on_loan(), 7)
        self.assertTrue(self.library.find_book(ISBN_PYTHON).is_available())
        self.assertFalse(self.library.find_member("M001")
                         .has_borrowed(ISBN_PYTHON))

    def test_return_book_that_was_not_borrowed(self):
        with self.assertRaises(LibraryError):
            self.library.return_book(ISBN_PYTHON, "M001")

    def test_return_by_wrong_member(self):
        self.library.borrow_book(ISBN_PYTHON, "M001")
        with self.assertRaises(LibraryError):
            self.library.return_book(ISBN_PYTHON, "M002")
        self.assertFalse(self.library.find_book(ISBN_PYTHON).is_available())

    def test_history_for_one_member(self):
        self.library.borrow_book(ISBN_PYTHON, "M001")
        self.library.borrow_book(ISBN_CLEAN, "M002")
        self.assertEqual(len(self.library.get_history()), 2)
        member_history = self.library.get_history("M002")
        self.assertEqual([r.isbn for r in member_history], [ISBN_CLEAN])


class TestPersistence(LibraryTestCase):
    """Saving to and loading from CSV files."""

    def test_data_survives_restart(self):
        self.add_sample_data()
        self.library.borrow_book(ISBN_PYTHON, "M001", date(2026, 11, 1))
        self.library.borrow_book(ISBN_CLEAN, "M002", date(2026, 11, 2))
        self.library.return_book(ISBN_CLEAN, "M002", date(2026, 11, 5))

        reloaded = Library(self.data_dir)  # simulates restarting the app
        self.assertEqual(len(reloaded.books), 2)
        self.assertEqual(len(reloaded.members), 2)
        self.assertFalse(reloaded.find_book(ISBN_PYTHON).is_available())
        self.assertTrue(reloaded.find_book(ISBN_CLEAN).is_available())
        self.assertEqual(reloaded.find_member("M001").borrowed_isbns,
                         [ISBN_PYTHON])
        self.assertEqual(reloaded.transactions[1].return_date,
                         date(2026, 11, 5))
        self.assertEqual(reloaded.warnings, [])

    def test_missing_files_are_created(self):
        for name in ("books.csv", "members.csv", "transactions.csv"):
            self.assertTrue((self.data_dir / name).exists())

    def test_empty_files_are_handled(self):
        for name in ("books.csv", "members.csv", "transactions.csv"):
            (self.data_dir / name).write_text("", encoding="utf-8")
        library = Library(self.data_dir)
        self.assertEqual(library.books, {})
        self.assertEqual(library.transactions, [])

    def test_invalid_rows_are_skipped_with_warning(self):
        (self.data_dir / "books.csv").write_text(
            "isbn,title,author,year,available\n"
            f"{ISBN_PYTHON},Python Crash Course,Eric Matthes,2019,True\n"
            "bad-isbn,Broken,Nobody,2019,True\n"
            f"{ISBN_PYTHON},Duplicate,Someone,2020,True\n",
            encoding="utf-8")
        library = Library(self.data_dir)
        self.assertEqual(len(library.books), 1)
        # Two "skipped" warnings plus one backup notice.
        self.assertEqual(len(library.warnings), 3)

    def test_backup_is_made_before_invalid_rows_are_lost(self):
        # Regression test for a bug found during manual testing: skipped
        # rows used to disappear permanently at the next save.
        original = ("isbn,title,author,year,available\n"
                    "bad-isbn,Broken,Nobody,2019,True\n")
        (self.data_dir / "books.csv").write_text(original, encoding="utf-8")
        library = Library(self.data_dir)
        library.add_book(ISBN_PYTHON, "Python Crash Course",
                         "Eric Matthes", 2019)  # triggers a save
        backup = self.data_dir / "books.csv.bak"
        self.assertTrue(backup.exists())
        self.assertEqual(backup.read_text(encoding="utf-8"), original)

    def test_missing_column_raises_error(self):
        (self.data_dir / "books.csv").write_text("isbn,title\n1,A\n",
                                                 encoding="utf-8")
        with self.assertRaises(ValueError):
            Library(self.data_dir)


if __name__ == "__main__":
    unittest.main()
