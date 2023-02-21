from configs import logger_init
from discord_bot import DiscordBot
from time import time, sleep
from swap import RECORDER, FILE_QUEUE
from utils import Json

from asyncio import CancelledError, set_event_loop_policy, sleep as asleep, WindowsSelectorEventLoopPolicy, run
from logging import getLogger

from aiohttp import ClientSession

LOGGER = getLogger("main")


async def main():
    client = ClientSession()

    w = False
    c = time()
    while True:
        try:
            res = await client.get("http://localhost:8080/face-data")
            data = await res.json(loads=Json.loads)
            det = len(data)
            print(f"People num: {det}", end="\r")
            if det != 0:
                if not w:
                    LOGGER.warning(f"Detect People: {det}")
                    await RECORDER.start_record()
                c = time()
                w = True
            else:
                await asleep(0.2)

            if w and time() - c > 3:
                res = await RECORDER.stop_record()
                if res:
                    await FILE_QUEUE.put(res)
                w = False
                await asleep(1)

        except CancelledError:
            break

    await client.close()

if __name__ == "__main__":
    # set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    logger_init()
    bot = DiscordBot()
    bot.startup()

    while True:
        sleep(1)

    # run(main())
