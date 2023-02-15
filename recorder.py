from configs import OBS_CONFIG
from obs_websocket import RecordRequests, RequestCode, OBSWebSocket

from asyncio import sleep as asleep, run
from logging import getLogger
from typing import Union


class Recorder:
    def __init__(self) -> None:
        self.obs = OBSWebSocket(**OBS_CONFIG.dict())
        self.__logger = getLogger("obs")

    async def start_record(self) -> bool:
        await self.obs.connect()
        status = await RecordRequests.GetRecordStatus(self.obs)
        if status:
            self.__logger.warning("Start Record... Fail.")
            return False
        self.__logger.info("Start Record... Success.")
        await RecordRequests.StartRecord(self.obs)

    async def stop_record(self) -> Union[str, bool]:
        await self.obs.connect()
        status = await RecordRequests.GetRecordStatus(self.obs)
        if status:
            self.__logger.info("Stop Record... Success.")
            return await RecordRequests.StopRecord(self.obs)
        self.__logger.warning("Stop Record... Fail.")
        return False

    async def record_test(self) -> Union[str, bool]:
        await self.obs.connect()
        self.__logger.info("Start Test.")
        status = await RecordRequests.GetRecordStatus(self.obs)
        if status:
            self.__logger.warning("Test Record... Fail.")
            return False
        await RecordRequests.StartRecord(self.obs)
        await asleep(10)
        self.__logger.info("Test Record... Success.")
        return await RecordRequests.StopRecord(self.obs)