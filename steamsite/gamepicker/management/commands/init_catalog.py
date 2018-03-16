from django.core.management.base import BaseCommand, CommandError
from gamepicker.models import GameInfo, SteamUser
from django.utils import timezone

import SteamAPI
from secret_steam_key import *

class Command(BaseCommand):
    help = "Populates steam game catalog table"


    def handle(self, *args, **options):

        steamConn = SteamAPI.SteamAPI(steam_key)
        #get list of all games and organize into map of id -> name
        updates = 0
        new_games = 0
        current_games = GameInfo.objects.count()
        appJson = steamConn.getAppList()
        apps = appJson['applist']['apps']
        appDetails = {}
        for app in apps:
            appid = app['appid']
            name = app['name']
            app = GameInfo.objects.filter(game_id=int(appid))
            if app.exists(): 
                #self.stdout.write(self.style.SUCCESS("Already have %s" % name))
                updates += 1
                app = app.first()
                if app.game_name is not name:
                    app.game_name = name
                    app.save()
            else: 
                #self.stdout.write(self.style.SUCCESS("New game found: %s" % name))
                new_games += 1
                app = GameInfo(game_name=name, game_id=appid, fetch_date=timezone.now())
                app.save()

        self.stdout.write(self.style.SUCCESS("Out of %s games, %s were updated. %s new games found." %
                                              (current_games, updates, new_games)))

