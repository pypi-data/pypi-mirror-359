# asyncfiles

A minimal async file I/O library using asyncio and thread pool executors.

## Usage

```python
from pyafiles import AsyncFile
import asyncio

async def main():
    async with AsyncFile('example.txt', 'w') as f:
        await f.write('Hello!')

    async with AsyncFile('example.txt', 'r') as f:
        data = await f.read()
        print(data)

asyncio.run(main())
```

## Features
- Asynchronous file operations using `asyncio`.
- Supports reading, writing, and appending to files.
- Context manager for automatic resource management.
- Uses thread pool executors for blocking I/O operations.

## Installation
You can install the library using pip:

```bash
pip install pyafiles
```

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug
fixes.

## Requirements
- Python 3.7 or higher

## Limitations
- This library is designed for simple file operations and may not be suitable for high-performance applications.
