"""Bound bytes retained from external process pipes."""


async def read_bounded(reader, limit, on_limit=None, drain=False):
    if type(limit) is not int or limit < 1:
        raise ValueError("limit must be a positive integer")

    chunks = []
    size = 0
    truncated = False
    while chunk := await reader.read(4096):
        remaining = limit - size
        if remaining > 0:
            chunks.append(chunk[:remaining])
            size += min(len(chunk), remaining)
        if len(chunk) > remaining:
            truncated = True
            if on_limit is not None:
                on_limit()
            if not drain:
                break
    return b"".join(chunks), truncated
