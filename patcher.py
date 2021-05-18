import re
from typing import Union

from bs4 import BeautifulSoup  # type: ignore
from bs4.element import NavigableString, Tag  # type: ignore

from config import settings

ignore_tags = ('script', 'style', 'html')


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
