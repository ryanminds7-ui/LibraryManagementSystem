# Project Guide: Compliance, Publishing and Submission

This document is for the student, not the marker. It covers the requirement analysis, a compliance matrix, known weaknesses, GitHub publishing steps, a submission checklist and notes to help you explain the work in a viva or Q&A.

---

## 1. Requirement analysis (Phase 1)

| ID | Requirement from the brief | Category |
|---|---|---|
| R1 | ≥ 4 classes, meaningful attributes, ≥ 4 meaningful methods each, objects interacting | Classes & objects |
| R2 | `for` and `while` loops; `if/elif/else` decisions | Control structures |
| R3 | CSV storage for books, members, transactions; persistence; missing/empty files handled | Data handling |
| R4 | try/except; invalid input; file errors; invalid borrow/return; clear messages | Exceptions |
| R5 | Multiple modules, not everything in `main.py` | Modules |
| R6 | PEP 8, meaningful names, docstrings, comments, no duplication, separation of concerns, beginner-readable | Code quality |
| R7 | Menu with options 1–10 | Interface |
| R8 | Add, register, search (title/author/ISBN), borrow, return, availability, history, duplicates, validation, informative messages | Functionality |
| R9 | `unittest` tests for the listed scenarios, with expected and actual results | Testing |
| R10 | README (12 sections), `.gitignore`, `requirements.txt`, sample CSVs, commit plan, publishing steps | GitHub |
| R11 | Report < 3,000 words, 5 sections, UML, analytical, honest | Report |

---

## 2. Marking-criteria compliance matrix

| Requirement | Demonstrated in code | Discussed in report | How it is tested |
|---|---|---|---|
| ≥ 4 classes | `Book`, `Member`, `Transaction`, `Library` (+ `LibraryError`) | §2.2, Fig. 1 | All test classes instantiate them |
| ≥ 4 methods per class | Book 7, Member 7, Transaction 7, Library 18 (excluding `__init__`) | §2.2 | `TestBook`, `TestMember`, `TestTransaction`, Library tests |
| Object interaction | `Library.borrow_book()` / `return_book()` | §3.1 | `TestBorrowingAndReturning` |
| `while` loops | `main.run_menu()`, `main.prompt_text()` | §3.3 | Demo session (blank title re-prompt, menu loop) |
| `for` loops | `Library._load_objects()`, `_index_unique()`, `_find_open_transaction()`, `main.print_table()`, `print_menu()` | §3.3 | Persistence tests, demo |
| `if/elif/else` | `Book.matches()`, `Library.borrow_book()`, `run_menu()` | §3.3 | `test_matches_is_case_insensitive`, borrow tests |
| CSV I/O | `storage.load_rows()`, `save_rows()`; `Library.load_data()`, `save_data()` | §2.4, §3.4 | `TestPersistence` |
| Persistence across restart | Save after every change | §2.4, §4.3 | `test_data_survives_restart`; demo session 2 |
| Missing / empty files | `storage.load_rows()` | §3.4 | `test_missing_files_are_created`, `test_empty_files_are_handled` |
| Corrupted data | Skip + warning + `.bak` backup | §4.4 | `test_invalid_rows_are_skipped_with_warning`, `test_backup_is_made_...` |
| try/except | `main.run_menu()`, `main.main()`, `Library._load_objects()`, `validation.validate_year()` | §3.5 | Error-case tests; demo |
| Invalid input | `validation.py`, `prompt_text()`, invalid menu choice | §3.5, §4.3 | `test_invalid_fields_are_rejected`, `test_invalid_input_is_not_saved`, `test_invalid_search_input` |
| File errors | `OSError` caught in `main()` and `run_menu()`; missing columns → `ValueError` | §3.4–3.5 | `test_missing_column_raises_error` |
| Prevent invalid borrow | Availability + loan limit + existence checks | §3.5 | `test_borrow_unavailable_book`, `test_loan_limit_is_enforced`, `test_borrow_unknown_book_or_member` |
| Prevent invalid return | `member.has_borrowed()` check | §3.5 | `test_return_book_that_was_not_borrowed`, `test_return_by_wrong_member` |
| Duplicates | `Library.add_book()`, `register_member()` | §2.2 | `test_duplicate_isbn_...`, `test_duplicate_member_id_...` |
| Search title/author/ISBN | `Book.matches()`, `Library.search_books()` | §2.2 | `TestSearching` |
| History | `Library.get_history()` | §2.2 | `test_history_for_one_member` |
| Modules | 7 modules (§2.1 of report) | §2.1 | Tests import each module separately |
| PEP 8 | Whole codebase | §4.1 | `pycodestyle` and `pyflakes`: no issues |
| Docstrings / comments | Every module, class and public method | — | Inspection |
| No duplication | `storage.py`, `validation.py`, `MENU_OPTIONS`, `print_table()` | §2.1, §3.2 | Inspection |
| Menu 1–10 | `main.MENU_OPTIONS` | §3.2 | Demo session |
| Testing | `tests/test_library.py` (33 tests) | §4 | `python -m unittest -v` |
| Reflection, limitations | — | §5 | — |

