from uuid import UUID

from django.shortcuts import Http404
from ninja import Router
from ninja_apikey.security import APIKeyAuth

from apps.todo.models import Todo
from apps.todo.schema import Message, TodoIn, TodoOut

router = Router()
auth = APIKeyAuth()


@router.get("/search", response=list[TodoOut])
def search(request, q: str = None, hashtags: str = None):
    if not q and not hashtags:
        return []
    todos = Todo.objects.filter(owner=request.user).prefetch_related("hashtag")
    if q:
        todos = todos.filter(input__icontains=q)
    if hashtags:
        todos = todos.filter(hashtag__name__in=hashtags.split(",")).distinct()
    return todos


@router.get("/", response=list[TodoOut])
def get_todos(request):
    return Todo.objects.filter(owner=request.user)


@router.post("/", response=TodoOut)
def create_todo(request, todo: TodoIn):
    new_todo = Todo.objects.create(input=todo.input, owner=request.user)
    return TodoOut.from_orm(new_todo)


@router.patch("/{uuid:todo_id}", response=TodoOut)
def edit_todo(request, newInfo: TodoIn, todo_id: UUID):
    if not todo_id:
        raise Http404("Todo ID not provided")
    try:
        todo = Todo.objects.get(id=todo_id, owner=request.user)
    except Todo.DoesNotExist:
        raise Http404("Todo not found")
    if newInfo.input is not None:
        todo.input = newInfo.input

    if newInfo.done is not None:
        todo.done = newInfo.done
    if newInfo.priority is not None:
        todo.priority = newInfo.priority
    if newInfo.hashtag is not None:
        todo.update_hashtags(newInfo.hashtag)
    todo.save()
    return todo


@router.delete("/{uuid:todo_id}", response=Message)
def delete_todo(request, todo_id: UUID):
    if not todo_id:
        raise Http404("Todo ID not provided")
    try:
        todo = Todo.objects.get(id=todo_id, owner=request.user)
    except Todo.DoesNotExist:
        raise Http404("Todo not found")
    todo.delete()
    return Message(message="deleted")
