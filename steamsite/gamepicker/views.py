from django.shortcuts import render
from django.http import HttpResponse

import random
import os

from .models import GameInfo, SteamUser,Ownership

from secret_steam_key import *
# Create your views here.

def select_game(request):
    random.seed(os.urandom(4))
    
    steamID = request.POST.get('steam_id')

    outputBuffer = [] 
    
    user = SteamUser.get_or_update_user(steam_key, steamID)
    outputBuffer.append("Username: %s" % user.name)
    user_games = Ownership.objects.filter(user=user)
    game_list = []
    for owned_game in user_games:
        game_list.append((owned_game.game.game_name,float(owned_game.play_time)/60))

    randomGame = random.choices(user_games)[0]
    outputBuffer.append("Random Game Name: %s, playtime: % 6.2f" % 
            (randomGame.game.game_name,float(randomGame.play_time)/60))

    #return HttpResponse('<br />'.join(outputBuffer))
    play_time_string = "% 6.2f" % (float(randomGame.play_time)/60)
    context = {'user_name': user.name, 
               'random_game': randomGame.game.game_name, 
               'random_game_time': play_time_string,
               'game_info': game_list}
    return render(request, 'game.html', context)

def index(request):
    return render(request, 'home.html')
