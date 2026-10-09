from django import forms

from .models import Todo


class TodoForm(forms.ModelForm):
    """The add form. Django strips spaces, rejects a blank title,
    and enforces the model's max_length of 200."""

    class Meta:
        model = Todo
        fields = ["title"]
