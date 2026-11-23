"""The Transaction class: a record of one book being borrowed and returned."""

from datetime import date


class Transaction:
    """One borrowing event. It stays "open" until the book is returned.

    Attributes:
        transaction_id (int): Unique, increasing number.
        isbn (str): ISBN of the borrowed book.
        member_id (str): ID of the member who borrowed it.
        borrow_date (date): Date the book was borrowed.
        return_date (date | None): Date it was returned, or None if on loan.
    """

    def __init__(self, transaction_id, isbn, member_id, borrow_date,
                 return_date=None):
        """Create a transaction record.

        Raises:
            ValueError: If the ID is not positive or the dates are in the
                wrong order.
        """
        self.transaction_id = int(transaction_id)
        if self.transaction_id < 1:
            raise ValueError("Transaction ID must be a positive number.")
        self.isbn = isbn
        self.member_id = member_id
        self.borrow_date = borrow_date
        self.return_date = return_date
        if return_date is not None and return_date < borrow_date:
            raise ValueError("Return date cannot be before the borrow date.")

    def is_open(self):
        """Return True if the book has not been returned yet."""
        return self.return_date is None

    def close(self, return_date=None):
        """Mark the loan as finished (defaults to today's date).

        Raises:
            ValueError: If already closed or the date is before borrowing.
        """
        if not self.is_open():
            raise ValueError(f"Transaction {self.transaction_id} has "
                             "already been closed.")
        return_date = return_date or date.today()
        if return_date < self.borrow_date:
            raise ValueError("Return date cannot be before the borrow date.")
        self.return_date = return_date

    def days_on_loan(self, today=None):
        """Return how many days the book was (or has been) on loan."""
        end_date = self.return_date or today or date.today()
        return (end_date - self.borrow_date).days

    def status(self):
        """Return a readable status: 'On loan' or 'Returned'."""
        return "On loan" if self.is_open() else "Returned"

    def to_dict(self):
        """Return the transaction as a dictionary of strings for CSV."""
        return {
            "transaction_id": str(self.transaction_id),
            "isbn": self.isbn,
            "member_id": self.member_id,
            "borrow_date": self.borrow_date.isoformat(),
            "return_date": (self.return_date.isoformat()
                            if self.return_date else ""),
        }

    @classmethod
    def from_dict(cls, row):
        """Create a Transaction from a dictionary read from the CSV file.

        Dates are stored in ISO format (YYYY-MM-DD). An empty return date
        means the book is still on loan.
        """
        return_text = (row.get("return_date") or "").strip()
        return_date = date.fromisoformat(return_text) if return_text else None
        return cls(row["transaction_id"], row["isbn"], row["member_id"],
                   date.fromisoformat(row["borrow_date"]), return_date)

    def __str__(self):
        """Return a one-line summary used in the history table."""
        returned = self.return_date.isoformat() if self.return_date else "-"
        return (f"{self.transaction_id:<5} {self.isbn:<14} "
                f"{self.member_id:<8} {self.borrow_date.isoformat():<11} "
                f"{returned:<11} {self.status()}")
