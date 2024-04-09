import asyncio
from threading import Thread
from functools import cache
import logging
@cache
def getLoop():
    loop = asyncio.new_event_loop()
    def side_thread(loop):
        asyncio.set_event_loop(loop)
        loop.run_forever()    
    thread = Thread(target=side_thread, args=(loop,), daemon=True)
    thread.start()
    return loop

import traceback
def run_async(f,*args, **kargs):
    async def _with_err_print(_f):
        try:
            await _f
        except Exception as e:            
            logging.exception(e)
    future = asyncio.run_coroutine_threadsafe(_with_err_print(f), getLoop())
    return future


