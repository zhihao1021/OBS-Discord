from configs import logger_init
from discord_bot import DiscordBot
from swap import RECORDER, FILE_QUEUE
from utils import Json

from asyncio import CancelledError, set_event_loop_policy, sleep as asleep, WindowsSelectorEventLoopPolicy, run
from logging import getLogger

from aiohttp import ClientSession

LOGGER = getLogger("main")




if __name__ == "__main__":
    set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    logger_init()
    bot = DiscordBot()
    bot.startup()
