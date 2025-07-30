import asyncio

from aiohttp import FormData


def is_not_empty(s: str) -> bool:
    return bool(s and s.strip())


def extract_last_url(url: str) -> str:
    if url:
        return url.rstrip("/").split("/")[-1]
    return url


def run_async(coro):
    asyncio.run(coro)

def print_form_data(form: FormData) -> str:
    fields = getattr(form, "_fields", None)
    if fields is None:
        return f"{form}"
    else:
        return ", ".join(f"{f[0]["name"]}={f[2]!r}" for f in fields)