from typing import Union

import httpx

from bs4 import BeautifulSoup  # type: ignore
from bs4.element import Doctype, NavigableString  # type: ignore

from fastapi import FastAPI, HTTPException, status
from fastapi.responses import HTMLResponse
from pydantic import BaseSettings


class Settings(BaseSettings):
    source_url: str = 'https://habr.com/ru/'
    local_url: str = 'http://0.0.0.0:8000/'

    class Config:
        env_file = 'config.env'


settings = Settings()


async def fetch_content(url: str) -> str:
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
            return r.text
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


def replace_link(link: str):
    if not link:
        return
    return link.replace(settings.source_url, settings.local_url)


def can_be_replaced(word: str) -> bool:
    list_of_exception_characters = ('.', ',', '!', '?', '™')
    if len(word) != 6:
        return False
    for char in list_of_exception_characters:
        if char in word:
            return False
    return True


def replace_word(word: str) -> str:
    if not can_be_replaced(word):
        return word
    return f'{word}™'


def update_string(string: str) -> str:
    words: list = string.split(' ')

    for index, word in enumerate(words):
        words[index] = replace_word(word)

    return ' '.join(words)


async def update_text(node: Union[NavigableString, Doctype]) -> None:

    if type(node) == Doctype:
        return
    if node.name == 'a':
        node.attrs['href'] = replace_link(node.attrs.get('href'))
    if node.string:
        node.string.replace_with(update_string(string=node.string))

    if hasattr(node, 'children'):
        for child in node.children:
            await update_text(child)


async def update_html(text_page: str) -> str:
    soup = BeautifulSoup(text_page, 'html.parser')
    for node in soup.children:
        await update_text(node)
    return str(soup)


async def get_content(url) -> str:
    prefix = settings.source_url
    text_page = await fetch_content(f'{prefix}{url}')
    updated_text = await update_html(text_page)
    return updated_text


app = FastAPI(
    title='Proxy TM',
    docs_url=None,
    openapi_url=None,
    redoc_url=None,
)


@app.get('/{url:path}', response_class=HTMLResponse)
async def proxy_pages(url: str):
    content = await get_content(url)
    return content
