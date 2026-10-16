# Plan: count what's left

Status: built.

Every row marked Accept in "Review objections" at the end is part of this plan, and wins where it
differs from the text above it. So: no `has_todos` (the template uses `{% if todos %}`), the count
comes from `todos.filter(done=False).count()`, there is no `test_the_database_does_the_counting`,
the add/toggle/delete test starts with two to-dos, and there are 40 tests, not 41.

This is F7 in `PLAN.md`. It is planned against our current `main` (commit `d8c4bab`). There, the
list view is a plain function `todo_list` that passes only `todos` to the page. There is no
`page_context` helper and no `todos/tests/` folder: all tests are in `todos/tests.py`.

## What it does

Above the list, the page shows how many to-dos are **not done yet**.

- 3 to-dos, 1 of them done: the page says `2 left`.
- 1 to-do, not done: the page says `1 left`.
- Every to-do is done: the page says `All done`. It never says `0 left`.
- **The list is empty: no count at all.** The page already says "Nothing to do yet. Add something
  above." Saying "All done" next to it would be wrong: nothing was done. Saying "0 left" would only
  repeat it. So the count line is not on the page.
- The number is right after every add, toggle (Done and Undo) and delete. Each of these sends the
  browser back to the list, and the list page counts again each time it loads. No extra work is
  needed for this, but a test checks it.
- An add with a blank title adds nothing, so the count does not change.

**The words.** The spec says `N left`, with no noun. So there is no "1 items left" problem: there is
no "item" word to make plural. `1 left` and `5 left` are both correct English. We do **not** use
Django's `pluralize` filter, because there is nothing to pluralize. (A **filter** is a small helper
in a template that changes a value before it is shown.) A test checks the exact text `1 left`, so
nobody adds "items" later by mistake.

**What counts.** Every to-do in the whole list that has `done = False`. Later, F14 (view filter)
will show only some to-dos. The count must still be for the whole list then. So the count and the
"is the list empty?" question both ask the database about **all** to-dos, not about the `todos`
that the page shows.

**Rules from `PLAN.md` section 11.** No new address and no change to any `POST`. The list page is a
`GET` and only reads. The count is one short line, so it fits a 400px wide phone screen.

## How it is built

No new field, no new address, no migration, no new package.

### 1. `todos/views.py` — two more values for the page

In `todo_list`, add two keys to the dictionary that goes to the template:

```python
def todo_list(request):
    todos = Todo.objects.all()
    return render(
        request,
        "todos/todo_list.html",
        {
            "todos": todos,
            "has_todos": Todo.objects.exists(),
            "remaining_count": Todo.objects.filter(done=False).count(),
        },
    )
```

- `has_todos`: `True` when there is at least one to-do. `.exists()` asks the database only "is
  there one?".
- `remaining_count`: the number of to-dos that are not done. `.count()` makes the database count
  (`SELECT COUNT(*) ...`). We do not load every to-do and count in Python.
