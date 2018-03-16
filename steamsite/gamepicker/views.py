from django.shortcuts import render
from django.http import HttpResponse

import random
import os

import SteamAPI
from secret_steam_key import *
# Create your views here.

def index(request):
    random.seed(os.urandom(4))

    outputBuffer = [] 
    steamID = '76561197995406081'

    steamConn = SteamAPI.SteamAPI(steam_key)

    #get username
    player = steamConn.getPlayerSummary(steamID)
    outputBuffer.append("Username: %s" % player.name)

    #gather user's list of owned games into list of (id, playtime)
    games = steamConn.getOwnedGames(steamID)['response']['games']
    gameList = []
    for game in games:
        gameList.append((game['appid'],game['playtime_forever']))
    gameListSorted = sorted(gameList, key=lambda x: x[1])

    #get list of all games and organize into map of id -> name
    appJson = steamConn.getAppList()
    apps = appJson['applist']['apps']
    appDetails = {}
    for app in apps:
        appDetails[app['appid']] = app['name']
    
    #collect owned games with their names
    for game in gameListSorted:
        outputBuffer.append("Game Name: %s, playtime: % 6.2f" % (appDetails[game[0]],float(game[1])/60))

    randomGame = random.choices(gameListSorted)[0]
    outputBuffer.append("Random Game Name: %s, playtime: % 6.2f" % (appDetails[randomGame[0]],float(randomGame[1])/60))

    return HttpResponse('<br />'.join(outputBuffer))