---

## 3. Weaknesses that could cost marks (and what to do)

1. **"What I learned" and AI declaration are placeholders.** These must be written by you. Markers can usually tell when a reflection is generic, so write about what you actually found difficult.
2. **Word count.** The report is about 2,920 words in total, or about 2,630 without code blocks, references and the declaration. Keep your additions under about 350 words, or cut Table 2 rows if you need space. Check whether your lecturer counts tables, diagrams and references.
3. **Understanding the code.** The biggest risk in a viva is being unable to explain a line. Read Section 6 below, run the program yourself and step through `borrow_book()`.
4. **Commit history.** A repository with one large commit looks like the code arrived all at once. Use the staged commit plan in Section 4 and make each commit as you review that part of the code.
5. **Mermaid rendering.** GitHub renders Mermaid in Markdown. If you submit the report as Word or PDF, export the diagram as an image first (for example from [mermaid.live](https://mermaid.live)).
6. **Brief wording.** Check the official brief for anything not in the prompt you were given, such as a required report template, referencing style, cover page or file naming. This guide only covers the requirements in that prompt.
7. **Known limitations** (report §5.3) are deliberate and honestly stated. Do not remove them; acknowledging limitations supports the "critical evaluation" criterion.

---

## 4. GitHub publishing

Nothing has been pushed to GitHub. You need to do this yourself.

**Repository description (one line):**
> Menu-driven, object-oriented Library Management System in Python with CSV persistence and unit tests (B100, Gisma University).

**Suggested topics:** `python`, `oop`, `csv`, `cli`, `unittest`, `library-management`

### Suggested commit history

Make these as separate commits while you review each part:

```
1. Initial project structure, README skeleton and .gitignore
2. Add validation helpers for ISBN, year, email and member IDs
3. Add Book class with availability and search matching
4. Add Member class with loan limit
5. Add Transaction class for borrow/return records
6. Add CSV storage helpers with missing/empty file handling
7. Add Library class: catalogue, members, borrowing and returning
8. Add menu-driven interface in main.py
9. Add sample CSV data
10. Add unit tests for books, members, transactions and library rules
11. Fix data loss when invalid CSV rows were skipped (backup to .bak)
12. Add README, demo session and assessment report
```

### Push instructions

1. Create an empty repository on GitHub named `LibraryManagementSystem`. Do **not** tick "Add a README".
2. In a terminal inside the project folder:

```bash
git init
git add .
git commit -m "Initial commit: Library Management System"
git branch -M main
git remote add origin https://github.com/<your-username>/LibraryManagementSystem.git
git push -u origin main
```

(For a staged history, replace `git add .` + a single commit with `git add <files>` + `git commit -m "..."` for each step above.)

3. GitHub will ask you to sign in. Use a personal access token or GitHub Desktop if a password is refused.
4. Open the repository page and check that the README and Mermaid diagram display correctly.
5. Put the repository URL in the report header and the README author line.

---

## 5. Final submission checklist

- [ ] Run `python -m unittest -v` on **your** computer and confirm `OK` (33 tests)
- [ ] Run `python main.py`, try every menu option, then restart and confirm data was kept
- [ ] Reset `data/` to the sample data if you changed it during testing (or keep your changes deliberately)
- [ ] Delete any `data/*.bak` files and `__pycache__` folders
- [ ] Fill in name, student ID, date and GitHub URL (report header, README)
- [ ] Write report §5.2 "What I learned" in your own words
- [ ] Complete the AI-assistance declaration according to Gisma policy
- [ ] Fill in "Accessed" dates in the references
- [ ] Re-check the word count after your edits (< 3,000)
- [ ] Export the report to the required format (Word/PDF), with the UML diagram as an image
- [ ] Push to GitHub and check that the repository is visible to your lecturer (public, or lecturer invited)
- [ ] Compare against the official brief and rubric one last time

---

## 6. Explaining the application (viva preparation)

**What happens when the program starts?**
`main()` creates `Library(DATA_DIR)`. The constructor calls `load_data()`, which uses `storage.load_rows()` to read each CSV into dictionaries, and `from_dict()` to turn each row into an object. Invalid rows are skipped with a warning, and the original file is backed up. Then `run_menu()` starts a `while True` loop.

**How does the menu choose what to do?**
`MENU_OPTIONS` maps `"1"`–`"10"` to `(label, function)`. `run_menu()` looks up the choice with `.get()`. If the result is `None` the choice is invalid; otherwise it calls the function, passing the library. Functions are objects in Python, so they can be stored in a dictionary.

**Walk through borrowing a book.**
`borrow_book(isbn, member_id)`:
1. `find_book()` normalises the ISBN and looks it up in the `books` dictionary, raising `LibraryError` if it is missing. `find_member()` does the same for members.
2. `if not book.is_available()` → error. `elif not member.can_borrow()` → error.
3. A `Transaction` is created with the next ID (highest existing ID + 1).
4. Only now is state changed: `book.mark_borrowed()`, `member.add_loan()`, append the transaction.
5. `save_data()` rewrites all three CSV files.

**Why check before changing anything?**
If a check fails half-way, nothing has been modified, so the data stays consistent.

**Why two exception types?**
`ValueError` means "the data you typed is invalid" (e.g. year "abc"). `LibraryError` means "the data is fine but the rules don't allow it" (e.g. the book is on loan). The menu catches both and prints different prefixes ("Invalid input:" vs "Error:").

**Why are books and members in dictionaries but transactions in a list?**
Books and members are looked up by a unique key, so a dictionary gives direct access and duplicate checks are just `if key in dict`. Transactions are a history whose order matters and which have no natural lookup key.

**Why does Transaction store an ISBN rather than a Book object?**
A CSV cell can hold text, not an object. Storing IDs makes saving and loading simple; `Library` turns IDs back into objects with `find_book()` and `find_member()`.

**What is `@classmethod from_dict`?**
An alternative constructor. `Book.from_dict(row)` builds a `Book` from a CSV dictionary, so each class knows how to load itself.

**What does `raise ... from None` do?**
It hides the original technical exception, so the user sees "Publication year must be a whole number." instead of a message about `int()`.

**How do the tests avoid changing the real data?**
`setUp()` creates a `tempfile.TemporaryDirectory()` and passes it to `Library`. `tearDown()` deletes it.

**What bug did you find?**
Skipped invalid rows were lost at the next save, because saving rewrites files from memory. The fix is `storage.backup_file()`, which creates a `.bak` copy first. A regression test confirms it.

**What would you improve first?**
A consistency check between the three CSV files at start-up, and due dates/overdue reports.
