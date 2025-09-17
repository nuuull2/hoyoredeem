from genshin import Game
from os.path import join, dirname
import os
import aiohttp
import asyncio
import re

CODES_URL = {
    Game.GENSHIN: "https://game8.co/games/Genshin-Impact/archives/304759",
    Game.STARRAIL: "https://game8.co/games/Honkai-Star-Rail/archives/410296",
    Game.ZZZ: "https://game8.co/games/Zenless-Zone-Zero/archives/435683"
}

async def get_codes_upstream(game):
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(CODES_URL[game], headers=headers) as response:
            if not response.status == 200:
                return None

            response_text = await response.text()

            return re.findall(r'(?:redemption|gift)\?code=([\w\d]+)', response_text)

async def get_codes_history(game):
    if os.environ.get("GITHUB_ACTIONS") == "true":
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f"Bearer {os.environ.get("GITHUB_TOKEN")}",
            'X-GitHub-Api-Version': '2022-11-28'
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://api.github.com/repos/{os.environ.get("GITHUB_REPOSITORY")}/actions/variables/{game.value.upper()}_HISTORY", headers=headers) as response:
                if not response.status == 200:
                    print("Can't access repository variables. Please check your credentials.")
                    exit(1)
                
                response_json = await response.json()

                try:
                    return response_json["value"].split()
                except:
                    return []
    else:
        return []

async def set_codes_history(game, codes):
    if os.environ.get("GITHUB_ACTIONS") == "true":
        headers = {
            'Accept': 'application/vnd.github+json',
            'Authorization': f"Bearer {os.environ.get("GITHUB_TOKEN")}",
            'X-GitHub-Api-Version': '2022-11-28',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        body = {
            "name": f"{game.value.upper()}_HISTORY",
            "value": " ".join(codes)
        }

        async with aiohttp.ClientSession() as session:
            async with session.patch(f"https://api.github.com/repos/{os.environ.get("GITHUB_REPOSITORY")}/actions/variables/{game.value.upper()}_HISTORY", headers=headers, json=body) as response:
                if not response.status == 204:
                   print("Can't access repository variables. Please check your credentials.")
                   exit(1)

async def get_codes(game):
    if f"{game.value.upper()}_CODES" in os.environ:
        return os.environ.get(f"{game.value.upper()}_CODES").split()
    else:
        upstream_codes = await get_codes_upstream(game)
        old_codes = await get_codes_history(game)

        await set_codes_history(game, upstream_codes)

        codes = [ x for x in upstream_codes if x not in old_codes ]

        os.environ[f"{game.value.upper()}_CODES"] = " ".join(codes)
        
        return codes
