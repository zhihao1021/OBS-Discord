from asyncio import CancelledError, get_event_loop, new_event_loop, ProactorEventLoop, Queue, set_event_loop, sleep as asleep, Task
from base64 import b64encode
from hashlib import sha256, sha1
from threading import Thread
from time import time
from random import random
from typing import Any, Optional, Union

from aiohttp import ClientSession, ClientTimeout
from aiohttp.typedefs import DEFAULT_JSON_DECODER, DEFAULT_JSON_ENCODER, JSONDecoder, JSONEncoder
from pydantic import BaseModel, Field

class RequestStatus(BaseModel):
    result: bool
    code: int
    comment: Optional[str]

class RequestData(BaseModel):
    requestType: str
    requestId: str=Field(default_factory=lambda: sha1(str(time() * random()).encode()).hexdigest())
    requestData: Optional[dict[str, Any]]=None

class ResponseData(BaseModel):
    requestType: str
    requestId: str
    requestStatus: RequestStatus
    responseData: Optional[dict[str, Any]]=None

class WebSocketData(BaseModel):
    op: int=Field(ge=2, le=9)
    d: Union[dict, RequestData, ResponseData]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.op == 6:
            self.d = RequestData(**self.d)
        elif self.op == 7:
            self.d = ResponseData(**self.d)

class OBSWebSocket:
    def __init__(
        self,
        host: str="localhost",
        port: int=4455,
        passwd: str="",
        client: Optional[ClientSession]=None,
        timeout: float=10,
        loads: JSONDecoder=DEFAULT_JSON_DECODER,
        dumps: JSONEncoder=DEFAULT_JSON_ENCODER,
        loop: Optional[ProactorEventLoop]=None,
    ) -> None:
        self.address = "ws://{}:{}".format(host, port)
        self.passwd = passwd

        self.client = client if client else self.__new_client(timeout)
        self.loads = loads
        self.dumps = dumps
        
        self.tasks: list[Task] = []
        self.responses: dict[str, ResponseData] = {}

        self.thr = Thread(target=self.__thread_job, name="OBS WebSocket Receive Thread")
        self.send_queue = Queue()

        loop = loop if loop else get_event_loop()
        if loop.is_closed():
            loop = new_event_loop()
            set_event_loop(loop)
        self.loop = loop
    
    def __thread_job(self):
        self.tasks = [
            self.loop.create_task(self.__recv_task(), name="OBS Websocket Receive Task")
            for _ in range(3)
        ]
        self.tasks.append(
            self.loop.create_task(self.__send_task(), name="OBS Websocket Send Task")
        )
        if not self.loop.is_running():
            for task in self.tasks:
                self.loop.run_until_complete(task)
        return
    
    async def __recv_task(self):
        while True:
            try:
                raw_data: dict = await self.ws.receive_json()
                print(raw_data)
                if raw_data["op"] != 7:
                    continue
                data = ResponseData(**raw_data["d"])
                uuid = data.requestId
                self.responses[uuid] = data
            except CancelledError:
                return
    
    async def __send_task(self):
        while True:
            try:
                data: RequestData = await self.send_queue.get()
                ws_data = WebSocketData(**{"op": 6, "d": data})
                await self.ws.send_json(ws_data.dict(), dumps=self.dumps)
            except CancelledError:
                return
    
    async def request(self, requestType: str, requestData: Optional[dict[str, Any]]=None) -> ResponseData:
        data = RequestData(**{
            "requestType": requestType,
            "requestData": requestData
        })
        await self.send_queue.put(data)
        while not (result := self.responses.get(data.requestId)):
            await asleep(0.01)
        del self.responses[data.requestId]
        return result
    
    async def connect(self):
        if self.thr.is_alive():
            return
        self.client = self.__new_client() if self.client.closed else self.client
        self.ws = await self.client.ws_connect(self.address)

        res: dict[str, dict] = await self.ws.receive_json(loads=self.loads)
        
        authData = res["d"].get("authentication")
        authentication = await self.__auth_string(**authData) if authData else ""

        await self.ws.send_json({
            "op": 1,
            "d": {
                "rpcVersion": 1,
                "authentication": authentication,
                # "eventSubscriptions": 33
            }
        }, dumps=self.dumps)

        await self.ws.receive()

        self.thr.start()
    
    async def start_record(self):
        pass
    
    async def close(self):
        for task in self.tasks:
            task.cancel()
        self.loop.stop()
        self.loop.close()
        self.thr.join()

        await self.ws.close()
        await self.client.close()
    
    async def __auth_string(self, challenge: str, salt: str) -> str:
        secret = b64encode(
            sha256((self.passwd + salt).encode("utf-8")).digest()
        )
        auth = b64encode(
            sha256(secret + challenge.encode("utf-8")).digest()
        ).decode("utf-8")
        return auth
    
    def __new_client(self, timeout: float) -> ClientSession:
        return ClientSession(timeout=ClientTimeout(connect=timeout, sock_read=timeout, sock_connect=timeout))
