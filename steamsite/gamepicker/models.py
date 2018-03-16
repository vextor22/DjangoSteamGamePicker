from django.db import models

# Create your models here.

class GameInfo(models.Model):
    game_name = models.CharField(max_length=300)
    game_id = models.IntegerField(blank=False)
    fetch_date = models.DateTimeField('date cached')

    def __str__(self):
        return "ID: %s, Game Title: %s" % (self.game_id, self.game_name)

class SteamUser(models.Model):
    name = models.CharField(max_length=150)
    user_id = models.BigIntegerField(blank=False)
    owned_games = models.ManyToManyField(GameInfo)

    def __str__(self):
        return "ID: %s, User Name: %s" % (self.user_id, self.name)
