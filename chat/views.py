from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Room, Message

def index(request):
    rooms = Room.objects.all()
    return render(request, 'chat/index.html', {
        'rooms': rooms
    })

def room(request, room_name):
    # Get or create the room
    room, created = Room.objects.get_or_create(name=room_name)
    
    # Get the last 50 messages for this room
    messages = Message.objects.filter(room=room).order_by('-timestamp')[:50]
    
    # Convert to list before reordering for display
    messages_list = list(messages)
    messages_list.reverse()  # Reverse to get chronological order
    
    return render(request, 'chat/room.html', {
        'room_name': room_name,
        'room': room,
        'messages': messages_list,
    })