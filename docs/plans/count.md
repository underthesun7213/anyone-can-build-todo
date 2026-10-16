# Plan: count what's left

Status: built.

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
- An add with a blank title adds nothing, so the count does not change. A test checks this too.

**The words.** The spec says `N left`, with no noun. So there is no "1 items left" problem: there is
no "item" word to make plural. `1 left` and `5 left` are both correct English. We do **not** use
Django's `pluralize` filter, because there is nothing to pluralize. (A **filter** is a small helper
in a template that changes a value before it is shown.) A test checks the exact text `1 left`, so
nobody adds "items" later by mistake.

**What counts.** Every to-do that has `done = False`. Both the count and the "is the list empty?"
check use `todos`, the list that the page shows. Today that list is every to-do, so this is the
whole list. **This is on purpose for now**: one base queryset means one place to add the owner
filter when F11 (accounts) comes. (A **queryset** is Django's description of a database question;
it runs when the result is needed.) Later, F14 (view filter) will show only some to-dos. **F14 must
change this**: the count and the empty check must then ask about the whole list, not about the
filtered `todos` that the page shows.

**Rules from `PLAN.md` section 11.** No new address and no change to any `POST`. The list page is a
`GET` and only reads. The count is one short line, so it fits a 400px wide phone screen.

## How it is built

No new field, no new address, no migration, no new package.

### 1. `todos/views.py` — one more value for the page

In `todo_list`, add one key to the dictionary that goes to the template:

```python
def todo_list(request):
    todos = Todo.objects.all()
    return render(
        request,
        "todos/todo_list.html",
        {
            "todos": todos,
            "remaining_count": todos.filter(done=False).count(),
        },
    )
```

- `remaining_count`: the number of to-dos that are not done. It is built from the same `todos`
  queryset. `.count()` makes the database count (`SELECT COUNT(*) ...`). We do not load every
  to-do and count in Python.
