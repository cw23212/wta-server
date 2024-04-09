import json
import aiohttp
import functools

import logging
logger = logging.getLogger("wta."+__name__)


class LoggingClientSession(aiohttp.ClientSession):
    async def _request(self, method, url, **kwargs):
        logging.getLogger('aiohttp.client').debug(
            'Starting request <%s %r %s>', method, url, str(kwargs))
        return await super()._request(method, url, **kwargs)


def getTraceConfig():
    trace_config = aiohttp.TraceConfig()
    trace_config.on_request_start.append(on_request_start)
    return [trace_config]


def getClientSession(debug=False):
    return aiohttp.ClientSession() if not debug else LoggingClientSession()


async def get(url, debug=False):
    async with getClientSession(debug) as session:
        async with session.get(url) as response:
            return await response.text()


async def post(url, *, data=None, debug=False, headers=None):
    async with getClientSession(debug) as session:
        async with session.post(url, data=data, headers=headers) as response:
            return await response.text()


async def jsonPost(url, data=None, *, debug=False, **k):
    if data == None:
        data = k
    headers = {'Content-Type': 'application/json'}
    return await post(url, data=json.dumps(data), headers=headers, debug=debug)
