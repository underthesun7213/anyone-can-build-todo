from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    """The form to add a to-do, and to edit one. Django strips spaces,
    rejects a blank title, and enforces the model's max_length of 200."""

    class Meta:
        model = Todo
        fields = ["title"]
        widgets = {
            "title": forms.TextInput(attrs={"aria-label": "Title", "autofocus": True}),
        }
        error_messages = {
            "title": {
                "required": "Title can't be blank",
                "max_length": "Title can't be longer than 200 characters",
            },
        }
