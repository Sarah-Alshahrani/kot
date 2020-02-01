import datetime

from passlib.hash import md5_crypt as md5
from game.models import User
from game.player.player import Player


class IRepositoryPlayer:
    def __init__(self):
        self.user = None

    def save_player_db(self, player: Player):
        self.user = User(monster_name=player.monster_name,
                         username=player.username,
                         password=md5.encrypt(player.password),
                         date_created=datetime.datetime.now())
        self.user.save()
        return self.user

    def get_player_db(self, player: Player):
        self.user = User.objects.get(monster_name=player.monster_name)
        return self.user

    def update_player_db(self, player: Player):
        self.user = User.objects.get(monster_name=player.monster_name)
        self.user.username = player.username
        self.user.password = md5.encrypt(player.password)
        self.user.save()
        return self.user

    def delete_player_db(self, player: Player):
        self.user = User.objects.get(monster_name=player.monster_name)
        self.user.delete()
        return None