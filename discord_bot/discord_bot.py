from swap import FILE_QUEUE
from configs import DISCORD_CONFIG
from utils import Thread

from asyncio import all_tasks, CancelledError, create_task, gather, get_event_loop, sleep as asleep
from io import BytesIO
from logging import getLogger
from os.path import split
from subprocess import run
from traceback import format_exception as os_format_exception, format_exc

from aiofiles import open as aopen
from discord import File, Intents
from discord.ext.bridge import Bot
from discord.ext.commands import when_mentioned_or


MAIN_LOGGER = getLogger("main")

def format_exception(exc: Exception):
    return os_format_exception(type(exc), exc, exc.__traceback__)


class DiscordBot(Bot):
    def __init__(self, *args, **kwargs):
        intents = Intents.default()
        intents.message_content = True
        super().__init__(*args, command_prefix=when_mentioned_or(*DISCORD_CONFIG.prefixs), intents=intents, **kwargs)

        self.__logger = getLogger("discord")
        self.__thread = None
        self.__first_connect = True

        self.load_extension("discord_bot.cog_manger")

    async def on_ready(self):
        if self.__first_connect:
            self.__first_connect = False
            self.__logger.warning(f"Discord Bot {self.user} Start.")

            self.loop = get_event_loop()
            self.loop.create_task(self.send_video())
            
            self.channel = self.get_channel(DISCORD_CONFIG.channel)
        else:
            self.__logger.warning(f"Discord Bot {self.user} Reconnect.")

    async def on_disconnect(self):
        self.__logger.warning(f"Discord Bot {self.user} Disconnect.")

    async def send_video(self):
        def scale_file():
            run("ffmpeg -i \"{}\" -fs 8M -c copy temp.mp4 -y".format(file_path))

        while True:
            file_path = await FILE_QUEUE.get()

            file_name = split(file_path)[1]
            self.__logger.info("Get File: {}".format(file_path))
            self.__logger.warning("Scale file...".format(file_path))
            await self.loop.run_in_executor(None, scale_file)

            self.__logger.info("Send File...")
            io = BytesIO(b"")
            async with aopen("temp.mp4", mode="rb") as video:
                io.write(await video.read())
            io.seek(0)
            await self.channel.send(content="People Detect!", file=File(io, file_name))
            self.__logger.info("Send File Successful!")

    def __thread_job(self):
        try:
            self.run(token=DISCORD_CONFIG.token)
        except SystemExit:
            for task in all_tasks(self.loop):
                task.cancel()
            self.loop.stop()
        except Exception as exc:
            MAIN_LOGGER.error(format_exception(exc))
        self.loop.close()

    def startup(self):
        if self.__thread != None:
            return
        self.__thread = Thread(target=self.__thread_job, name="Discord")
        self.__thread.start()
