from configs import logger_init
from discord_bot import DiscordBot
from time import sleep

from logging import getLogger

LOGGER = getLogger("main")

if __name__ == "__main__":
    # set_event_loop_policy(WindowsSelectorEventLoopPolicy())
    logger_init()
    bot = DiscordBot()
    bot.startup()

    while True:
        sleep(1)

    # run(main())