- One key per line, so other features that add keys here clash less.
- We do not add a custom manager or QuerySet method (the course's version did). One
  `filter(done=False)` in one place is enough. If a second place needs it later, we move it to the
  model then.

### 2. `todos/templates/todos/todo_list.html` — the count line

Just **before** `<ul>` (after the add form), add:

```html
{% if todos %}
  <p class="count">{% if remaining_count %}{{ remaining_count }} left{% else %}All done{% endif %}</p>
{% endif %}
```

- `{% if todos %}` is true when the list has at least one to-do. The page loops over `todos` just
  below, so Django loads the list once and uses it for both.
- Keep the `<p>` on **one line**, so the tests can match the whole element with `html=True`.
- No new CSS. A plain `<p>` already looks right, and leaving `base.html` alone avoids clashes.

### 3. `AGENTS.md` — the file table

- `todos/views.py` row: add "The list also gets `remaining_count`."
- The template row: say the page shows how many to-dos are left, above the list.

### 4. `PLAN.md` — F7

Change `### F7. Show how many are left — Planned` to `— Built`, like F1 to F5. Add the line
"If there are no to-dos at all, the count line is not shown."

### 5. `README.md` — the test count

Change `Ran 34 tests` to `Ran 40 tests`.

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

**Tests for new behavior.** Each one fails before the code, because the page has no count yet:

| Test | What it sets up | What it checks | How it fails before the code |
|---|---|---|---|
| `test_count_shows_how_many_are_left` | 3 to-dos, 1 of them done | the page has `<p class="count">2 left</p>` | `AssertionError`: no count on the page |
| `test_count_says_1_left_without_items` | 1 to-do, not done | the page has `<p class="count">1 left</p>`, and does not contain `item left` or `items left` (not just `item`: the CSS has `align-items`) | `AssertionError`: no count on the page |
| `test_count_says_all_done_when_nothing_is_left` | 2 to-dos, both done | the page has `<p class="count">All done</p>`, and does not contain `0 left` | `AssertionError`: no count on the page |
| `test_count_is_above_the_list` | 1 to-do | `class="count"` is on the page, and comes before `<ul` | `AssertionError`: no count on the page |
| `test_count_follows_add_toggle_and_delete` | 1 to-do, `Call mum` | with `follow=True`: add `Buy milk` gives `2 left`; add a blank title (`"  "`) still gives `2 left`; toggle `Buy milk` (Done) gives `1 left`; toggle it again (Undo) gives `2 left`; toggle it again (Done) gives `1 left`; delete `Call mum` (the open one) gives `All done`; delete `Buy milk` gives no `class="count"` | `AssertionError`: no `2 left` after the add |

**A test that protects what already works.** It **passes** before the code, and must still pass
after:

| Test | What it sets up | What it checks |
|---|---|---|
| `test_no_count_when_the_list_is_empty` | nothing | the page says `Nothing to do yet`, and does not contain `class="count"`, `All done` or ` left<` |

So before the code: 5 fail, 1 passes, and the 34 old tests still pass. After the code: all 40 pass.

## Done when

- `make test` shows `Ran 40 tests` and `OK`. (34 old tests + 6 new tests = 40.)
- `make check` passes. It also proves no migration is missing.
- By hand: `make run`, add three to-dos and check `3 left`. Press Done on one: `2 left`. Press Undo
  on it: `3 left`. Press Done on all three: `All done`. Delete them all: no count line, only
  "Nothing to do yet".

## Files this touches

- `todos/views.py` (`todo_list` only)
- `todos/templates/todos/todo_list.html` (one block just before `<ul>`)
- `todos/tests.py` (new class `CountTests` at the end)
- `AGENTS.md` (file table: views row and template row)
- `PLAN.md` (F7 heading and one new F7 line)
- `README.md` (the test count)

Likely overlap: F6 (clear completed) will also change `todos/views.py`, `todo_list.html`,
`todos/tests.py`, `AGENTS.md`, `PLAN.md` and `README.md`. F8 (result messages) will also put
something "above the list" in `todo_list.html`. Each of these adds its own lines, so a clash is
small and easy to fix by hand.

## Review objections

| # | Objection | Decision | Why |
|---|---|---|---|
| 1 | The spec says "0 left → All done", but the plan hides the count on an empty list and does not update the spec. | Accept | Keep the decision (no count line on an empty list), and change the F7 lines in `PLAN.md` to say so: "If there are no to-dos at all, the count line is not shown." |
| 2 | `README.md` is missing; it says `Ran 34 tests`. | Accept | Update it to the new count (`Ran 40 tests`, see #4). |
| 3 | Three separate `Todo.objects` queries will each need the owner filter when F11 comes. | Accept | Build one base queryset `todos = Todo.objects.all()` and derive the count from it (`todos.filter(done=False).count()`). |
| 4 | `test_the_database_does_the_counting` tests how, not what, and is weak. | Accept | Drop it. Done when becomes `Ran 40 tests` and `OK` (34 + 6). |
| 5 | `has_todos` is an extra query needed only for F14. | Accept | Use `{% if todos %}` on the base queryset; drop `has_todos`. |
| 6 | The add/toggle/delete test barely checks delete. | Accept | Start with two to-dos: add → `2 left`, toggle → `1 left`, delete the open one → `All done`, delete the last → no count line. |

## Result review

| # | Objection | Decision | Why |
|---|---|---|---|
| 1 | The body of this file still described the dropped version (`has_todos`, three queries, `test_the_database_does_the_counting`, the old add/toggle/delete test, `Ran 41 tests`). | Accept | Rewrote the text and the code samples to match what was built, and removed the override note. |
| 2 | "What counts" said the empty check asks about all to-dos; it now uses the shown list. | Accept | Say that this is on purpose for now (one base queryset for F11), and that F14 (view filter) must change it to a check on the whole list. |
| 3 | `test_count_follows_add_toggle_and_delete` does not test Undo. | Accept | After the first toggle gives `1 left`, toggle the same to-do back and check `2 left`, then go on. |
| 4 | The plan promises "a blank-title add does not change the count", but no test checks it; `README.md` is missing from "Files this touches". | Accept | Add a step to the same test: add `{"title": "  "}` with `follow=True` and check the count is still `2 left`. Add `README.md` to the list. These are steps in an existing test, so the count stays 40. |
