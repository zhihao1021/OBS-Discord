from asyncio import CancelledError, get_event_loop, new_event_loop, ProactorEventLoop, Queue, set_event_loop, sleep as asleep, Task
from typing import Optional, Any, Union

from simpleobsws import WebSocketClient, Request

from pydantic import BaseModel, Field

class RequestStatus(BaseModel):
    result: bool
    code: int
    comment: Optional[str]

class ResponseData(BaseModel):
    requestType: str
    requestStatus: RequestStatus
    responseData: Optional[dict[str, Any]]=None

class OBSWebSocket:
    def __init__(
        self,
        host: str="localhost",
        port: int=4455,
        passwd: str="",
    ) -> None:
        self.address = "ws://{}:{}".format(host, port)
        self.passwd = passwd

        self.ws = WebSocketClient(url=self.address, password=self.passwd)
        self.connected = False
    
    async def request(self, requestType: str, requestData: Optional[dict[str, Any]]=None) -> ResponseData:
        request = Request(requestType, requestData)
        ret = await self.ws.call(request)
        result = None
        if ret:
            result = ResponseData(**{
                "requestType": ret.requestType,
                "requestStatus": ret.requestStatus,
                "responseData": ret.responseData
            })
        return result
    
    async def connect(self):
        if self.connected:
            return
        
        await self.ws.connect()
        await self.ws.wait_until_identified()

        self.connected = True
    
    async def close(self):
        await self.ws.disconnect()
