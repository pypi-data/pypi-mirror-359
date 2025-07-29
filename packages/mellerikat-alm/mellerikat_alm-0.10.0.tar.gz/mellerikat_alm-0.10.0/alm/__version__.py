import os
import re

def get_version():
    # setup.py 파일 경로
    setup_py_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'setup.py')

    try:
        with open(setup_py_path, 'r') as f:
            content = f.read()
            # version="x.y.z" 패턴 찾기
            match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    except (FileNotFoundError, IOError):
        pass

    # fallback
    return "0.9.0"

__version__ = get_version()

# VERSION = (0, 9, 0)
# __version__ = ".".join(map(str, VERSION))

COPYRIGHT = """
    Copyright (c) 2025, LLO Software

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of ALO Software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.

    Contributor: Sehyun Song, Wonjun Sung, Woosung Jang, Jeongjun Park
    Special Thanks: Sanggyun Seo
    """
