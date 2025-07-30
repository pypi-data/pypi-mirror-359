# -*- coding: utf-8 -*-
"""
Created on 2025/6/15 19:42
@author: guest881
"""

import asyncio
from Decorators import *

@async_retry()
async def test(i):
    raise ValueError("123{}".format(i))
async def thread_main():
    tasks=[test(i) for i in range(2)]
    await asyncio.gather(*tasks)
async def main():
    await test()
asyncio.run(thread_main())
@retry()
def test2(i):
    raise ValueError("456{}".format(i))
[test2(i)for i in range(2)]