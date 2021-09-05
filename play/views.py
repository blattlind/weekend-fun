"""the views for tictactoe.play"""
import json
from collections import defaultdict
from typing import Dict, List, Tuple

from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http.response import HttpResponseBadRequest
from rest_framework.authtoken.models import Token
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from play.models import Game


class UserView(APIView):
    """The view that handles the creation of users"""

    def post(self, request):
        """create a user if not already existing"""
        user_data = json.loads(request.read())
        name = user_data.get("user")
        try:
            User.objects.get(username=name)
            message = {"message": f"{name} already exists"}
        except ObjectDoesNotExist:
            User.objects.create_user(
                name,
                f"{name}@organization.org",
                user_data.get("password"),
            )
            message = {"message": f"{name} succesfully created"}
        return Response(message)


class GameView(APIView):
    """The view that handles the creation of games"""

    @permission_classes([IsAuthenticated])
    def post(self, request, player_x, player_o):
        """create a new game for the two players"""
        token = request.headers["Authorization"].split()[-1]
        print(Token.objects.get(key=token).user)

        user_x = User.objects.get(username=player_x)
        user_o = User.objects.get(username=player_o)
        game = Game.objects.create(
            player_x=user_x,
            player_o=user_o,
        )
        content = {"game_id": str(game.id)}
        return Response(content)


class MoveView(APIView):
    """The view that does the moves"""

    WINNING_TRIPLES: List[Tuple[int, int, int]] = [
        (1, 2, 3),
        (4, 5, 6),
        (7, 8, 9),
        (1, 4, 7),
        (2, 5, 8),
        (5, 6, 9),
        (1, 5, 9),
        (3, 5, 7),
    ]

    @classmethod
    def won_or_over(cls, board: str, tag: str) -> Tuple[bool, bool]:
        for tri in cls.WINNING_TRIPLES:
            won = True
            for cur in tri:
                if board[cur - 1] != tag:
                    won = False
                    break
            if won:
                return True, True
        return (not "_" in board), False

    @permission_classes([IsAuthenticated])
    def put(self, request, game_id, row, column):
        """make a move"""
        token = request.headers["Authorization"].split()[-1]
        user = Token.objects.get(key=token).user
        print(user, game_id, row, column)

        try:
            game = Game.objects.get(id=game_id)
        except ObjectDoesNotExist:
            return HttpResponseBadRequest(f"{game_id} does not match a game")
        if game.last_player and game.last_player == user:
            return HttpResponseBadRequest("it is not your turn")
        if game.over:
            return HttpResponseBadRequest(f"game {game_id} is over")

        def is_valid(coord: int):
            return 1 <= coord <= 3

        if not is_valid(column) or not is_valid(row):  #
            return HttpResponseBadRequest(f"field index [{row},{column}] is not valid")
        idx = (row - 1) * 3 + (column - 1)
        field_states = list(game.board)
        cur_tag = field_states[idx]
        if cur_tag != "_":
            return HttpResponseBadRequest(
                f"field [{row},{column}] not available any more"
            )
        if game.player_o == user:
            tag = "o"
        elif game.player_x == user:
            tag = "x"
        else:
            return HttpResponseBadRequest(f"{user} does not play this game")
        field_states[idx] = tag
        game.board = "".join(field_states)
        game.last_player = user
        is_over, has_won = MoveView.won_or_over(game.board, tag)
        if has_won:
            game.winner = user
        if is_over:
            game.over = True
        game.save()
        print(game.board)
        content = {
            "board": game.board,
            "last": game.last_player.username,
            "winner": game.winner.username if game.winner else "",
            "over": game.over,
        }
        return Response(content)


class ScoreView(APIView):
    """The view that shows the scores"""

    def get(self, reuest):
        winners = defaultdict(int)
        participants = defaultdict(int)
        for game in Game.objects.all():
            if game.over:
                if game.winner:
                    winners[game.winner.username] += 1
                participants[game.player_x.username] += 1
                participants[game.player_o.username] += 1
        result: Dict[str, Tuple[int, int, float]] = {}
        for user in participants.keys():
            result[user] = (
                participants[user],
                winners[user],
                round(winners[user] / participants[user], 2),
            )
        return Response(result)
