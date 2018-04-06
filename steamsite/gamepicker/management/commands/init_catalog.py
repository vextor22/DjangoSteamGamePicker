from django.core.management.base import BaseCommand, CommandError
from gamepicker.models import GameInfo, SteamUser
from django.utils import timezone

import SteamAPI
import progressbar
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
        with progressbar.ProgressBar(max_value=len(apps), redirect_stdout=True) as progress:
            for idx,app in enumerate(apps):
                appid = app['appid']
                name = app['name']
                app = GameInfo.objects.filter(game_id=int(appid))
                if app.exists(): 
                    #                    self.stdout.write(self.style.SUCCESS("Already have %s" % name))
                    app = app.first()
                    if app.game_name != name:
                        self.stdout.write(self.style.SUCCESS("%s, %s" % (app.game_name, name)))
                        updates += 1
                        app.game_name = name

                        app.save()
                else: 
                    #self.stdout.write(self.style.SUCCESS("New game found: %s" % name))
                    new_games += 1
                    app = GameInfo(game_name=name, game_id=appid, fetch_date=timezone.now())
                    try:
                        app.save()
                    except Exception as e:
                        self.stdout.write(self.style.SUCCESS(name))
                        
                        self.stdout.write(self.style.ERROR(e))
                progress.update(idx)

        self.stdout.write(self.style.SUCCESS("Out of %s games, %s were updated. %s new games found." %
                                              (current_games, updates, new_games)))

