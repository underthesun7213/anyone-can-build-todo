# Product spec — To-do app

This document says **what the app does**. It does not say how it is built.
Each feature has a status. **Built** means it works now. **Planned** means it does not exist yet.
When a feature is added or changed, change this document first, then the tests and the code.

## 1. Overview

- **In one line**: the simplest web to-do list — write a to-do, finish it, delete it.
- **Who it is for**: anyone with a browser. No install and no sign-up.
- **Scope today**: there is one list, and everyone who opens the site sees the same list.
- **Where data lives**: in the server's database. It stays after the browser is closed.

## 2. Terms

| Term | Meaning |
|---|---|
| To-do | One line in the list. It has a title, whether it is done, and when it was made. |
| Done | A mark that a to-do is finished. It can be undone. |
| List | The first page. It shows every to-do in the order it was made. |
| Admin site | `/admin/`. Django's built-in page where an operator sees and changes the data directly. |

## 3. Out of scope (what we do not build)

- Sharing, working together, notifications (email or push), repeating to-dos, attachments, tags, sub-tasks.
- A mobile app. It is enough that the web page works at phone width.
- While there are no accounts, there is no idea of "mine". (See section 5.)

## 4. Features — managing to-dos

### F1. See the list — Built

- Opening `/` shows every to-do **in the order it was made** (oldest at the top).
- Each line has the title, an Edit link, a Done/Undo button and a Delete button.
- A done to-do has its title struck through and in grey. Its button says Undo.
- If there are no to-dos, one line says "Nothing to do yet. Add something above."
- Above the list are an input box for a new to-do and an Add button. When the page opens, the cursor is in the box.

### F2. Add a to-do — Built

- Type a title in the box and press Add or Enter. The to-do is added at the bottom of the list.
- Title rules:
  - Spaces at the start and end are removed before saving.
  - A blank title, or one with only spaces, is not saved.
  - A title longer than 200 characters is not saved. The box also accepts at most 200 characters.
- After saving, the browser goes back to the list. The box is empty.
- If a rule is broken, nothing is saved and the browser goes back to the list. The reason is shown once, in red, above the list. (F8)

### F3. Mark done and undo — Built

- Done marks a to-do as done; Undo marks it as not done. This can be switched any number of times.
- After the change, the browser goes back to the list.
- Changing a to-do that does not exist gives a 404 (page not found) response.

### F4. Delete — Built

- Delete removes the to-do at once. There is no confirmation. It cannot be brought back.
- After deleting, the browser goes back to the list.
- Deleting a to-do that does not exist gives a 404 response.

### F5. Edit the title — Built

