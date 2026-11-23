"""Reusable validation functions for the Library Management System.

The Book, Member and Library classes share these functions so that each
validation rule is written only once. Every function either returns a
cleaned-up value or raises ValueError with a message that can be shown
directly to the user.
"""

from datetime import date

EARLIEST_PUBLICATION_YEAR = 1450  # roughly when the printing press appeared


def require_text(value, field_name):
    """Return the value without surrounding spaces, or raise if it is blank.

    Args:
        value: The raw value typed by the user or read from a CSV file.
        field_name: A readable name used in the error message, e.g. "Title".

    Returns:
        str: The stripped text.

    Raises:
        ValueError: If the value is None or contains only whitespace.
    """
    text = "" if value is None else str(value).strip()
    if not text:
        raise ValueError(f"{field_name} is required and cannot be empty.")
    return text


def normalise_isbn(isbn):
    """Remove hyphens and spaces from an ISBN and check its length.

    Both ISBN-10 (the last character may be 'X') and ISBN-13 are accepted.
    The check digit itself is not verified, to keep the rules simple.

    Raises:
        ValueError: If the ISBN is blank or has the wrong format.
    """
    cleaned = require_text(isbn, "ISBN").replace("-", "").replace(" ", "")
    cleaned = cleaned.upper()

    if len(cleaned) == 13 and cleaned.isdigit():
        return cleaned
    if (len(cleaned) == 10 and cleaned[:9].isdigit()
            and (cleaned[9].isdigit() or cleaned[9] == "X")):
        return cleaned
    raise ValueError("ISBN must contain 10 or 13 digits "
                     "(hyphens and spaces are allowed).")


def validate_year(year):
    """Convert a publication year to int and check it is realistic.

    Raises:
        ValueError: If the year is not a whole number or is out of range.
    """
    try:
        year_number = int(str(year).strip())
    except ValueError:
        # "from None" hides the technical int() error from the user.
        raise ValueError("Publication year must be a whole number.") from None

    current_year = date.today().year
    if not EARLIEST_PUBLICATION_YEAR <= year_number <= current_year:
        raise ValueError("Publication year must be between "
                         f"{EARLIEST_PUBLICATION_YEAR} and {current_year}.")
    return year_number


def validate_member_id(member_id):
    """Return a member ID in upper case, checking it is letters/digits only.

    Raises:
        ValueError: If the ID is blank or contains other characters.
    """
    text = require_text(member_id, "Member ID").upper()
    if not text.isalnum():
        raise ValueError("Member ID may only contain letters and numbers "
                         "(for example M001).")
    return text


def validate_email(email):
    """Perform a simple sanity check on an email address.

    This is intentionally basic: it checks for one '@', text before it and
    a dot inside the domain part. It does not prove the address exists.

    Raises:
        ValueError: If the address does not look like name@example.com.
    """
    text = require_text(email, "Email").lower()
    local_part, at_sign, domain = text.partition("@")

    if (not local_part or not at_sign or " " in text or "@" in domain
            or "." not in domain or domain.startswith(".")
            or domain.endswith(".")):
        raise ValueError("Email address must look like name@example.com.")
    return text


def parse_bool(value):
    """Convert text such as 'True' or 'False' (from a CSV file) to a bool.

    Raises:
        ValueError: If the text is not a recognised true/false value.
    """
    text = str(value).strip().lower()
    if text in ("true", "yes", "1"):
        return True
    if text in ("false", "no", "0"):
        return False
    raise ValueError(f"'{value}' is not a valid true/false value.")
