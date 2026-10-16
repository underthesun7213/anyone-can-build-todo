# Plan: clear done to-dos

Status: built.

This is feature F6 in `PLAN.md`. It starts from the current `main` (commit `d8c4bab`, with the edit
feature merged). Every "How it fails today" below is true on that `main`.

## What it does

The list page has a **Clear done** button. Pressing it deletes every to-do that is done. The
to-dos that are not done stay, in the same order.

- **The button shows only when at least one to-do is done.** If no to-do is done, or the list is
  empty, there is no button.
- **No confirmation dialog.** One press deletes them. It cannot be undone.
- **The address is `/clear-done/`, and it accepts only `POST`.** A `GET` on it gives 405 (method
  not allowed) and deletes nothing. (`PLAN.md` section 11.)
- **After the delete, the browser goes back to the list** (a redirect, status 302). So pressing
  reload on the list does not send the delete again.
- **A `POST` when nothing is done** is not an error. It deletes nothing and still goes back to the
  list. (This can happen if two people use the list at the same time: everyone sees the same list.)
- There is no to-do number in this address, so the "missing to-do gives 404" rule does not apply.

## How it is built

No new field, so **no migration**. No new form: the button needs no input, only the CSRF token.
(CSRF is Django's check that a `POST` came from our own page.)

- `todos/urls.py`: add one address, `path("clear-done/", views.todo_clear_done,
  name="todo_clear_done")`.
- `todos/views.py`:
  - A new view, `todo_clear_done`, with the `@require_POST` decorator, like `todo_delete`. It runs
    `Todo.objects.filter(done=True).delete()`, then `return redirect("todo_list")`. The database
    deletes them all in one step; no Python loop.
  - `todo_list` gives the page one more value: `"has_done": todos.filter(done=True).exists()`.
    `.exists()` asks the database only "is there one?". The template cannot filter by itself, so
    the view decides.
- `todos/templates/todos/todo_list.html`: just **after** `</ul>`, add:

  ```html
  {% if has_done %}
    <form method="post" action="{% url 'todo_clear_done' %}">
      {% csrf_token %}
      <button type="submit">Clear done</button>
    </form>
  {% endif %}
  ```

  No new CSS: the button uses the existing `button` style.
- `AGENTS.md`: the `todos/urls.py` row says "four addresses". Change it to name the addresses, with
  clear-done added. The `todos/views.py` row: add that clear-done is `POST` only too.

Files that do not change: `models.py`, `forms.py`, `base.html`, `todo_edit.html`, the migrations.
No new package.

## Tests

All new tests go in `todos/tests.py`, in the `TodoTests` class. We write them **first**, run
`make test`, and show the person the failures. Then we write the code and show them passing.

Most tests use `reverse("todo_clear_done")`. Today that name does not exist, so those tests fail
with an **error** `NoReverseMatch` (Django cannot find an address with that name).

| Test | What it checks | How it fails today |
|---|---|---|
| `test_clear_done_removes_only_done_todos` | 3 to-dos, 2 done. `POST` to clear-done. Only the not-done one is left, with its title. | Error: `NoReverseMatch` |
| `test_clear_done_redirects_to_list` | `POST` to clear-done gives a redirect to `reverse("todo_list")` (`assertRedirects`). | Error: `NoReverseMatch` |
| `test_clear_done_with_nothing_done_changes_nothing` | 2 to-dos, none done. `POST` to clear-done: both are still there, and it still redirects to the list. | Error: `NoReverseMatch` |
| `test_get_on_clear_done_is_not_allowed` | 1 done to-do. `GET` on clear-done gives 405, and the to-do is still there. Put it with the other "GET is 405" tests. | Error: `NoReverseMatch` |
| `test_clear_done_button_shown_when_something_is_done` | 1 done and 1 not-done to-do. The list page contains `Clear done` and `action="/clear-done/"`. | `AssertionError`: the page has no button |
| `test_no_clear_done_button_when_nothing_is_done` | 1 to-do, not done. The page does **not** contain `Clear done`. | Passes today (it protects the "hidden" rule). |
| `test_no_clear_done_button_on_empty_list` | No to-dos. The page says `Nothing to do yet` and does **not** contain `Clear done`. | Passes today (it protects the "hidden" rule). |

The two "no button" tests use the plain text `Clear done`, not `reverse(...)`, so they run and pass
today. They pass for the right reason only after the code: to prove that, after the code, change
`{% if has_done %}` to `{% if todos %}` for a moment and see `test_no_clear_done_button_when_nothing_is_done`
fail; then put it back.

The 5 new-behavior tests must fail before the code (4 errors, 1 failure). All 34 old tests must
still pass.

## Done when

`make test` shows `Ran 41 tests` and `OK` (34 today + 7 new). `make check` passes, including the
check that no migration is missing. A person runs `make run`, marks one to-do done, sees the
button, presses it, and the done one is gone while the others stay.

## Files this touches

- `todos/urls.py` (one new line in `urlpatterns`)
- `todos/views.py` (new view `todo_clear_done`; one new key in `todo_list`'s context)
- `todos/templates/todos/todo_list.html` (new form after `</ul>`)
- `todos/tests.py` (7 new tests in `TodoTests`)
- `AGENTS.md` (file table rows for `urls.py` and `views.py`)

Overlap note: F7 (count) will likely also add a context key in `todo_list` and something after
`</ul>`. Merge those by hand; each adds its own lines.

## Review objections

| # | Objection | Decision | Why |
|---|---|---|---|
| 1 | The plan says the AGENTS.md `urls.py` row reads "four addresses"; on `main` it already reads "five addresses", and the `views.py` row already mentions Edit. | Accept | The plan must match the real file. Change "five addresses" to "six addresses: the list, add, edit, toggle, delete, clear-done", and add clear-done to "accept `POST` only". Keep the Edit sentence. |
| 2 | `README.md` is missing from the files list; it says `Ran 34 tests`. | Accept | A beginner following the README would think something broke. Update it to `Ran 41 tests`. |
| 3 | `PLAN.md` is missing: F6's heading and the §10 `/clear-done/` row still say 계획 (planned). | Accept | The spec should say what is built. Change both to 구현됨 (implemented). |
| 4 | The plan only lives in a temporary folder. | Accept | Copy this final plan to `docs/plans/clear-done.md` in the same commit, with `Status: built.` |
| 5 | No test checks that the not-done to-dos stay in the same order. | Accept | In `test_clear_done_removes_only_done_todos`, use 4 to-dos (A open, B done, C open, D done) and check the remaining titles are exactly `["A", "C"]`. Test count stays 41. |
