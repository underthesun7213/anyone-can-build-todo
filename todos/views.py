from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_http_methods, require_POST

from .forms import TodoForm
from .models import Todo


def todo_list(request):
    todos = Todo.objects.all()
    has_done = todos.filter(done=True).exists()
    return render(
        request, "todos/todo_list.html", {"todos": todos, "has_done": has_done}
    )


@require_POST
def todo_add(request):
    form = TodoForm(request.POST)
    if form.is_valid():
        form.save()
    return redirect("todo_list")


@require_http_methods(["GET", "POST"])
def todo_edit(request, pk):
    """GET shows the edit form; POST saves it and goes back to the list.
    An invalid POST shows the form again, with the error, and changes nothing."""
    todo = get_object_or_404(Todo, pk=pk)
    if request.method == "POST":
        form = TodoForm(request.POST, instance=todo)
        if form.is_valid():
            form.save()
            return redirect("todo_list")
    else:
        form = TodoForm(instance=todo)
    return render(request, "todos/todo_edit.html", {"form": form, "todo": todo})


@require_POST
def todo_toggle(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.done = not todo.done
    todo.save()
    return redirect("todo_list")


@require_POST
def todo_delete(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.delete()
    return redirect("todo_list")


@require_POST
def todo_clear_done(request):
    """Delete every done to-do in one step. If none is done, nothing changes."""
    Todo.objects.filter(done=True).delete()
    return redirect("todo_list")
