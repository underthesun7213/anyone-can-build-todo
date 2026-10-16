# Plan: edit a to-do

Status: **built and reviewed**, on branch `feature/edit`. Not merged yet.

## What it does

Each to-do on the list has an **Edit** link. It opens `/<pk>/edit/`, a page with the current title in
a box. **Save** changes the title and goes back to the list. **Cancel** goes back without a change.

- A blank title, or one longer than 200 characters, is rejected. The page shows the error, and the
  old title is kept.
- Editing changes only the title. `done` and `created_at` stay the same.
- A to-do that does not exist gives 404.
- The edit address accepts only `GET` (show the form) and `POST` (save). Other methods give 405.

## How it is built

- `todos/urls.py`: a fifth address, `<int:pk>/edit/`, named `todo_edit`.
- `todos/views.py`: `todo_edit`, using `get_object_or_404` and `TodoForm(instance=todo)`.
- `todos/forms.py`: the same `TodoForm` as the add form. Its widget sets `aria-label` and `autofocus`.
- `todos/templates/todos/base.html`: the shared page frame and CSS, so the list and edit pages match.
- `todos/templates/todos/todo_edit.html`: the edit page. It renders the box with `{{ form.title }}`.

## Done when

`Ran 34 tests in 3.329s` `OK` — all 34 tests pass.

## Review objections

The review was done in a new session, from the diff. Each objection, and what was decided:

| # | Objection | Decision | Why |
|---|---|---|---|
| 1 | The edit box was hand-written HTML. It copied the 200 limit, and showed `None` when the POST had no title. | Accept | Use what Django already has. Now `{{ form.title }}`. Test: `test_edit_without_title_key_does_not_show_none`. |
| 2 | `todo_edit` accepted every HTTP method. | Accept | Only GET and POST make sense. Test: `test_edit_rejects_other_methods`. |
| 3 | The test for a blank title did not check that the error is shown. | Accept | Added `assertContains(response, "This field is required")`. |
| 4 | The edit form borrowed the `add` CSS class. | Accept | Renamed to `inline`, used by both forms. |
| 5 | `AGENTS.md` said "four addresses" and missed the new files. | Accept | Updated. |
| 6 | `TodoForm`'s docstring said "the add form". | Accept | Updated. |
| 7 | Local `main` and the course's `main` had split; the test count would be wrong after a merge. | Reject | I forked the course repo and work in my own fork, so the split from the course repo does not matter here. |
