from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.db.models import Q, Count, Sum
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm


def logInPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = User.objects.get(email=email)
        except:
            messages.error(request, 'User does not exist')

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')

    context = {'page': page}
    return render(request, 'base/login_register.html', context)


def logoutUser(request):
    logout(request)
    return redirect('home')


def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user': user, 'rooms': rooms,
               'room_messages': room_messages, 'topics': topics}
    return render(request, 'base/profile.html', context)


def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(Q(topic__name__icontains=q) | Q(
        name__icontains=q) | Q(description__icontains=q))
    topics = Topic.objects.all()[0:5]
    room_len = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics': topics,
               'room_count': room_len, 'room_messages': room_messages}
    return render(request, 'base/home.html', context=context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    edit_message_id = request.session.get('edit_message_id', -1)

    room_messages = room.message_set.all()
    participants = room.participants.all()
    if request.method == 'POST':
        try:
            if request.POST.get('msgBody'):
                msg_to_change = Message.objects.get(
                    id=int(request.POST.get('msgId')))
                msg_to_change.body = request.POST.get('msgBody')
                msg_to_change.save()
                return redirect('room', pk=room.id)
            elif request.user.is_authenticated and not (request.POST.get('msgBody')):
                Message.objects.create(
                    body=request.POST.get('body'), room=room, user=request.user)
                room.participants.add(request.user)
                return redirect('room', pk=room.id)
            else:
                raise Exception('Not logged in')
        except Exception as E:
            messages.error(request, E)
    context = {'room': room, 'room_messages': room_messages,
               'participants': participants, 'edit_message_id': edit_message_id}
    return render(request, 'base/room.html', context=context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        Room.objects.create(
            host=request.user,
            topic=topic,
            name=request.POST.get('name'),
            description=request.POST.get('description'),
        )
        return redirect('home')
    context = {'form': form, 'action': 'Create', 'topics': Topic.objects.all()}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')
    if request.method == 'POST':
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.description = request.POST.get('description')
        room.topic = topic
        room.save()
        return redirect('home')
    context = {'form': form, 'action': 'Update',
               'room': room, 'topics': topics}
    return render(request, 'base/room_form.html', context)


def registerPage(request):
    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')
    return render(request, 'base/login_register.html', {'form': form, 'page': 'register'})


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.user != room.host:
        return HttpResponse('You are not allowed here')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    context = {'obj': room, 'action': 'room'}
    return render(request, 'base/delete.html', context)


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)
    if request.user != message.user:
        return HttpResponse("You are not allowed to delete")
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': message, 'action': 'message'})


@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == 'POST':
        form = UserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)

    context = {'form': form}
    return render(request, 'base/update-user.html', context)


def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    room_count = Room.objects.filter(topic__in=topics).count()
    return render(request, 'base/topics.html', {'topics': topics, 'all_rooms_count': room_count})


def activityPage(request):
    room_messages = Message.objects.all()
    context = {'room_messages': room_messages}
    return render(request, 'base/activity.html', context)
