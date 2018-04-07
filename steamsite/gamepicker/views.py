from django.shortcuts import render
from django.http import HttpResponse

import random
import os

from .models import GameInfo, SteamUser,Ownership

from secret_steam_key import *
# Create your views here.

def index(request):
    random.seed(os.urandom(4))

    outputBuffer = [] 
    steamID = ''
    user = SteamUser.get_or_update_user(steam_key, steamID)
    outputBuffer.append("Username: %s" % user.name)
    user_games = Ownership.objects.filter(user=user)
    #get list of all games and organize into map of id -> name
#    appJson = steamConn.getAppList()
#    apps = appJson['applist']['apps']
#    appDetails = {}
#    for app in apps:
#        appDetails[app['appid']] = app['name']
    
    #collect owned games with their names
    for owned_game in user_games:
        outputBuffer.append("Game Name: %s, playtime: % 6.2f" % 
                (owned_game.game.game_name,float(owned_game.play_time)/60))

    randomGame = random.choices(user_games)[0]
    outputBuffer.append("Random Game Name: %s, playtime: % 6.2f" % 
            (randomGame.game.game_name,float(randomGame.play_time)/60))

    return HttpResponse('<br />'.join(outputBuffer))
