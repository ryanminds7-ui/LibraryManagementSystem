"""The Member class: a registered library user and their current loans."""

from validation import require_text, validate_email, validate_member_id


class Member:
    """A person registered to borrow books.

    Attributes:
        member_id (str): Unique identifier such as "M001".
        name (str): Member's full name.
        email (str): Contact email address.
        borrowed_isbns (list[str]): ISBNs of books currently on loan.
    """

    MAX_LOANS = 3  # library policy: at most three books at once

    def __init__(self, member_id, name, email, borrowed_isbns=None):
        """Create a member, validating every field.

        Raises:
            ValueError: If any field is missing or invalid.
        """
        self.member_id = validate_member_id(member_id)
        self.name = require_text(name, "Name")
        self.email = validate_email(email)
        # list(...) makes a copy so two members never share one list.
        self.borrowed_isbns = list(borrowed_isbns) if borrowed_isbns else []

    def can_borrow(self):
        """Return True if the member is below the loan limit."""
        return len(self.borrowed_isbns) < Member.MAX_LOANS

    def has_borrowed(self, isbn):
        """Return True if the member currently has this book on loan."""
        return isbn in self.borrowed_isbns

    def add_loan(self, isbn):
        """Record that the member has borrowed a book.

        Raises:
            ValueError: If the limit is reached or the book is already held.
        """
        if not self.can_borrow():
            raise ValueError(f"{self.name} already has the maximum of "
                             f"{Member.MAX_LOANS} books on loan.")
        if self.has_borrowed(isbn):
            raise ValueError(f"{self.name} already has this book.")
        self.borrowed_isbns.append(isbn)

    def remove_loan(self, isbn):
        """Record that the member has returned a book.

        Raises:
            ValueError: If the member does not have this book.
        """
        if not self.has_borrowed(isbn):
            raise ValueError(f"{self.name} does not have this book on loan.")
        self.borrowed_isbns.remove(isbn)

    def to_dict(self):
        """Return the member as a dictionary of strings for CSV storage.

        Borrowed ISBNs are joined with ';' so they fit in one CSV cell.
        """
        return {
            "member_id": self.member_id,
            "name": self.name,
            "email": self.email,
            "borrowed_isbns": ";".join(self.borrowed_isbns),
        }

    @classmethod
    def from_dict(cls, row):
        """Create a Member from a dictionary read from the CSV file."""
        isbn_text = row.get("borrowed_isbns") or ""
        isbns = [isbn.strip() for isbn in isbn_text.split(";") if isbn.strip()]
        return cls(row["member_id"], row["name"], row["email"], isbns)

    def __str__(self):
        """Return a one-line summary used in the menu tables."""
        loans = f"{len(self.borrowed_isbns)}/{Member.MAX_LOANS}"
        return (f"{self.member_id:<8} {self.name[:24]:<24} "
                f"{self.email[:30]:<30} {loans}")
