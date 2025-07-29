'''
MIT License

Copyright (c) 2025 Fatih Kuloglu

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import asyncio
import aiohttp
import json

from .utils import MISSING
from typing import Any
from urllib.parse import quote
from loguru import logger

class Route:
    '''
        Represents an API route with a method and path, used to build full request URLs
        for the Teamly API.

        Example:
            Route("GET", "/channels/{channel_id}", channel_id="1234")
            → https://api.teamly.one/api/v1/channels/1234

        Attributes:
            BASE_URL (str): The base URL for all API requests.
            method (str): The HTTP method (e.g., "GET", "POST").
            path (str): The API path, possibly containing placeholders.
            url (str): The fully constructed request URL.
    '''

    BASE_URL = "https://api.teamly.one/api/v1"

    def __init__(self, method:str, path: str, **params: Any) -> None:
        self.method = method
        self.path = path

        url = self.BASE_URL + self.path
        if params:
            url = url.format_map({
                k: quote(v, safe='') if isinstance(v, str) else v
                for k, v in params.items()
            })
        self.url: str = url

class HTTPClient:

    def __init__(self, loop: asyncio.AbstractEventLoop) -> None:
        self._session: aiohttp.ClientSession = MISSING
        self.token = None
        self.loop: asyncio.AbstractEventLoop = loop

    async def static_login(self, token: str):
        logger.debug("static logging...")

        self.token = token
        self._session = aiohttp.ClientSession()

    async def close(self):
        logger.debug("closing client session...")
        await self._session.close()

    async def ws_connect(self) -> aiohttp.ClientWebSocketResponse:
        logger.debug("creating ws connect...")

        kwargs = {
            "timeout": 30,
            "max_msg_size": 0,
            "headers": {
                "Authorization": f'Bot {self.token}'
            }
        }

        return await self._session.ws_connect(url="wss://api.teamly.one/api/v1/ws", **kwargs)

    async def request(self, route: Route, **kwargs) -> Any:
        method = route.method
        url = route.url

        #creating headers
        headers = {}

        if self.token is not None:
            headers["Authorization"] = f'Bot {self.token}'

        if 'json' in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs['data'] = json.dumps(kwargs.pop('json'))

        kwargs["headers"] = headers

        try:
            logger.debug("making request...")
            return await self._session.request(method, url, **kwargs)
        except Exception as e:
            logger.error("Exception error: {}",e)
