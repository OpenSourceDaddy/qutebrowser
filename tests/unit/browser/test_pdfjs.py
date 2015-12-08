# vim: ft=python fileencoding=utf-8 sts=4 sw=4 et:

# Copyright 2015 Daniel Schadt
#
# This file is part of qutebrowser.
#
# qutebrowser is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# qutebrowser is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with qutebrowser.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for qutebrowser.browser.pdfjs"""

import textwrap

import pytest
from PyQt5.QtCore import QUrl

from qutebrowser.browser import pdfjs


# Note that we got double protection, once because we use QUrl.FullyEncoded and
# because we use qutebrowser.browser.webelem.javascript_escape.  Characters
# like " are already replaced by QUrl.
@pytest.mark.parametrize('url, expected', [
    ('http://foo.bar', 'PDFView.open("http://foo.bar");\n'),
    ('http://"', 'PDFView.open("");\n'),
    ('\0', 'PDFView.open("%00");\n'),
    ('http://foobar/");alert("attack!");',
     'PDFView.open("http://foobar/%22);alert(%22attack!%22);");\n'),
])
def test_generate_pdfjs_script(url, expected):
    url = QUrl(url)
    actual = pdfjs._generate_pdfjs_script(url)
    assert actual == expected


def test_fix_urls():
    page = textwrap.dedent("""
        <html>
        <script src="viewer.js"></script>
        <link href="viewer.css">
        <script src="unrelated.js"></script>
        </html>
    """).strip()

    expected = textwrap.dedent("""
        <html>
        <script src="qute://pdfjs/web/viewer.js"></script>
        <link href="qute://pdfjs/web/viewer.css">
        <script src="unrelated.js"></script>
        </html>
    """).strip()

    actual = pdfjs.fix_urls(page)
    assert actual == expected


@pytest.mark.parametrize('path, expected', [
    ('web/viewer.js', 'viewer.js'),
    ('build/locale/foo.bar', 'locale/foo.bar'),
    ('viewer.js', 'viewer.js'),
    ('foo/viewer.css', 'foo/viewer.css'),
])
def test_remove_prefix(path, expected):
    assert pdfjs._remove_prefix(path) == expected

