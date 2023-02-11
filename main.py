from configs import logger_init
from discord_bot import DiscordBot

if __name__ == "__main__":
    logger_init()
    bot = DiscordBot()
    bot.startup()

    input()