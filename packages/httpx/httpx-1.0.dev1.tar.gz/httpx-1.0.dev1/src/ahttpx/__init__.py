from ._client import *  # Client
from ._content import *  # Content, File, Files, Form, HTML, JSON, MultiPart, Text
from ._headers import *  # Headers
from ._network import *  # NetworkBackend, NetworkStream, timeout
from ._pool import *  # Connection, ConnectionPool, Transport
from ._quickstart import *  # get, post, put, patch, delete
from ._response import *  # Response
from ._request import *  # Request
from ._streams import *  # ByteStream, IterByteStream, FileStream, Stream
from ._server import *  # serve_http
from ._urlencode import *  # quote, unquote, urldecode, urlencode
from ._urls import *  # QueryParams, URL


__all__ = [
    "ByteStream",
    "Client",
    "Connection",
    "ConnectionPool",
    "Content",
    "delete",
    "File",
    "FileStream",
    "Files",
    "Form",
    "get",
    "Headers",
    "HTML",
    "IterByteStream",
    "JSON",
    "MultiPart",
    "NetworkBackend",
    "NetworkStream",
    "open_connection",
    "post",
    "put",
    "patch",
    "Response",
    "Request",
    "serve_http",
    "Stream",
    "Text",
    "timeout",
    "Transport",
    "QueryParams",
    "quote",
    "unquote",
    "URL",
    "urldecode",
    "urlencode",
]


__locals = locals()
for __name in __all__:
    setattr(__locals[__name], "__module__", "httpx")
