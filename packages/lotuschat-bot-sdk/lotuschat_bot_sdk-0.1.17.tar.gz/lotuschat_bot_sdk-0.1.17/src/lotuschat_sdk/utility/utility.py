import asyncio


def is_not_empty(s: str) -> bool:
    return bool(s and s.strip())


def extract_last_url(url: str) -> str:
    if url:
        return url.rstrip("/").split("/")[-1]
    return url


def run_async(coro):
    asyncio.run(coro)
