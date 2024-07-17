from genshin import Game
from os.path import join, dirname
import os
import aiohttp
import asyncio
import re

CODES_URL = {
    Game.GENSHIN: "https://genshin-impact.fandom.com/wiki/Promotional_Code",
    Game.STARRAIL: "https://honkai-star-rail.fandom.com/wiki/Redemption_Code",
    Game.ZZZ: "https://game8.co/games/Zenless-Zone-Zero/archives/435683"
}

async def get_codes_upstream(game):
    headers = {
        'User-Agent': "Opera/9.50 (J2ME/MIDP; Opera Mini/5.1.21965/20.2513; U; en)"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(CODES_URL[game]) as response:
            if not response.status == 200:
                return None
            
            response_text = await response.text()

            if game == Game.GENSHIN:
                return re.findall(r'en/gift\?code=(.+?)"', response_text)
            elif game == Game.STARRAIL:
                rows = [ x for x in re.findall(r'<tr.*?>(?s:.*?)<\/tr>', response_text) if "Valid" in x ]
                return list(map(lambda x: re.search(r'com/gift\?code=(.+?)"', x).group(1), rows))
            elif game == Game.ZZZ:
                table = re.search(r'Active Redeem Codes(?s:.*?)</tbody>', response_text).group(0)
                return re.findall(r"redemption\?code=(.+?) ", table)
            else:
                return None

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
                    exit()
                
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
                   exit()

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