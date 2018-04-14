from django.db import models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from datetime import timedelta
import SteamAPI

import time
# Create your models here.

class GameInfo(models.Model):
    game_name = models.CharField(max_length=300)
    game_id = models.IntegerField(db_index=True, blank=False)
    fetch_date = models.DateTimeField('date cached', default=timezone.now)

    def __str__(self):
        return "ID: %s, Game Title: %s" % (self.game_id, self.game_name)

class SteamUser(models.Model):
    name = models.CharField(max_length=150)
    user_id = models.BigIntegerField(db_index=True, blank=False)
    owned_games = models.ManyToManyField(GameInfo, through='Ownership')
    last_updated = models.DateTimeField('date cached', default=timezone.now)
  
    def get_user_name(steam_key, user_id):
        steamConn = SteamAPI.SteamAPI(steam_key)

        #get username
        player = steamConn.getPlayerSummary(user_id)
        return player.name
    def is_user_fresh(self):
        cur_time = timezone.now()
        delta = self.last_updated - cur_time
        if timedelta(minutes=-360) < delta:
            return True
        else:
            return False


    #Largely the same as user creation
    #TODO refactor user data operations for DRY
    def _update_user(steam_key, steamID):
        start = time.time()
        user_model = SteamUser.objects.get(user_id=steamID)
        user_name = SteamUser.get_user_name(steam_key, steamID)

        games = SteamUser.get_game_list(steam_key, steamID)
        game_ids = {game_id: play_time for (game_id, play_time) in games}
        game_models = GameInfo.objects.filter(game_id__in=game_ids)
        game_models_dict = {model.game_id: model for model in game_models}

        user_model.name = user_name
        user_model.user_id = steamID
        user_model.last_updated = timezone.now()
        user_model.owned_games.clear()
        user_model.save()

        relations=[]
        for (key, value) in game_ids.items():
            relations.append(
                    Ownership(game=game_models_dict[key], user=user_model, play_time=value))
                    #Ownership(game=game_models.get(game_id=key), user=user_model, play_time=value))
        Ownership.objects.bulk_create(relations)


        end = time.time()
        return user_model

    def get_or_update_user(steam_key, steamID):
        try:
            user_model = SteamUser.objects.get(user_id=steamID)
            
            print("User Found!")
            if not user_model.is_user_fresh():
                print("User not fresh, updating...")
                user_model = SteamUser._update_user(steam_key, steamID)
            else:
                print("User is fresh, taking cached data!")
                
        except ObjectDoesNotExist:
            print("Creating user...")
            user_name = SteamUser.get_user_name(steam_key, steamID)
            games = SteamUser.get_game_list(steam_key, steamID)
            
            #play time data to enrich relationship object
            game_ids = {game_id: play_time for (game_id, play_time) in games}

            #find game objects owned by user
            game_models = GameInfo.objects.filter(game_id__in=game_ids)

            #materialize queryset into dict for faster lookup than .get()
            game_models_dict = {model.game_id: model for model in game_models}

            #Not data safe if relationship object creation fails, Impove!
            user_model = SteamUser(name=user_name, user_id=steamID)
            user_model.save()
           
            #generate User,Game relationships and bulk add to reduce DB queries VS .save()
            relations=[]
            for (key, value) in game_ids.items():
                relations.append(
                        Ownership(game=game_models_dict[key], user=user_model, play_time=value))
            Ownership.objects.bulk_create(relations)
        return user_model

    def get_game_list(steam_key, user_id):
        steamConn = SteamAPI.SteamAPI(steam_key)

        #gather user's list of owned games into list of (id, playtime)
        games = steamConn.getOwnedGames(user_id)['response']['games']
        gameList = []
        for game in games:
            gameList.append((game['appid'],game['playtime_forever']))
        gameListSorted = sorted(gameList, key=lambda x: x[1])

        return gameListSorted



    def __str__(self):
        return "ID: %s, User Name: %s" % (self.user_id, self.name)

class Ownership(models.Model):
    game = models.ForeignKey(GameInfo, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(SteamUser, on_delete=models.DO_NOTHING)
    play_time = models.IntegerField(blank=False)
