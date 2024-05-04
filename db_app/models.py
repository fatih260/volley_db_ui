from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)

class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    date_of_birth = models.DateField()
    height = models.FloatField()
    weight = models.FloatField()

class Coach(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nationality = models.CharField(max_length=100)

class Jury(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    nationality = models.CharField(max_length=100)

class DatabaseAdministrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)

class Position(models.Model):
    position_id = models.AutoField(primary_key=True)
    position_name = models.CharField(max_length=100)

class Team(models.Model):
    team_id = models.AutoField(primary_key=True)
    team_name = models.CharField(max_length=100)
    coach = models.ForeignKey(Coach, on_delete=models.CASCADE)
    contract_start = models.DateField()
    contract_finish = models.DateField()
    channel_id = models.CharField(max_length=100)

class PlayerPosition(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

class PlayerTeam(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

class SessionSquad(models.Model):
    squad_id = models.AutoField(primary_key=True)
    session_id = models.IntegerField()
    played_player = models.ForeignKey(Player, on_delete=models.CASCADE)
    position = models.ForeignKey(Position, on_delete=models.CASCADE)

class MatchSession(models.Model):
    session_id = models.AutoField(primary_key=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    stadium_id = models.IntegerField()
    stadium_name = models.CharField(max_length=100)
    stadium_country = models.CharField(max_length=100)
    time_slot = models.IntegerField()
    date = models.DateField()
    assigned_jury = models.ForeignKey(Jury, on_delete=models.CASCADE)
    rating = models.FloatField(null=True)

