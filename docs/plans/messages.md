# Plan: result messages

Status: built.

This is feature **F8** in `PLAN.md`. A *message* here is a one-line note that Django keeps for the
next page only. Django calls this the *messages framework*. It is already turned on in
`config/settings.py` (the app, the middleware and the context processor), so no setting changes.

## What it does

After a change, the list page shows one line above the list. It shows **once**. A reload of the
page does not show it again.

| Action | Message | Kind |
|---|---|---|
| Add, title is good | `Added` | success |
| Add, title is blank or only spaces | `Title can't be blank` | error |
| Add, title is over 200 characters | `Title can't be longer than 200 characters` | error |
| Edit, Save with a good title | `Saved` | success |
| Done (to-do becomes done) | `Marked done` | success |
| Undo (to-do becomes not done) | `Marked not done` | success |
| Delete | `Deleted` | success |

An error message is red. A success message uses the normal text color.

Edge cases:

- **A bad add** saves nothing, still goes back to the list (as today), and shows the reason.
  A POST with no `title` at all counts as blank.
- **A bad edit** does not use a message. It stays on the edit page and shows the field error, as
  today. The error text changes to the same plain words: `Title can't be blank` or
  `Title can't be longer than 200 characters`. This replaces Django's `This field is required.`
- **Cancel** on the edit page is a plain link. It changes nothing, so it shows no message.
- **404 and 405** answers show no message, because nothing changed.
- **A reload** after the message shows the list without it. The browser never re-sends the POST,
  because every change ends with a redirect (PLAN.md section 11).
- **Messages belong to one browser**, not to the list. Another person who opens the site does not
  see your message. (Django stores it in a cookie or the session of that browser.)
- **The message text never contains the to-do title.** So a title with HTML in it cannot get into
  the message.
- **In a browser, `""` and 201 characters can't be sent**, because the add input has `required`
  and `maxlength="200"`. Those two cases are tested with the test client only. To try an error
  message by hand, add a spaces-only title.

## How it is built

- `todos/forms.py`: in `TodoForm.Meta`, add `error_messages` for `title`:
  `"required": "Title can't be blank"` and `"max_length": "Title can't be longer than 200 characters"`.
  Both the add and the edit page use this form, so both get the new words. (Checked: Django uses
  `required` for empty, spaces-only and missing titles, and `max_length` for 201 characters.)
- `todos/views.py`: `from django.contrib import messages`. Then:
  - `todo_add`: if valid, `form.save()` and `messages.success(request, "Added")`. If not valid,
    `messages.error(request, error)` for each error in `form.errors["title"]`. Still redirect.
  - `todo_edit`: after `form.save()`, `messages.success(request, "Saved")`, then redirect.
  - `todo_toggle`: after save, `messages.success(request, "Marked done" if todo.done else "Marked not done")`.
  - `todo_delete`: after delete, `messages.success(request, "Deleted")`.
- `todos/templates/todos/todo_list.html`: between the add form and the `<ul>` of to-dos, add:
  `{% if messages %}<ul class="messages">{% for message in messages %}<li class="{{ message.tags }}">{{ message }}</li>{% endfor %}</ul>{% endif %}`.
  Looping over `messages` is what marks them as shown, so they are gone on the next page.
- `todos/templates/todos/base.html`: `.messages li { border-bottom: none; padding: 0.25rem 0; }`
  (the plain `li` rule adds a border), and one shared red rule for field errors and error
  messages: `.errorlist, .messages .error { color: #b00; }`. The color moved out of `.errorlist`.
- `PLAN.md`: first, per its own rule. F2 last bullet: a bad add now shows the reason. F5 gets a
  line with the two new error sentences. F8 status becomes Built, with the full message table;
  the `Cleared done` row is marked `(with F6)`, because F6 is not on this branch.
- `AGENTS.md`: the `todos/views.py` row says each change adds a one-line message.
- `README.md`: `Ran 34 tests` becomes `Ran 44 tests`.

No model change, so no migration. No new URL. No new package.

## Tests

All new tests go in `TodoTests` in `todos/tests.py`, under a comment `# F8: result messages`.
Write them first and run `make test`. Each one fails today, because today no view adds a message
and no page shows one. Then write the code, and they pass.

To read the messages a page showed, add one small helper method to `TodoTests`:
`def shown_messages(self, response): return [(str(m), m.level_tag) for m in response.context["messages"]]`.
It returns `(text, kind)` pairs, so each test also checks success vs error.
Each test posts with `follow=True`, so `response` is the list page after the redirect. This is
easier than `assertContains` for the text, because Django writes `can't` in HTML as `can&#x27;t`.
Two tests also read the HTML, with `assertContains(..., html=True)`.

| Test | What it checks | How it fails today |
|---|---|---|
| `test_add_shows_added_message` | Add `Buy milk` → messages are `[("Added", "success")]`, and the page has `<li class="success">Added</li>`. | The list is `[]`. |
| `test_message_is_gone_after_reload` | Add, see `["Added"]`. Then `GET /` again → `[]`. | The first check fails: `[]`, not `["Added"]`. |
| `test_edit_shows_saved_message` | Edit with `Call mum` → `["Saved"]`. | `[]`. |
| `test_done_shows_marked_done_message` | Toggle an open to-do → `["Marked done"]`. | `[]`. |
| `test_undo_shows_marked_not_done_message` | Toggle a done to-do → `["Marked not done"]`. | `[]`. |
| `test_delete_shows_deleted_message` | Delete → `["Deleted"]`. | `[]`. |
| `test_blank_add_shows_reason` | Add `""` → `[("Title can't be blank", "error")]`, no to-do saved, the page has `<li class="error">Title can&#x27;t be blank</li>`, and the message block comes after the add form and before the `<ul>` of to-dos. | `[]`. |
| `test_add_without_title_key_shows_reason` | Post `{}` → `[("Title can't be blank", "error")]`, and no to-do saved. | `[]`. |
| `test_spaces_only_add_shows_reason` | Add `"   "` → `["Title can't be blank"]`. | `[]`. |
| `test_too_long_add_shows_reason` | Add 201 × `x` → `["Title can't be longer than 200 characters"]`. | `[]`. |

