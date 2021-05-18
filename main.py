import re
from typing import Union

import httpx

from bs4 import BeautifulSoup  # type: ignore
from bs4.element import NavigableString, Tag  # type: ignore

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import Response
from pydantic import BaseSettings


class Settings(BaseSettings):
    source_url: str = 'https://habr.com/'
    local_url: str = 'http://0.0.0.0:8000/'
    word_len: int = 6

    class Config:
        env_file = 'config.env'


settings = Settings()


ignore_tags = ('script', 'style', 'html')


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


def replace_url(link: str):
    if not link:
        return
    return link.replace(settings.source_url, settings.local_url)


def can_be_replaced(word: str) -> bool:
    if '\n' in word or len(word) != settings.word_len:
        return False
    return True


def patch_word(word: str) -> str:
    if not can_be_replaced(word):
        return word
    return f'{word}™'


def modify_string(text: str) -> str:
    words = re.split(r'(\W+)', text)
    for index, word in enumerate(words):
        words[index] = patch_word(word)
    return ''.join(words)


def modify_link(tag) -> None:

    map_tag_name_to_attr = {
        'a': 'href',
        'use': 'xlink:href'
    }

    for tag_name, html_att in map_tag_name_to_attr.items():
        if tag.name == tag_name:
            tag.attrs[html_att] = replace_url(tag.attrs.get(html_att))


def modify_tag(tag: Union[Tag, NavigableString]) -> None:

    if tag.name in ignore_tags:
        return

    modify_link(tag)

    if tag.string and tag.children:

        for child_tag in tag.children:
            try:
                modify_tag(child_tag)
            # NavigableString objects have no attributes; only Tag objects have them.
            except AttributeError:
                child_tag.parent.string = modify_string(child_tag)


async def modify_html(html_content: bytes) -> str:
    soup = BeautifulSoup(html_content, 'html5lib')
    for tag in soup.find_all(name=True):
        modify_tag(tag)
    return str(soup)


async def get_content(url) -> tuple[Union[str, bytes], str]:
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
async def proxy(url: str):
    content, media_type = await get_content(url)
    return Response(content=content, media_type=media_type)
