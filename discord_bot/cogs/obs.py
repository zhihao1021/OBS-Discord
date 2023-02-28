from .config import ADMIN_PERMISSION
from .fix_module import bridge_group, response

from swap import RECORDER, FILE_QUEUE

from io import BytesIO
from typing import Optional

from aiohttp import ClientSession
from discord import Cog, Message, File
from discord.ext.bridge import Bot, BridgeContext


class OBSCog(Cog):
    def __init__(self, bot: Bot) -> None:
        self.bot = bot

    @bridge_group(default_member_permissions=ADMIN_PERMISSION)
    async def obs(self, ctx: BridgeContext):
        ...

    @obs.command(name="test", description="紀錄測試，會錄製一個10秒鐘的影片。")
    async def command(
        self,
        ctx: BridgeContext,
    ):
        mes = await response(ctx=ctx, content="Querying...")
        res = await RECORDER.record_test()
        if res:
            await FILE_QUEUE.put(res)
            result = "Record Successful!"
        else:
            result = "Record Fail!"
        if type(mes) == Message:
            await mes.edit(content=result)
        else:
            await mes.edit_original_response(content=result)

    @obs.command(name="light-on", description="開燈。")
    async def light_on(
        self,
        ctx: BridgeContext,
    ):
        await response(ctx=ctx, content="Light On!")
        async with ClientSession() as client:
            await client.get("http://localhost:8080/api/light-on")

    @obs.command(name="light-off", description="關燈。")
    async def light_off(
        self,
        ctx: BridgeContext,
    ):
        await response(ctx=ctx, content="Light Off!")
        async with ClientSession() as client:
            await client.get("http://localhost:8080/api/light-off")
    
    @obs.command(name="light-test", description="測試燈。")
    async def light_test(
        self,
        ctx: BridgeContext,
        times: Optional[int]=5,
        sleep: Optional[int]=50
    ):
        mes = await response(ctx=ctx, content="Querying...")
        async with ClientSession() as client:
            await client.get(f"http://localhost:8080/api/light-test?n={times}&s={sleep}")
        if type(mes) == Message:
            await mes.edit(content="Finish!")
        else:
            await mes.edit_original_response(content="Finish")

    @obs.command(name="shot", description="拍攝快照。")
    async def shot(self, ctx: BridgeContext, timestamp: bool=True):
        io = BytesIO(b"")
        async with ClientSession() as client:
            if timestamp:
                res = await client.get("http://localhost:8080/timestamp_shot")
            else:
                res = await client.get("http://localhost:8080/shot")
            io.write(await res.content.read())
        io.seek(0)
        await response(ctx=ctx, content="One Shot!", file=File(io, "shot.jpg"))


def setup(bot: Bot):
    bot.add_cog(OBSCog(bot))
