from config import ACCOUNTS
from utils import get_codes
from time import sleep
import genshin
import asyncio
import aiohttp

async def main():
    for account in ACCOUNTS:
        cookies = await genshin.refresh_cookie_token({ key: value for key, value in account.items() if key != "games" }, source="cookie_token")
        client = genshin.Client(cookies)

        for game in account["games"]:
            uid = await client._get_uid(game)
            print(f"\n-- {game.value.upper()} | UID{uid[0:3]}*** --")

            codes = await get_codes(game)
            if codes:
                for code in codes:
                    try:
                        await client.redeem_code(code, game=game)
                    except Exception as e:
                        print(f"[{code}] {e.msg}")
                    else:
                        print(f"[{code}] Code redeemed successfully.")
                    sleep(5)
            else:
                print(f"No new codes available")
                sleep(5)

asyncio.run(main())