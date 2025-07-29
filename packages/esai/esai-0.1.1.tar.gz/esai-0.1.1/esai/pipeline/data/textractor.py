import contextlib
import os
import tempfile

from urllib.parse import urlparse
from urllib.request import urlopen, Request

from .filetohtml import FileToHTML
from .htmltomd import HTMLToMarkdown
from .segmentation import Segmentation

class Textractor(Segmentation):
    def __init__(self, sentences=False, lines=False, paragraphs=False, minlength=False, join=False, sections=False, cleantext=False, chunker=None, headers=None, backend="available", **kwargs):
        super().__init__(sentences, lines, paragraphs, sections, minlength, join, cleantext, chunker, **kwargs)

        backend = "tika" if "tika" in kwargs and kwargs["tika"] else None if "tika" in kwargs else backend
        self.html = FileToHTML(backend) if backend else None
        self.markdown = HTMLToMarkdown(self.paragraphs, self.sections)
        self.headers = headers if headers else {}

    def text(self, text):
        path, exists = self.valid(text)

        if not path:
            html = text
        elif self.html:
            path = path if exists else self.download(path)

            html = self.html(path)

            html = html if html else self.retrieve(path)
             
            if not exists:
                os.remove(path)
            
        else:
            html = self.retrieve(path)

        return self.markdown(html)
    
    def valid(self, path):
        path = path.replace("file://", "")
        exists = os.path.exists(path)
        
        return (path if exists or urlparse(path).scheme in ("http", "https") else None, exists)
    
    def download(self, url):
        with tempfile.NamedTemporaryFile(mode="wb", delete=False) as output:
            path = output.name

            output.write(self.retrieve(url))

        return path
    
    def retrieve(self, url):
        if os.path.exists(url):
            with open(url, "rb") as f:
                return f.read()
            
        with contextlib.closing(urlopen(Request(url, headers=self.headers))) as connection:
            return connection.read()
        