That is **10 new tests**. (The other rows check the kind too: `success` or `error`.)

Two existing tests change their expectation:

- `test_edit_rejects_blank_title_and_keeps_old_one`: replace
  `assertContains(response, "This field is required")` with
  `assertFormError(response.context["form"], "title", "Title can't be blank")`.
  Change it together with the new tests. It fails today (the error is still `This field is required.`)
  and passes after the change to `forms.py`.
- `test_edit_rejects_too_long_title`: add
  `assertFormError(response.context["form"], "title", "Title can't be longer than 200 characters")`.
  It fails today (Django's `Ensure this value has at most 200 characters (it has 201).`).

No other test changes. The tests that check redirects, 404 and 405 do not use `follow=True`, so
they still pass. `test_done_todo_is_marked_and_offers_undo` checks that `>Done<` is not on the
page; the message `Marked done` does not match `>Done<`, and that test loads the list with a plain
`GET`, so it has no message anyway.

## Done when

`make test` shows `Ran 44 tests` and `OK` (34 today + 10 new). `make check` passes.

## Files this touches

- `todos/views.py`
- `todos/forms.py`
- `todos/templates/todos/todo_list.html`
- `todos/templates/todos/base.html`
- `todos/tests.py`
- `PLAN.md`
- `AGENTS.md` (the `todos/views.py` row)
- `README.md` (the test count)
- `docs/plans/messages.md` (this plan)

Overlap to watch: F6 (Clear done) and F7 (N left) also change `todo_list.html`, `views.py`,
`tests.py`, `PLAN.md` and the README test count. F7 also puts a line above the list. If F6 is
built at the same time, its view should add its own message (for example `Cleared done`) once
this feature is in.

## Review objections

| # | Objection | Decision | Why |
|---|---|---|---|
| 1 | Building F8 at the same time as F6 and F7 goes against PLAN.md §12, and the Clear-done message is not decided. | Partly accept | Reject the order part: the three are built in parallel on purpose, and they are **merged** in §12 order (F6 → F7 → F8). Accept the message part: the Clear-done message is `Cleared done` (success). This branch does not have the clear-done view, so that one line is added when this branch is brought up to date with `main` after F6 is merged. Put it in the PLAN.md F8 table now. |
| 2 | Some stated behavior has no test: add with no `title` key, the edit page's too-long error text, and error vs success kind. | Accept | Add a test for add with `{}` (one new test). Add `assertFormError(..., "Title can't be longer than 200 characters")` to the existing too-long edit test. Make the helper return `(text, level_tag)` so tests check the kind. Done when becomes `Ran 44 tests` and `OK`. |
| 3 | PLAN.md edits miss the new edit error words and the full message table. | Accept | Put the full message table and both error sentences in F8, add a line to F5 about the new edit error words, and update the `todos/views.py` row in AGENTS.md. |
| 4 | In a browser, "" and 201 characters can't be sent because of `required` and `maxlength`. | Accept | Add under Edge cases: those two are tested by the test client only; by hand, try a spaces-only title. |
| 5 | The plan file is not in the repo. | Accept | Commit it as `docs/plans/messages.md` with `Status: built.` |
| 6 | A second CSS rule copies the error red. | Accept | Use one rule for both, e.g. `.errorlist, .messages .error { color: #b00; }`. |

## Result review

| # | Objection | Decision | Why |
|---|---|---|---|
| 1 | No test reads the HTML. | Accept | `test_blank_add_shows_reason` now checks the rendered `<li class="error">` (with `&#x27;`, `html=True`), and that the message block is between the add form and the `<ul>` of to-dos, by comparing positions in the page. |
| 2 | The body of this file is out of date. | Accept | Counts are now 44 tests and 10 new; the CSS is described as built (shared `.errorlist, .messages .error` rule); the browser edge case from objection 4 is under Edge cases; AGENTS.md and this file are in "Files this touches". |
| 3 | The `Cleared done` row in PLAN.md F8 is not true on this branch. | Accept | The row is marked `(with F6)`. It is wired up when this branch is brought up to date after F6 merges. |
| 4 | `test_add_shows_added_message` duplicates the first check of `test_message_is_gone_after_reload`. | Accept | It is kept, and now also checks the HTML `<li class="success">Added</li>` (`html=True`). The count stays 44. |

## Merge with F6 and F7

This branch was brought up to date with F6 (clear done) and F7 (count) before its pull request.
Conflicts were in `AGENTS.md`, `README.md`, `todos/templates/todos/todo_list.html` and
`todos/tests.py`; each kept both sides. On the list page the order is: add form, messages, count,
list. The clear-done view now adds `Cleared done`, with a new test
`test_clear_done_shows_cleared_done_message` (it failed first with `[] != [('Cleared done', 'success')]`),
and the `(with F6)` mark is gone from PLAN.md. Done when: `Ran 58 tests` and `OK`.
