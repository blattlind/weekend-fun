import json

import requests


def create_user(name, url):
    body = json.dumps({"user": name, "password": "geheim"})
    response = requests.post(f"{url}/user/", data=body)
    print(response.json())


def get_token(name, url):
    body = json.dumps({"username": name, "password": "geheim"})
    headers = {"Content-Type": "application/json"}
    response = requests.post(f"{url}/api-token-auth/", data=body, headers=headers)
    if response.status_code != 200:
        raise ValueError(response.text)
    return extract_field(response, "token")

def play_game(moves, tok_x, url, user_x, user_o,):
    game_id = start_game(tok_x, url, user_x, user_o,)
    for move in moves:
        if make_move(url, move[0], game_id, move[1], move[2]):
            break
    resonse = requests.get(url=f"{url}/score/")
    print(resonse.json())


def start_game(token, url, user_x, user_o,):
    response = requests.post(
        f"{url}/game/{user_o}/{user_x}/", headers={f"Authorization": f"Token {token}"}
    )
    game_id = extract_field(response, "game_id")
    return game_id


def make_move(url, token, game_id, row, column) -> bool:
    response = requests.put(
        f"{url}/move/{game_id}/{row}/{column}/",
        headers={f"Authorization": f"Token {token}"},
    )
    if response.status_code != 200:
        raise ValueError(response.text)
    board = extract_field(response, "board")
    print(f"{board[:3]}\n{board[3:6]}\n{board[6:]}")
    return extract_field(response, "over", False)


def extract_field(response, field_name, verbose = True):
    response_json = response.json()
    if verbose:
        print(response_json)
    return response_json[field_name]



def play():
    url = "http://127.0.0.1:8000"

    user_o = "otto"
    create_user(user_o, url)
    user_x = "xaver"
    create_user(user_x, url)
    tok_x = get_token(user_x, url)
    tok_o = get_token(user_o, url)

    moves_1 = [
        (tok_x, 1, 2),
        (tok_o, 1, 1),
        (tok_x, 2, 2),
        (tok_o, 2, 1),
        (tok_x, 3, 2),
        (tok_o, 3, 1),
    ]
    play_game(moves_1, tok_x, url, user_x, user_o,)
    moves = [
        (tok_o, 1, 1),
        (tok_x, 1, 2),
        (tok_o, 1, 3),
        (tok_x, 2, 1),
        (tok_o, 2, 2),
        (tok_x, 2, 3),
        (tok_o, 3, 1),
    ]
    play_game(moves, tok_o, url, user_o, user_x,)
    moves = [
        (tok_x, 1, 1),
        (tok_o, 1, 2),
        (tok_x, 1, 3),
        (tok_o, 2, 2),
        (tok_x, 2, 1),
        (tok_o, 2, 3),
        (tok_x, 3, 2),
        (tok_o, 3, 1),
        (tok_x, 3, 3),
    ]
    play_game(moves, tok_o, url, user_x, user_o,)


if __name__ == "__main__":
    play()