- Edit on the list opens `/<number>/edit/`. The box holds the current title, and the cursor is in it.
- Save saves and goes back to the list. Cancel changes nothing and goes back to the list.
- The title rules are the same as F2. If a rule is broken, nothing is saved and the same page shows a red error. The old title stays.
- The error says "Title can't be blank" or "Title can't be longer than 200 characters". (F8 replaced Django's default wording.)
- Editing does not change whether the to-do is done, or when it was made.
- Opening a number that does not exist gives a 404 response.

### F6. Clear all done to-dos at once — Built

- The list has a "Clear done" button. If no to-do is done, the button is not shown.
- Pressing it removes every done to-do. Not-done ones stay.
- There is no confirmation. They cannot be brought back.

### F7. Show how many are left — Built

- Above the list, the number of not-done to-dos is shown as "N left". When it is 0, it says "All done".
- If there are no to-dos at all, the count line is not shown.
- After every add, done/undo and delete, the number is right at once.

### F8. Result messages — Built

- After something changes, a one-line message shows above the list (between the input box and the list) **once**. It is gone after a reload.

| Action | Message | Kind |
|---|---|---|
| Add, title follows the rules | `Added` | success |
| Add, blank title, spaces only, or no title | `Title can't be blank` | error |
| Add, title longer than 200 characters | `Title can't be longer than 200 characters` | error |
| Edit, Save | `Saved` | success |
| Done (becomes done) | `Marked done` | success |
| Undo (becomes not done) | `Marked not done` | success |
| Delete | `Deleted` | success |
| Clear done (F6) | `Cleared done` | success |

- Error messages are red; success messages use the normal text color.
- On the edit page, a broken rule does not use a message. The same page shows one of the same two sentences as an error: "Title can't be blank", "Title can't be longer than 200 characters".
- Cancel, 404 and 405 change nothing, so they show no message.
- A message shows only in that browser. Other people do not see it.
- A message never contains a to-do's title.

## 5. Features — accounts and your own list (Planned)

When this section is built, "everyone sees the same list" becomes "each person has their own list".

### F9. Sign up — Planned

- At `/accounts/signup/`, sign up with a username and a password (typed twice).
- A username that already exists, or a password that is too short or too common, is refused, and the reason is shown. (Django's default rules)
- After signing up, the person is logged in and the list opens.

### F10. Log in / log out — Planned

- At `/accounts/login/`, log in with a username and password. If they are wrong, the reason is shown.
- Every page shows the logged-in username and a Log out button at the top. Logging out works only with the button (POST).

### F11. Only my to-dos are shown — Planned

- Every to-do has an owner. The list shows only mine.
- Someone else's to-do cannot be edited, marked done or deleted, even if its number is known. Trying gives a 404 response.

### F12. You must log in to use it — Planned

- Opening the list or the edit page without logging in sends the person to the login page. After logging in, they go back to the page they wanted.

## 6. Features — more useful (Planned)

### F13. Due date — Planned

- A to-do can have one date. It is optional.
- The list shows the due date. A not-done to-do whose date is before today is shown in red.
- It can be set and changed on both the add form and the edit page.

### F14. View filter — Planned

- Above the list are three views: All / Active / Done. The default is All.
- The address tells them apart: `/?show=active`, `/?show=done`. A reload keeps the same view.
- A view only reads. It never changes data.

### F15. Priority — Planned

- One of Low / Normal / High. The default is Normal.
- The list shows High first; within the same priority, in the order made.
- High has a mark that stands out (a color or an icon).

## 7. Features — the page (Planned)

### F16. Done toggle without a reload — Planned

- Done/Undo changes only that line, without reloading the whole page.
- With JavaScript turned off, it must still work like F3.

### F17. Korean interface — Planned

- Buttons and messages are shown in Korean. If the browser's language is not Korean, they are in English.

### F18. Accessibility — Planned

- Every feature can be used with the keyboard alone. The Tab order is the same as the order on the page.
- Every button and input box has a name that a screen reader can read.

## 8. Running it

### F19. Admin site — Built

- At `/admin/`, an operator who logs in can see every to-do in a table, change it and delete it.
- An operator account is made only with the `createsuperuser` command. It cannot be made from a page.

### F20. Put it on the internet — Planned

- Anyone can reach it at one HTTPS address. A request over HTTP is sent to HTTPS.
- Secret values (the secret key, the allowed hosts, whether debug is on) go only in the server's environment variables. They are not in the code.

### F21. A database that does not lose data — Planned

- To-dos stay after the server restarts or is deployed again. (PostgreSQL instead of the SQLite file.)
- On a laptop it still uses SQLite. The code is the same; only the environment variables differ.

## 9. Data

### What one to-do (Todo) has

| Field | Status | Rule |
|---|---|---|
| Title `title` | Built | 1 to 200 characters. Spaces at the start and end are removed. |
| Done `done` | Built | True or false. Default false. |
| Made at `created_at` | Built | Recorded automatically when saved. Cannot be changed. |
| Owner `owner` | Planned (F11) | One signed-up user. |
| Due date `due` | Planned (F13) | A date. Can be empty. |
| Priority `priority` | Planned (F15) | Low/Normal/High. Default Normal. |

## 10. Addresses (URLs)

| Address | Method | What it does | Status |
|---|---|---|---|
| `/` | GET | See the list (F1) | Built |
| `/add/` | POST | Add (F2) | Built |
| `/<number>/edit/` | GET, POST | Edit page, save (F5) | Built |
| `/<number>/toggle/` | POST | Done/undo (F3) | Built |
| `/<number>/delete/` | POST | Delete (F4) | Built |
| `/clear-done/` | POST | Delete all done to-dos (F6) | Built |
| `/?show=active` etc. | GET | View filter (F14) | Planned |
| `/accounts/signup/` | GET, POST | Sign up (F9) | Planned |
| `/accounts/login/`, `/accounts/logout/` | GET, POST / POST | Log in, log out (F10) | Planned |
| `/admin/` | GET, POST | Admin site (F19) | Built |

## 11. Rules for every feature

- **Every request that changes data is a POST.** Opening an address with GET never changes data. Opening a changing address with GET gives a 405 (method not allowed) response.
- Every request about **a to-do that does not exist** gives a 404 response.
- **After a change, the browser goes back to the list.** Pressing reload does not make the same change twice.
- **The page works at phone width (about 400px)** with no sideways scrolling.
- Every feature's behavior is protected by **automated tests**. When a line in this document changes, the tests change too.

## 12. Build order

Lower numbers are built first. One feature is one commit.

1. F6 → F7 → F8 (first, the ones that do not change the data structure)
2. F9 → F10 → F11 → F12 (accounts; F11 changes the data structure)
3. F13 → F14 → F15
4. F20 → F21
5. F16 → F17 → F18 (the ones the app works without)
