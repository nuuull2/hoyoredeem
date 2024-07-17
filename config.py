import os
from genshin import Game
from dotenv import load_dotenv
from os.path import join, dirname

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

ACCOUNTS = (
    {
        "cookie_token_v2": os.environ.get("MY_COOKIE_TOKEN"),
        "account_mid_v2": os.environ.get("MY_MID"),
        "games": [ Game.GENSHIN, Game.ZZZ ]
    },
    {
        "cookie_token_v2": os.environ.get("ALT_COOKIE_TOKEN"),
        "account_mid_v2": os.environ.get("ALT_MID"),
        "games": [ Game.STARRAIL ]
    }
)