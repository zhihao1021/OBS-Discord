from .config import ADMIN_PERMISSION
from .fix_module import bridge_group, response

from swap import RECORDER, FILE_QUEUE

from asyncio import get_event_loop

from discord import Cog, Message
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


def setup(bot: Bot):
    bot.add_cog(OBSCog(bot))
