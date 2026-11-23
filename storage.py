"""CSV file helpers used by the Library class.

Keeping file input/output in one small module means the Library class does
not repeat the same csv code three times (for books, members and
transactions), and the file-handling rules are easy to find and test.
"""

import csv
import shutil
from pathlib import Path


def load_rows(file_path, fieldnames):
    """Read a CSV file and return its rows as a list of dictionaries.

    * If the file does not exist, it is created with just a header row and
      an empty list is returned (first run of the program).
    * If the file is completely empty, an empty list is returned.

    Args:
        file_path: Path to the CSV file.
        fieldnames: The column names the file is expected to contain.

    Returns:
        list[dict]: One dictionary per data row.

    Raises:
        ValueError: If the header row is missing a required column.
        OSError: If the file exists but cannot be read.
    """
    path = Path(file_path)
    if not path.exists():
        save_rows(path, fieldnames, [])
        return []

    with path.open("r", newline="", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:  # the file has no content at all
            return []

        missing = [name for name in fieldnames
                   if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"{path.name} is missing the column(s): "
                             f"{', '.join(missing)}")
        return list(reader)


def backup_file(file_path):
    """Copy a file to '<name>.bak' and return the backup's path.

    Used before a file containing invalid rows is overwritten, so the
    original data can still be inspected and repaired by hand.
    """
    path = Path(file_path)
    backup_path = path.with_name(path.name + ".bak")
    shutil.copyfile(path, backup_path)
    return backup_path


def save_rows(file_path, fieldnames, rows):
    """Write a list of dictionaries to a CSV file, replacing its contents.

    The data folder is created automatically if it does not exist.

    Raises:
        OSError: If the file cannot be written (e.g. no permission).
    """
    path = Path(file_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
