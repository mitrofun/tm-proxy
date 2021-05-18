import pytest
from main import patch_word, can_be_replaced, modify_string, modify_html


@pytest.fixture()
def html() -> str:
    return """
        <!DOCTYPE html>
        <html>
            <head>
                <title>Header</title>
                <meta charset="utf-8">
            </head>
            <body>
                <h2>Operating systems</h2>
                <ul id="mylist" style="width:150px">
                    <li><a href="http://haha.hu/sol">Solaris</a></li>
                    <li><a href="http://haha.hu/free">FreeBSD</a></li>
                    <li><a href="http://haha.hu/debian">Debian</a></li>
                    <li><a href="http://haha.hu/n">NetBSD</a></li>
                    <li><a href="http://hha.tu/win">Windows</a></li>
                </ul>
            </body>
        </html>
        """


@pytest.mark.parametrize('test_input, expected', [
    ('server', True),
    ('super', False),
    ('', False),
])
def test_can_be_replaced(test_input, expected):
    assert can_be_replaced(test_input) == expected


@pytest.mark.parametrize('test_input, expected', [
    ('word', 'word'),
    ('superb', 'superb™'),
    ('', ''),
])
def test_patch_word(test_input, expected):
    assert patch_word(test_input) == expected


@pytest.mark.parametrize('test_input, expected', [
    (
        'Вас ждёт более 50 крутых улучшений и новых фич в этом релизе!',
        'Вас ждёт более 50 крутых™ улучшений и новых фич в этом релизе™!',
    ),    (
        'А у кого вы его украли?',
        'А у кого вы его украли™?',
    ),
    ('Читать дальше', 'Читать™ дальше™'),
    ('Erlang/OTP', 'Erlang™/OTP')
])
def test_modify_string(test_input, expected):
    assert modify_string(test_input) == expected


@pytest.mark.asyncio
async def test_modify_text_in_html(html):
    assert '<title>Header™</title>' in await modify_html(html)
    assert 'Debian™' in await modify_html(html)


@pytest.mark.asyncio
async def test_update_link_in_html(html):
    assert '<a href="http://0.0.0.0:8000/free">FreeBSD</a>' in await modify_html(html)
