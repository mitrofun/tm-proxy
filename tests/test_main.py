import pytest
from main import replace_word, can_be_replaced, update_string, update_html


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
    ('super?', False),
    ('', False),
])
def test_can_be_replaced(test_input, expected):
    assert can_be_replaced(test_input) == expected


@pytest.mark.parametrize('test_input, expected', [
    ('1', '1'),
    ('word', 'word'),
    ('superb', 'superb™'),
    ('super.', 'super.'),
    ('super,', 'super,'),
    ('super!', 'super!'),
    ('', ''),
])
def test_update_word(test_input, expected):
    assert replace_word(test_input) == expected


@pytest.mark.parametrize('test_input, expected', [
    (
        'Вас ждёт более 50 крутых улучшений и новых фич в этом релизе!',
        'Вас ждёт более 50 крутых™ улучшений и новых фич в этом релизе!',
    ),
    ('Читать дальше', 'Читать™ дальше™')
])
def test_update_string(test_input, expected):
    assert update_string(test_input) == expected


@pytest.mark.asyncio
async def test_update_text_in_html(html):
    assert 'Header™' in await update_html(html)
    assert 'Debian™' in await update_html(html)


@pytest.mark.asyncio
async def test_update_link_in_html(html):
    assert '<li><a href="http://0.0.0.0:8000/free">FreeBSD</a></li>' in await update_html(html)
