import json
import threading

import requests

output = threading.Lock()


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


def play_game(moves, tok_x, url, user_x, user_o, thread_name=""):
    game_id = start_game(
        tok_x,
        url,
        user_x,
        user_o,
    )
    for move in moves:
        if make_move(url, move[0], game_id, move[1], move[2], thread_name):
            break


def start_game(
    token,
    url,
    user_x,
    user_o,
):
    response = requests.post(
        f"{url}/game/{user_o}/{user_x}/", headers={f"Authorization": f"Token {token}"}
    )
    game_id = extract_field(response, "game_id")
    return game_id


def make_move(url, token, game_id, row, column, thread_name="") -> bool:
    response = requests.put(
        f"{url}/move/{game_id}/{row}/{column}/",
        headers={f"Authorization": f"Token {token}"},
    )
    if response.status_code != 200:
        raise ValueError(response.text)
    # board = extract_field(response, "board", False, thread_name)
    # with output:
    #     print(f"{thread_name}\n{board[:3]}\n{board[3:6]}\n{board[6:]}")
    return extract_field(response, "over", True, thread_name)


def extract_field(response, field_name, verbose=True, thread_name=""):
    response_json = response.json()
    if verbose:
        with output:
            print(f"{thread_name}{response_json}")
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
    moves_2 = [
        (tok_o, 1, 1),
        (tok_x, 1, 2),
        (tok_o, 1, 3),
        (tok_x, 2, 1),
        (tok_o, 2, 2),
        (tok_x, 2, 3),
        (tok_o, 3, 1),
    ]
    moves_3 = [
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

    threads = []
    i = 0
    for moves in [moves_1, moves_2, moves_3]:
        i += 1
        thread = threading.Thread(
            target=play_game,
            args=(
                moves,
                tok_o,
                url,
                user_x,
                user_o,
                f"T{i} ",
            ),
        )
        threads.append(thread)

    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    response = requests.get(url=f"{url}/score/")
    print(response.json())


if __name__ == "__main__":
    play()
