from typing import Union

import httpx

from fastapi import FastAPI, Header, HTTPException, status
from fastapi.responses import Response

from config import settings
from patcher import modify_html


async def fetch_data(url: str) -> httpx.Response:
    try:
        async with httpx.AsyncClient() as client:
            res: httpx.Response = await client.get(url)
            return res
    except httpx.ConnectTimeout:
        raise HTTPException(
            status_code=status.HTTP_408_REQUEST_TIMEOUT,
            detail='Check internet connection.',
        )
    except httpx.ConnectError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Host: "{settings.source_url}" not found.Check proxy settings.',
        )


async def get_content(url: str) -> tuple[Union[str, bytes], str]:
    prefix = settings.source_url
    data = await fetch_data(f'{prefix}{url}')

    # Modify only html
    if 'text/html' in data.headers.get('content-type'):
        updated_text = await modify_html(data.content)
        return updated_text, data.headers.get('content-type')

    return data.content, data.headers.get('content-type')


app = FastAPI(
    title='Proxy TM',
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
)


@app.get('/{url:path}')
async def proxy(url: str, host: str = Header(None)):
    settings.host = host
    content, media_type = await get_content(url)
    return Response(content=content, media_type=media_type, headers={'host': host})
