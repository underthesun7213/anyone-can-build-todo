# AGENTS.md — for the AI agent working in this repository

The person asking you may be new to programming, and may read English as a second language.
Explain in short, plain sentences, and define a technical word the first time you use it. When you
change code, say which file changed and why.

## What this is

The most basic to-do list, in Django. A person can add a to-do, mark it done (or undo that), and
delete it. There are no accounts: everyone who opens the site sees the same list. The data is kept
in a SQLite database, the file `db.sqlite3`, which is not in git.

## What each file does

| File | Its one job |
|---|---|
| `config/settings.py` | Settings for the whole project. The secret key, debug and allowed hosts come from environment variables on a live server, with defaults for a laptop. |
| `config/urls.py` | Sends `/admin/` to Django's admin, and everything else to `todos/urls.py`. |
| `todos/models.py` | The `Todo` table: `title`, `done`, `created_at`. |
| `todos/urls.py` | The six addresses: the list, add, edit, toggle, delete, clear-done. |
| `todos/views.py` | One function per address. Add, toggle, delete and clear-done accept `POST` only, then send the browser back to the list. Edit accepts `GET` and `POST` only. |
| `todos/forms.py` | `TodoForm`: checks the title, for both add and edit. |
| `todos/templates/todos/base.html` | The shared page frame and styles. The other pages extend it. |
| `todos/templates/todos/todo_list.html` | The main page: the add form and the list. |
| `todos/templates/todos/todo_edit.html` | The edit page: one form to change a to-do's title. |
| `todos/tests.py` | The tests. |
| `todos/migrations/` | Made by Django from `models.py`. Never edit these by hand. |
| `pyproject.toml`, `uv.lock` | The packages this project uses, and their exact versions. |
| `.pre-commit-config.yaml` | The checks that run on every `git commit`. |
| `Makefile` | Short commands. `make help` lists them. |

## Commands

This project uses **uv** to install Python and the packages. Run every Python command through
`uv run`, so it uses this project's packages:

- `make setup` — install everything, create the database, turn on the commit checks
- `make run` — start the server at <http://127.0.0.1:8000>
- `make test` — run the tests
- `make lint` / `make format` — Ruff: find mistakes, and rewrite code in the standard style
- `make check` — every commit check on every file, then the tests

Add a package with `uv add <name>`, never with `pip install`. After changing `models.py`, run
`uv run python manage.py makemigrations` and then `uv run python manage.py migrate`.

## Rules

- **Run `make check` before every commit.** The commit checks also run by themselves. If one fails
  after fixing a file, look at the change, `git add` the file, and commit again.
- **Never put a secret in the code.** Passwords, keys and tokens go in environment variables.
- **Use what Django already has** — forms, the admin, `get_object_or_404`, the test client — before
  writing your own.
- **Change data only with `POST`.** A `GET` request only reads.
- **Add or change a test with every change in behavior**, and show the person the test failing
  before the fix and passing after.
