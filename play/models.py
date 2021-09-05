"""the orm model for playing tictactoe"""
from django.contrib.auth.models import User
from django.db import models


class Game(models.Model):
    """  a tictactoe game for django users"""
    player_x = models.ForeignKey(User, on_delete=models.CASCADE, related_name="x")
    player_o = models.ForeignKey(User, on_delete=models.CASCADE, related_name="o")
    last_player = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="last"
    )
    winner = models.ForeignKey(
        User, on_delete=models.CASCADE, null=True, related_name="winner"
    )
    board = models.CharField(max_length=9, blank=False, default="_________")
    over = models.BooleanField(default=False)
