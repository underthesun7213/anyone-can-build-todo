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
        todo.refresh_from_db()
        self.assertEqual(todo.title, "Call home")

    def test_edit_missing_todo_is_404(self):
        response = self.client.get(reverse("todo_edit", args=[999]))
        self.assertEqual(response.status_code, 404)


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
