from configs import logger_init
from discord_bot import DiscordBot
from swap import RECORDER, FILE_QUEUE
from utils import Json

from asyncio import CancelledError, set_event_loop_policy, sleep as asleep, WindowsSelectorEventLoopPolicy, run
from logging import getLogger

from aiohttp import ClientSession

LOGGER = getLogger("main")


async def main():
    client = ClientSession()

    w = False
    s = False
    c = 0
    while True:
        try:
            res = await client.get("http://localhost:8080/face-data")
            data = await res.json(loads=Json.loads)
            if len(data) != 0:
                if not w:
                    LOGGER.warning(f"Detect People: {len(data)}")
                c = 0
                w = True
            else:
                c += 1

            if w and c > 25:
                res = RECORDER.stop_record()
                if res:
                    await FILE_QUEUE.put(res)
                s = False
                w = False

            if w and not s:
                RECORDER.start_record()
                s = True
            await asleep(0.2)
        except CancelledError:
            break

    await client.close()

if __name__ == "__main__":
    # set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    logger_init()
    bot = DiscordBot()
    bot.startup()

    run(main())
