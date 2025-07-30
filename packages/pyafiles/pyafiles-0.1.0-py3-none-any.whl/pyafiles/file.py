import asyncio
from concurrent.futures import ThreadPoolExecutor

_executor = ThreadPoolExecutor()

class AsyncFile:
    def __init__(self, filename, mode='r', encoding='utf-8'):
        self.filename = filename
        self.mode = mode
        self.encoding = encoding
        self._file = None

    async def __aenter__(self):
        loop = asyncio.get_running_loop()
        self._file = await loop.run_in_executor(
            _executor,
            lambda: open(self.filename, self.mode, encoding=self.encoding)
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        loop = asyncio.get_running_loop()
        await loop.run_in_executor(_executor, self._file.close)

    async def read(self):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_executor, self._file.read)

    async def write(self, data):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_executor, self._file.write, data)

    async def readline(self):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_executor, self._file.readline)

    async def readlines(self):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_executor, self._file.readlines)

    async def writelines(self, lines):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(_executor, self._file.writelines, lines)
