"""The Book class: the details and loan status of one book."""

from validation import normalise_isbn, parse_bool, require_text, validate_year

# The fields a user may search by. "all" means title, author or ISBN.
SEARCH_FIELDS = ("title", "author", "isbn", "all")


class Book:
    """A single book in the library's catalogue.

    Attributes:
        isbn (str): Unique identifier, stored without hyphens.
        title (str): Title of the book.
        author (str): Author's name.
        year (int): Year of publication.
        available (bool): True if the book is on the shelf, False if on loan.
    """

    def __init__(self, isbn, title, author, year, available=True):
        """Create a book, validating every field.

        Raises:
            ValueError: If any field is missing or invalid.
        """
        self.isbn = normalise_isbn(isbn)
        self.title = require_text(title, "Title")
        self.author = require_text(author, "Author")
        self.year = validate_year(year)
        self.available = available

    def is_available(self):
        """Return True if the book can currently be borrowed."""
        return self.available

    def mark_borrowed(self):
        """Mark the book as on loan.

        Raises:
            ValueError: If the book is already on loan.
        """
        if not self.available:
            raise ValueError(f"'{self.title}' is already on loan.")
        self.available = False

    def mark_returned(self):
        """Mark the book as back on the shelf.

        Raises:
            ValueError: If the book was not on loan.
        """
        if self.available:
            raise ValueError(f"'{self.title}' is not currently on loan.")
        self.available = True

    def matches(self, query, field="all"):
        """Return True if the query appears in the chosen field.

        The comparison is case-insensitive and matches part of a word,
        so "pyth" matches "Python Crash Course".

        Args:
            query (str): The text to look for.
            field (str): One of "title", "author", "isbn" or "all".

        Raises:
            ValueError: If the field name is not recognised.
        """
        query = query.strip().lower()

        if field == "title":
            return query in self.title.lower()
        elif field == "author":
            return query in self.author.lower()
        elif field == "isbn":
            # Ignore hyphens so "978-0" finds "9780...".
            cleaned_query = query.replace("-", "").replace(" ", "")
            return cleaned_query in self.isbn.lower()
        elif field == "all":
            return any(self.matches(query, name)
                       for name in ("title", "author", "isbn"))
        else:
            raise ValueError(f"Cannot search by '{field}'. Choose from: "
                             f"{', '.join(SEARCH_FIELDS)}.")

    def to_dict(self):
        """Return the book as a dictionary of strings for CSV storage."""
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "year": str(self.year),
            "available": str(self.available),
        }

    @classmethod
    def from_dict(cls, row):
        """Create a Book from a dictionary read from the CSV file.

        Raises:
            ValueError: If the row contains invalid data.
        """
        return cls(row["isbn"], row["title"], row["author"], row["year"],
                   parse_bool(row["available"]))

    def __str__(self):
        """Return a one-line summary used in the menu tables."""
        status = "Available" if self.available else "On loan"
        return (f"{self.isbn:<14} {self.title[:30]:<30} "
                f"{self.author[:22]:<22} {self.year:<5} {status}")
