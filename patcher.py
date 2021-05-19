# import re
from typing import Union

from bs4 import BeautifulSoup  # type: ignore
from bs4.element import NavigableString, Tag  # type: ignore

from nltk.tokenize import regexp_tokenize  # type: ignore

from config import settings

ignore_tags = ('script', 'style')


def replace_url(link: str):
    if not link:
        return
    return link.replace(settings.source_url, f'http://{settings.host}/')


def patch_word(word: str) -> str:
    return f'{word}™' if len(word) == settings.word_len else word


def modify_string(text: str) -> str:
    # ((( hack
    if '™™' in text:
        return text.replace('™™', '™')

    words = list(set(regexp_tokenize(text, pattern=r'\w+|\$[\d\.]+|\S+')))
    for word in words:
        text = text.replace(word, patch_word(word))
    return text


def modify_link(tag) -> None:

    map_tag_name_to_attr = {
        'a': 'href',
        'use': 'xlink:href'
    }

    for tag_name, html_att in map_tag_name_to_attr.items():
        if tag.name == tag_name:
            tag.attrs[html_att] = replace_url(tag.attrs.get(html_att))


def modify_tag(tag: Union[Tag, NavigableString]) -> None:

    for child_tag in tag.children:
        if isinstance(child_tag, NavigableString):
            child_tag.string.replace_with(modify_string(str(child_tag)))


async def modify_html(html_content: bytes) -> str:
    soup = BeautifulSoup(html_content, 'html5lib')
    for tag in soup.find_all():
        if tag.name not in ignore_tags:
            modify_tag(tag)
        if tag.name in ('a', 'use'):
            modify_link(tag)
    return str(soup)
