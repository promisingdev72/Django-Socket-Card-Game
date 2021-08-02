from django.http import HttpResponse
from django.shortcuts import render
import socketio
import random
import numpy


async_mode = None
sio = socketio.Server(async_mode=async_mode)
suits = ["♣", "♦", "♥", "♠"]
numbers = ["A", '2', '3', '4', '5', '6', '7', '8', '9', '10', "J", "Q", "K"]
cards = []

for n in numbers:
    for s in suits:
        cards.append({'suit': s, 'number': n})


def ShowCardGameHome(request):
    return render(request, "card_game_home.html")


def ShowCardGamePage(request, room_name, person_name):
    return render(request, "card_game_room.html", {'room_name': room_name, 'person_name': person_name})


@sio.event
def connect(sid, env):
    print('connected ' + sid)


@sio.event
def join(sid, message):
    members = []
    try:
        for rsid, _ in sio.manager.get_participants('/', message['room']):
            members.append(rsid)
    except:
        members = []
    if len(members) < 4:
        sio.enter_room(sid, message['room'])
        sio.emit('status_msg', {'status': 'connected', 'name': message['name']}, room=message['room'])
        members.append(sid)
        print('Entered room: ' + message['room'] + ' : ' + message['name'])
        print(len(members))
        if len(members) == 2:
            random.shuffle(cards)
            cards_rand = numpy.array_split(cards, 4)
            for room_sid in members:
                sio.emit('status_msg', {'status': 'cards', 'cards': list(cards_rand.pop())}, to=room_sid)
            sio.emit('status_msg', {'status': 'round'}, to=members[0])
    else:
        pass


@sio.event
def disconnect(sid):
    print('Client disconnected ' + sid)
    for room in sio.rooms(sid):
        if room != sid:
            sio.emit('status_msg', {'status': 'disconnected'}, to=sid)
    sio.disconnect(sid)


@sio.event
def place(sid, message):
    sio.emit('status_msg', {'status': 'placed', 'name': message['name'], 'card': message['card']}, room=message['room'])
    members = []
    for rsid, _ in sio.manager.get_participants('/', message['room']):
        members.append(rsid)
    index = members.index(sid)
    sio.emit('status_msg', {'status': 'round'}, to=members[(index + 1) % 2])


@sio.event
def next_round(sid, message):
    members = []
    for rsid, _ in sio.manager.get_participants('/', message['room']):
        members.append(rsid)
    sio.emit('status_msg', {'status': 'placed', 'name': message['name'], 'card': message['card']}, room=message['room'])
