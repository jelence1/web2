from django.db import models

# Create your models here.
class Users(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000, default="user")
    role = models.CharField(max_length=1000)
    email = models.CharField(max_length=1000, unique=True)
    password = models.CharField(max_length=1000)
    first_name = models.CharField(max_length=1000)
    last_name = models.CharField(max_length=1000)

class Teams(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=1000)
    nickname = models.CharField(max_length=1000)
    played = models.IntegerField(default=0)
    won = models.IntegerField(default=0)
    lost = models.IntegerField(default=0)
    points = models.IntegerField(default=0)

    def _calc_diff(self):
        return self.played - (self.won + self.lost)
    
    draw = property(_calc_diff)

    def _calc_percent(self):
        if self.played == 0:
            return 0
        return round(self.won / self.played, 3)

    win_percent = property(_calc_percent)


class Matches(models.Model):
    id = models.AutoField(primary_key=True)
    team1 = models.ForeignKey('Teams', on_delete=models.DO_NOTHING, related_name="team1")
    team2 = models.ForeignKey('Teams', on_delete=models.DO_NOTHING, related_name="team2")
    goals1 = models.IntegerField(null=True)
    goals2 = models.IntegerField(null=True)
    date = models.DateField()
    time = models.TimeField()

class Comments(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('Users', on_delete=models.DO_NOTHING)
    match = models.ForeignKey('Matches', on_delete=models.CASCADE)
    comment = models.CharField(max_length=1000)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