- One key per line, so other features that add keys here clash less.
- We do not add a custom manager or QuerySet method (the course's version did). One
  `filter(done=False)` in one place is enough. If a second place needs it later, we move it to the
  model then.

### 2. `todos/templates/todos/todo_list.html` — the count line

Just **before** `<ul>` (after the add form), add:

```html
{% if has_todos %}
  <p class="count">{% if remaining_count %}{{ remaining_count }} left{% else %}All done{% endif %}</p>
{% endif %}
```

- Keep the `<p>` on **one line**, so the tests can match the whole element with `html=True`.
- No new CSS. A plain `<p>` already looks right, and leaving `base.html` alone avoids clashes.

### 3. `AGENTS.md` — the file table

- `todos/views.py` row: add "The list also gets `has_todos` and `remaining_count`."
- The template row: add "and, above the list, how many to-dos are left".

### 4. `PLAN.md` — the F7 heading

Change `### F7. 남은 개수 표시 — 계획` to `— 구현됨`, like F1 to F5.

### Files that do not change

`models.py`, `forms.py`, `urls.py`, `admin.py`, `base.html`, `todo_edit.html`, the migrations.

## Tests

All new tests go in a new class `CountTests(TestCase)` at the end of `todos/tests.py`. A new class
clashes less with tests that other features add to `TodoTests` at the same time.

Every check on the count matches the whole element, for example:

```python
self.assertContains(response, '<p class="count">2 left</p>', html=True)
```

With `html=True`, Django compares whole HTML elements. So a check for `1 left` can never match
`11 left` by mistake.

We write all the tests **first**, run `make test`, and show the person the result **before** the
code changes. Then we change the code and show that every test passes.

**Tests for new behavior.** Each one fails today, because the page has no count yet:

| Test | What it sets up | What it checks | How it fails today |
|---|---|---|---|
| `test_count_shows_how_many_are_left` | 3 to-dos, 1 of them done | the page has `<p class="count">2 left</p>` | `AssertionError`: no count on the page |
| `test_count_says_1_left_without_items` | 1 to-do, not done | the page has `<p class="count">1 left</p>`, and does not contain `item left` or `items left` (not just `item`: the CSS has `align-items`) | `AssertionError`: no count on the page |
| `test_count_says_all_done_when_nothing_is_left` | 2 to-dos, both done | the page has `<p class="count">All done</p>`, and does not contain `0 left` | `AssertionError`: no count on the page |
| `test_count_is_above_the_list` | 1 to-do | `class="count"` is on the page, and comes before `<ul` | `AssertionError`: no count on the page |
| `test_count_follows_add_toggle_and_delete` | nothing | with `follow=True`: `POST` add `Buy milk` gives `1 left`; toggle it gives `All done`; toggle again gives `1 left`; delete it gives no `class="count"` | `AssertionError`: no `1 left` after the add |
| `test_the_database_does_the_counting` | 1 to-do | while the list page loads (`CaptureQueriesContext`), one SQL query has `COUNT` and `todos_todo` in it. Not `assertNumQueries`: later features add queries. | `AssertionError`: no `COUNT` query yet |

**A test that protects what already works.** It **passes** today, and must still pass after:

| Test | What it sets up | What it checks |
|---|---|---|
| `test_no_count_when_the_list_is_empty` | nothing | the page says `Nothing to do yet`, and does not contain `class="count"`, `All done` or ` left<` |

So before the code: 6 fail, 1 passes, and the 34 old tests still pass. After the code: all 41 pass.

## Done when

- `make test` shows `Ran 41 tests` and `OK`. (34 tests today + 7 new tests = 41.)
- `make check` passes. It also proves no migration is missing.
- By hand: `make run`, add three to-dos and check `3 left`. Press Done on one: `2 left`. Press Done
  on the other two: `All done`. Delete them all: no count line, only "Nothing to do yet".

## Files this touches

- `todos/views.py` (`todo_list` only)
- `todos/templates/todos/todo_list.html` (one block just before `<ul>`)
- `todos/tests.py` (new class `CountTests` at the end)
- `AGENTS.md` (file table: views row and template row)
- `PLAN.md` (F7 heading only)

Likely overlap: F6 (clear completed) will also change `todos/views.py`, `todo_list.html`,
`todos/tests.py`, `AGENTS.md` and `PLAN.md`. F8 (result messages) will also put something "above
the list" in `todo_list.html`. Each of these adds its own lines, so a clash is small and easy to fix
by hand.

## Review objections

| # | Objection | Decision | Why |
|---|---|---|---|
| 1 | The spec says "0 left → All done", but the plan hides the count on an empty list and does not update the spec. | Accept | Keep the decision (no count line on an empty list), and change the F7 lines in `PLAN.md` to say so: "할 일이 하나도 없으면 개수 줄을 보이지 않습니다." |
| 2 | `README.md` is missing; it says `Ran 34 tests`. | Accept | Update it to the new count (`Ran 40 tests`, see #4). |
| 3 | Three separate `Todo.objects` queries will each need the owner filter when F11 comes. | Accept | Build one base queryset `todos = Todo.objects.all()` and derive the count from it (`todos.filter(done=False).count()`). |
| 4 | `test_the_database_does_the_counting` tests how, not what, and is weak. | Accept | Drop it. Done when becomes `Ran 40 tests` and `OK` (34 + 6). |
| 5 | `has_todos` is an extra query needed only for F14. | Accept | Use `{% if todos %}` on the base queryset; drop `has_todos`. |
| 6 | The add/toggle/delete test barely checks delete. | Accept | Start with two to-dos: add → `2 left`, toggle → `1 left`, delete the open one → `All done`, delete the last → no count line. |
