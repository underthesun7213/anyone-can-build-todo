from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .forms import TodoForm
from .models import Todo


class TodoTests(TestCase):
    def test_list_page_loads(self):
        response = self.client.get(reverse("todo_list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Nothing to do yet")

    def test_add_a_todo(self):
        self.client.post(reverse("todo_add"), {"title": "Buy milk"})
        self.assertEqual(Todo.objects.get().title, "Buy milk")

    def test_empty_title_is_not_added(self):
        self.client.post(reverse("todo_add"), {"title": "   "})
        self.assertEqual(Todo.objects.count(), 0)

    def test_too_long_title_is_not_added(self):
        self.client.post(reverse("todo_add"), {"title": "x" * 201})
        self.assertEqual(Todo.objects.count(), 0)

    def test_toggle_marks_done_and_back(self):
        todo = Todo.objects.create(title="Read chapter 3")
        self.client.post(reverse("todo_toggle", args=[todo.pk]))
        todo.refresh_from_db()
        self.assertTrue(todo.done)
        self.client.post(reverse("todo_toggle", args=[todo.pk]))
        todo.refresh_from_db()
        self.assertFalse(todo.done)

    def test_delete_removes_it(self):
        todo = Todo.objects.create(title="Call home")
        self.client.post(reverse("todo_delete", args=[todo.pk]))
        self.assertEqual(Todo.objects.count(), 0)

    def test_list_links_to_edit_page(self):
        todo = Todo.objects.create(title="Call home")
        response = self.client.get(reverse("todo_list"))
        self.assertContains(response, reverse("todo_edit", args=[todo.pk]))

    def test_edit_page_shows_current_title(self):
        todo = Todo.objects.create(title="Call home")
        response = self.client.get(reverse("todo_edit", args=[todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'value="Call home"')

    def test_edit_saves_new_title(self):
        todo = Todo.objects.create(title="Call home")
        response = self.client.post(
            reverse("todo_edit", args=[todo.pk]), {"title": "Call mum"}
        )
        self.assertRedirects(response, reverse("todo_list"))
        todo.refresh_from_db()
        self.assertEqual(todo.title, "Call mum")

    def test_edit_rejects_blank_title_and_keeps_old_one(self):
        todo = Todo.objects.create(title="Call home")
        response = self.client.post(reverse("todo_edit", args=[todo.pk]), {"title": ""})
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "title", "Title can't be blank")
        todo.refresh_from_db()
        self.assertEqual(todo.title, "Call home")

    def test_edit_without_title_key_does_not_show_none(self):
        todo = Todo.objects.create(title="Call home")
        response = self.client.post(reverse("todo_edit", args=[todo.pk]), {})
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'value="None"')

    def test_edit_rejects_other_methods(self):
        todo = Todo.objects.create(title="Call home")
        url = reverse("todo_edit", args=[todo.pk])
        self.assertEqual(self.client.put(url).status_code, 405)
        self.assertEqual(self.client.delete(url).status_code, 405)

    def test_edit_missing_todo_is_404(self):
        response = self.client.get(reverse("todo_edit", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_edit_rejects_too_long_title(self):
        todo = Todo.objects.create(title="Call home")
        response = self.client.post(
            reverse("todo_edit", args=[todo.pk]), {"title": "x" * 201}
        )
        self.assertFormError(
            response.context["form"],
            "title",
            "Title can't be longer than 200 characters",
        )
        todo.refresh_from_db()
        self.assertEqual(todo.title, "Call home")

    def test_edit_keeps_done_and_created_at(self):
        todo = Todo.objects.create(title="Call home", done=True)
        self.client.post(reverse("todo_edit", args=[todo.pk]), {"title": "Call mum"})
        changed = Todo.objects.get(pk=todo.pk)
        self.assertTrue(changed.done)
        self.assertEqual(changed.created_at, todo.created_at)

    # F1: how the list looks

    def test_list_is_in_creation_order(self):
        Todo.objects.create(title="First")
        Todo.objects.create(title="Second")
        response = self.client.get(reverse("todo_list"))
        self.assertEqual(
            [t.title for t in response.context["todos"]], ["First", "Second"]
        )

    def test_done_todo_is_marked_and_offers_undo(self):
        Todo.objects.create(title="Buy milk", done=True)
        response = self.client.get(reverse("todo_list"))
        self.assertContains(response, 'class="done"')
        self.assertContains(response, ">Undo<")
        self.assertNotContains(response, ">Done<")

    def test_open_todo_offers_done(self):
        Todo.objects.create(title="Buy milk")
        response = self.client.get(reverse("todo_list"))
        self.assertNotContains(response, 'class="done"')
        self.assertContains(response, ">Done<")

    # Rule: every change sends the browser back to the list

    def test_add_redirects_to_list(self):
        response = self.client.post(reverse("todo_add"), {"title": "Buy milk"})
        self.assertRedirects(response, reverse("todo_list"))

    def test_invalid_add_still_redirects_to_list(self):
        response = self.client.post(reverse("todo_add"), {"title": ""})
        self.assertRedirects(response, reverse("todo_list"))

    def test_toggle_redirects_to_list(self):
        todo = Todo.objects.create(title="Buy milk")
        response = self.client.post(reverse("todo_toggle", args=[todo.pk]))
        self.assertRedirects(response, reverse("todo_list"))

    def test_delete_redirects_to_list(self):
        todo = Todo.objects.create(title="Buy milk")
        response = self.client.post(reverse("todo_delete", args=[todo.pk]))
        self.assertRedirects(response, reverse("todo_list"))

    # Rule: a missing to-do is 404

    def test_toggle_missing_todo_is_404(self):
        response = self.client.post(reverse("todo_toggle", args=[999]))
        self.assertEqual(response.status_code, 404)

    def test_delete_missing_todo_is_404(self):
        response = self.client.post(reverse("todo_delete", args=[999]))
        self.assertEqual(response.status_code, 404)

    # Rule: only POST changes data; GET on a changing address is 405

    def test_get_on_add_is_not_allowed(self):
        response = self.client.get(reverse("todo_add"))
        self.assertEqual(response.status_code, 405)

    def test_get_on_toggle_is_not_allowed(self):
        todo = Todo.objects.create(title="Buy milk")
        response = self.client.get(reverse("todo_toggle", args=[todo.pk]))
        self.assertEqual(response.status_code, 405)
        todo.refresh_from_db()
        self.assertFalse(todo.done)

    def test_get_on_delete_is_not_allowed(self):
        todo = Todo.objects.create(title="Buy milk")
        response = self.client.get(reverse("todo_delete", args=[todo.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertEqual(Todo.objects.count(), 1)

    # F8: result messages

    def shown_messages(self, response):
        """The messages the page showed, as (text, kind) pairs."""
        return [(str(m), m.level_tag) for m in response.context["messages"]]

    def test_add_shows_added_message(self):
        response = self.client.post(
            reverse("todo_add"), {"title": "Buy milk"}, follow=True
        )
        self.assertEqual(self.shown_messages(response), [("Added", "success")])

    def test_message_is_gone_after_reload(self):
        response = self.client.post(
            reverse("todo_add"), {"title": "Buy milk"}, follow=True
        )
        self.assertEqual(self.shown_messages(response), [("Added", "success")])
        response = self.client.get(reverse("todo_list"))
        self.assertEqual(self.shown_messages(response), [])

    def test_edit_shows_saved_message(self):
        todo = Todo.objects.create(title="Call home")
        response = self.client.post(
            reverse("todo_edit", args=[todo.pk]), {"title": "Call mum"}, follow=True
        )
        self.assertEqual(self.shown_messages(response), [("Saved", "success")])

    def test_done_shows_marked_done_message(self):
        todo = Todo.objects.create(title="Buy milk")
        response = self.client.post(reverse("todo_toggle", args=[todo.pk]), follow=True)
        self.assertEqual(self.shown_messages(response), [("Marked done", "success")])

    def test_undo_shows_marked_not_done_message(self):
        todo = Todo.objects.create(title="Buy milk", done=True)
        response = self.client.post(reverse("todo_toggle", args=[todo.pk]), follow=True)
        self.assertEqual(
            self.shown_messages(response), [("Marked not done", "success")]
        )

    def test_delete_shows_deleted_message(self):
        todo = Todo.objects.create(title="Buy milk")
        response = self.client.post(reverse("todo_delete", args=[todo.pk]), follow=True)
        self.assertEqual(self.shown_messages(response), [("Deleted", "success")])

    def test_blank_add_shows_reason(self):
        response = self.client.post(reverse("todo_add"), {"title": ""}, follow=True)
        self.assertEqual(
            self.shown_messages(response), [("Title can't be blank", "error")]
        )
        self.assertEqual(Todo.objects.count(), 0)

    def test_spaces_only_add_shows_reason(self):
        response = self.client.post(reverse("todo_add"), {"title": "   "}, follow=True)
        self.assertEqual(
            self.shown_messages(response), [("Title can't be blank", "error")]
        )

    def test_add_without_title_key_shows_reason(self):
        response = self.client.post(reverse("todo_add"), {}, follow=True)
        self.assertEqual(
            self.shown_messages(response), [("Title can't be blank", "error")]
        )
        self.assertEqual(Todo.objects.count(), 0)

    def test_too_long_add_shows_reason(self):
        response = self.client.post(
            reverse("todo_add"), {"title": "x" * 201}, follow=True
        )
        self.assertEqual(
            self.shown_messages(response),
            [("Title can't be longer than 200 characters", "error")],
        )


class AdminTests(TestCase):
    """F19: the admin site lists to-dos for a superuser."""

    def test_admin_lists_todos(self):
        User.objects.create_superuser("boss", "boss@example.com", "a-long-password")
        Todo.objects.create(title="Buy milk")
        self.client.login(username="boss", password="a-long-password")
        response = self.client.get(reverse("admin:todos_todo_changelist"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buy milk")


class TodoFormTests(TestCase):
    """Unit tests: the form alone, no view, no page."""

    def test_valid_title_is_accepted(self):
        form = TodoForm({"title": "Buy milk"})
        self.assertTrue(form.is_valid())

    def test_blank_title_is_rejected(self):
        form = TodoForm({"title": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("title", form.errors)

    def test_whitespace_only_title_is_rejected(self):
        form = TodoForm({"title": "   "})
        self.assertFalse(form.is_valid())

    def test_title_over_200_characters_is_rejected(self):
        form = TodoForm({"title": "x" * 201})
        self.assertFalse(form.is_valid())

    def test_save_strips_surrounding_spaces(self):
        form = TodoForm({"title": "  Call home  "})
        self.assertTrue(form.is_valid())
        todo = form.save()
        self.assertEqual(todo.title, "Call home")

    def test_form_with_instance_updates_that_todo(self):
        todo = Todo.objects.create(title="Old")
        form = TodoForm({"title": "New"}, instance=todo)
        self.assertTrue(form.is_valid())
        saved = form.save()
        self.assertEqual(saved.pk, todo.pk)
        self.assertEqual(Todo.objects.count(), 1)
        self.assertEqual(Todo.objects.get().title, "New")
