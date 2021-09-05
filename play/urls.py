from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.views import obtain_auth_token

from play import views

urlpatterns = [
    path("user/", views.UserView.as_view(), name="user"),
    path("score/", views.ScoreView.as_view(), name="score"),
    path("api-token-auth/", obtain_auth_token, name="api_token_auth"),
    path(
        r"game/<str:player_x>/<str:player_o>/",
        csrf_exempt(views.GameView.as_view()),
        name="game",
    ),
    path(
        r"move/<int:game_id>/<int:row>/<int:column>/",
        csrf_exempt(views.MoveView.as_view()),
        name="game",
    ),
]
