import pytest
from patcher import patch_word, modify_string, modify_html


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
                <i><font color="gray">Другие старые устройства</font></i>
                <ul id="mylist" style="width:150px">
                    <li><a href="http://haha.hu/sol">Solaris</a></li>
                    <li><a href="http://haha.hu/free">FreeBSD</a></li>
                    <li><a href="http://haha.hu/debian">Debian</a></li>
                    <li><a href="http://haha.hu/n">NetBSD</a></li>
                    <li><a href="http://hha.tu/win">Windows</a></li>
                </ul>
                <div>
                    <a href="http://erlang.org/pipermail/erlang-questions/2008-October/039176.html">
                    erlang.org/pipermail/erlang-questions/2008-October/039176.html</a>
                </div>
            </body>
        </html>
        """


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
    ),
    (
        'А у кого вы его украли?',
        'А у кого вы его украли™?',
    ),
    (
        'которому я в итоге пришёл.',
        'которому я в итоге пришёл™.',
    ),
    (
        'тонкие шпации...',
        'тонкие™ шпации™...',
    ),
    (
        '# ... продолжение предыдущего примера',
        '# ... продолжение предыдущего примера',
    ),
    ('Читать дальше', 'Читать™ дальше™'),
    ('Erlang/OTP', 'Erlang™/OTP')
])
def test_modify_string(test_input, expected):
    assert modify_string(test_input) == expected


@pytest.mark.asyncio
async def test_modify_text_in_html(html):
    html_text = await modify_html(html)
    assert '<title>Header™</title>' in html_text
    assert 'Debian™™' not in html_text
    assert 'Другие™ старые™ устройства' in html_text
    assert 'erlang™.org/pipermail/erlang™-questions/2008-October/039176.html' in html_text


@pytest.mark.asyncio
async def test_update_link_in_html(html):
    html_text = await modify_html(html)
    assert '<a href="http://0.0.0.0:9999/free">FreeBSD</a>' in html_text
    assert '<li><a href="http://0.0.0.0:9999/debian">Debian™</a></li>' in html_text
