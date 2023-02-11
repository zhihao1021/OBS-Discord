from .core import OBSWebSocket
from .requests_code import RequestCode

from typing import Optional


class RecordRequests:
    @staticmethod
    async def GetRecordStatus(obs: OBSWebSocket) -> Optional[bool]:
        res = await obs.request(RequestCode.GET_RECORD_STATUS)
        if not res.requestStatus.result:
            return None
        return res.responseData.get("outputActive")

    @staticmethod
    async def ToggleRecord(obs: OBSWebSocket) -> bool:
        res = await obs.request(RequestCode.TOGGLE_RECORD)
        if not res.requestStatus.result:
            return False
        return True

    @staticmethod
    async def StartRecord(obs: OBSWebSocket) -> bool:
        res = await obs.request(RequestCode.START_RECORD)
        if not res.requestStatus.result:
            return False
        return True

    @staticmethod
    async def StopRecord(obs: OBSWebSocket) -> Optional[str]:
        res = await obs.request(RequestCode.STOP_RECORD)
        if not res.requestStatus.result:
            return None
        return res.responseData.get("outputPath")

    @staticmethod
    async def ToggleRecordPause(obs: OBSWebSocket) -> bool:
        res = await obs.request(RequestCode.TOGGLE_RECORD_PAUSE)
        if not res.requestStatus.result:
            return False
        return True

    @staticmethod
    async def PauseRecord(obs: OBSWebSocket) -> bool:
        res = await obs.request(RequestCode.PAUSE_RECORD)
        if not res.requestStatus.result:
            return False
        return True

    @staticmethod
    async def ResumeRecord(obs: OBSWebSocket) -> bool:
        res = await obs.request(RequestCode.RESUME_RECORD)
        if not res.requestStatus.result:
            return False
        return True
