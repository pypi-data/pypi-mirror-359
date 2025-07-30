"""mureq is a replacement for python-requests, intended to be vendored
in-tree by Linux systems software and other lightweight applications.

mureq is copyright 2021 by its contributors and is released under the
0BSD ("zero-clause BSD") license.
"""

import contextlib
import io
import socket
import ssl
import sys
import urllib.parse
from collections.abc import Generator, MutableMapping
from http import HTTPStatus
from http.client import (
    HTTPConnection,
    HTTPException,
    HTTPMessage,
    HTTPResponse,
    HTTPSConnection,
)
from typing import cast

__version__ = "0.3.0"

__all__ = [
    "HTTPException",
    "Response",
    "TooManyRedirects",
    "delete",
    "get",
    "head",
    "patch",
    "post",
    "put",
    "request",
    "yield_response",
]

DEFAULT_TIMEOUT: float = 3

# e.g. "Python 3.8.10"
DEFAULT_UA = "Python " + sys.version.split()[0]

Headers = MutableMapping[str, str] | HTTPMessage
# pyrefly: ignore  # not-a-type
JsonValue = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]


def request(
    method: str,
    url: str,
    *,
    read_limit: int | None = None,
    **kwargs,
) -> "Response":
    """Request performs an HTTP request and reads the entire response body.

    :param str method: HTTP method to request (e.g. 'GET', 'POST')
    :param str url: URL to request
    :param read_limit: maximum number of bytes to read from the body, or None for no limit
    :type read_limit: int or None
    :param kwargs: optional arguments defined by yield_response
    :return: Response object
    :rtype: Response
    :raises: HTTPException
    """  # noqa: E501
    with yield_response(method, url, **kwargs) as response:
        try:
            body = response.read(read_limit)
        except HTTPException:
            raise
        except OSError as e:
            raise HTTPException(str(e)) from e
        return Response(
            response.url,
            response.status,
            _prepare_incoming_headers(response.headers),
            body,
        )


def get(url: str, *, auto_retry: bool = False, **kwargs) -> str:
    """Performs an HTTP GET request.

    See yield_response for kwargs.
    """
    try:
        return request("GET", url=url, **kwargs).body.decode("utf-8")
    except TimeoutError:
        if auto_retry:
            return get(url, auto_retry=False, **kwargs)
        raise


def post(url: str, body: bytes | None = None, **kwargs) -> "Response":
    """Performs an HTTP POST request.

    See yield_response for kwargs.
    """
    return request("POST", url=url, body=body, **kwargs)


def head(url: str, **kwargs) -> "Response":
    """Performs an HTTP HEAD request.

    See yield_response for kwargs.
    """
    return request("HEAD", url=url, **kwargs)


def put(url: str, body: bytes | None = None, **kwargs) -> "Response":
    """Performs an HTTP PUT request.

    See yield_response for kwargs.
    """
    return request("PUT", url=url, body=body, **kwargs)


def patch(url: str, body: bytes | None = None, **kwargs) -> "Response":
    """Performs an HTTP PATCH request.

    See yield_response for kwargs.
    """
    return request("PATCH", url=url, body=body, **kwargs)


def delete(url: str, **kwargs) -> "Response":
    """Performs an HTTP DELETE request.

    See yield_response for kwargs.
    """
    return request("DELETE", url=url, **kwargs)


@contextlib.contextmanager
def yield_response(  # noqa: PLR0913
    method: str,
    url: str,
    *,
    unix_socket: str | None = None,
    timeout: float | None = DEFAULT_TIMEOUT,
    headers: Headers | list[tuple[str, str]] | None = None,
    params: dict[str, str | bytes] | list[tuple[str, str | bytes]] | None = None,
    body: bytes | None = None,
    form: dict[str, str | bytes] | list[tuple[str, str | bytes]] | None = None,
    json: JsonValue | None = None,
    verify: bool = True,
    source_address: str | tuple[str, int] | None = None,
    max_redirects: int | None = None,
    ssl_context: ssl.SSLContext | None = None,
) -> Generator[HTTPResponse, None, None]:
    """yield_response is a low-level API that exposes the actual
    http.client.HTTPResponse via a contextmanager.

    Note that unlike mureq.Response, http.client.HTTPResponse does not
    automatically canonicalize multiple appearances of the same header by
    joining them together with a comma delimiter. To retrieve canonicalized
    headers from the response, use response.getheader():
    https://docs.python.org/3/library/http.client.html#http.client.HTTPResponse.getheader

    :param str method: HTTP method to request (e.g. 'GET', 'POST')
    :param str url: URL to request
    :param unix_socket: path to Unix domain socket to query, or None for a normal TCP request
    :type unix_socket: str or None
    :param timeout: timeout in seconds, or None for no timeout (default: 15 seconds)
    :type timeout: float or None
    :param headers: HTTP headers as a mapping or list of key-value pairs
    :param params: parameters to be URL-encoded and added to the query string, as a mapping or list of key-value pairs
    :param body: payload body of the request
    :type body: bytes or None
    :param form: parameters to be form-encoded and sent as the payload body, as a mapping or list of key-value pairs
    :param json: object to be serialized as JSON and sent as the payload body
    :param bool verify: whether to verify TLS certificates (default: True) - it is highly recommended to set this True
    :param source_address: source address to bind to for TCP
    :type source_address: str or tuple(str, int) or None
    :param max_redirects: maximum number of redirects to follow, or None (the default) for no redirection
    :type max_redirects: int or None
    :param ssl_context: TLS config to control certificate validation, or None for default behavior
    :type ssl_context: ssl.SSLContext or None
    :return: http.client.HTTPResponse, yielded as context manager
    :rtype: http.client.HTTPResponse
    :raises: HTTPException
    """  # noqa: E501
    method = method.upper()
    headers = cast("MutableMapping[str, str]", _prepare_outgoing_headers(headers))
    enc_params = _prepare_params(params)
    prepared_body = _prepare_body(body, form, json, headers)

    visited_urls: list[str] = []

    while max_redirects is None or len(visited_urls) <= max_redirects:
        url, conn, path = _prepare_request(
            url=url,
            enc_params=enc_params,
            timeout=timeout,
            unix_socket=unix_socket,
            verify=verify,
            source_address=source_address,
            ssl_context=ssl_context,
        )
        enc_params = ""  # don't reappend enc_params if we get redirected
        visited_urls.append(url)
        try:
            try:
                conn.request(method, path, headers=headers, body=prepared_body)
                response = conn.getresponse()
            except TimeoutError:
                raise
            except HTTPException:
                raise
            except OSError as e:
                # wrap any IOError that is not already an HTTPException
                # in HTTPException, exposing a uniform API for remote errors
                raise HTTPException(str(e)) from e
            redirect_url = _check_redirect(url, response.status, response.headers)
            if max_redirects is None or redirect_url is None:
                response.url = url  # https://bugs.python.org/issue42062
                yield response
                return
            else:
                url = str(redirect_url)
                if response.status == HTTPStatus.SEE_OTHER:
                    # 303 See Other: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status/303
                    method = "GET"
        finally:
            conn.close()

    raise TooManyRedirects(visited_urls)


class Response:
    """Response contains a completely consumed HTTP response."""

    __slots__ = ("body", "headers", "status_code", "url")

    def __init__(
        self,
        url: str,
        status_code: int,
        headers: Headers,
        body: bytes,
    ) -> None:
        """Initialize a Response object.

        :ivar str url: the retrieved URL, indicating whether a redirection occurred
        :ivar int status_code: the HTTP status code
        :ivar http.client.HTTPMessage headers: the HTTP headers
        :ivar bytes body: the payload body of the response
        """
        self.url, self.status_code, self.headers, self.body = (
            url,
            status_code,
            headers,
            body,
        )

    def __repr__(self) -> str:
        return f"Response(status_code={self.status_code:d})"

    @property
    def ok(self) -> bool:
        """Ok returns whether the response had a successful status code
        (anything other than a 40x or 50x).
        """
        return not (
            HTTPStatus.BAD_REQUEST
            <= self.status_code
            < HTTPStatus.NETWORK_AUTHENTICATION_REQUIRED
        )

    @property
    def content(self) -> bytes:
        """Content returns the response body (the `body` member). This is an
        alias for compatibility with requests.Response.
        """
        return self.body

    def raise_for_status(self) -> None:
        """raise_for_status checks the response's success code, raising an
        exception for error codes.
        """
        if not self.ok:
            raise HTTPErrorStatus(self.status_code)

    def json(self) -> JsonValue:
        """Attempts to deserialize the response body as UTF-8 encoded JSON."""
        import json as jsonlib  # noqa: PLC0415

        return jsonlib.loads(self.body)

    def _debugstr(self) -> str:
        buf = io.StringIO()
        print("HTTP", self.status_code, file=buf)
        for k, v in self.headers.items():
            print(f"{k}: {v}", file=buf)
        print(file=buf)
        try:
            print(self.body.decode("utf-8"), file=buf)
        except UnicodeDecodeError:
            print(f"<{len(self.body)} bytes binary data>", file=buf)
        return buf.getvalue()


class TooManyRedirects(HTTPException):
    """TooManyRedirects is raised when automatic following of redirects was
    enabled, but the server redirected too many times without completing.
    """


class HTTPErrorStatus(HTTPException):
    """HTTPErrorStatus is raised by Response.raise_for_status() to indicate an
    HTTP error code (a 40x or a 50x). Note that a well-formed response with an
    error code does not result in an exception unless raise_for_status() is
    called explicitly.
    """

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code

    def __str__(self) -> str:
        return f"HTTP response returned error code {self.status_code:d}"


# end public API, begin internal implementation details

_JSON_CONTENTTYPE = "application/json"
_FORM_CONTENTTYPE = "application/x-www-form-urlencoded"


class UnixHTTPConnection(HTTPConnection):
    """UnixHTTPConnection is a subclass of HTTPConnection that connects to a
    Unix domain stream socket instead of a TCP address.
    """

    def __init__(self, path: str, timeout: float | None = DEFAULT_TIMEOUT) -> None:
        super().__init__("localhost", timeout=timeout)
        self._unix_path = path

    def connect(self) -> None:
        sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        try:
            sock.settimeout(self.timeout)
            sock.connect(self._unix_path)
        except Exception:
            sock.close()
            raise
        self.sock = sock


def _check_redirect(url: str, status: int, response_headers: Headers) -> str | None:
    """Return the URL to redirect to, or None for no redirection."""
    if status not in (301, 302, 303, 307, 308):
        return None
    location = response_headers.get("Location")
    if not location:
        return None
    parsed_location = urllib.parse.urlparse(location)
    if parsed_location.scheme:
        # absolute URL
        return location

    old_url = urllib.parse.urlparse(url)
    if location.startswith("/"):
        # absolute path on old hostname
        return str(
            urllib.parse.urlunparse(
                (
                    old_url.scheme,
                    old_url.netloc,
                    parsed_location.path,
                    parsed_location.params,
                    parsed_location.query,
                    parsed_location.fragment,
                ),
            ),
        )

    # relative path on old hostname
    return urllib.parse.urljoin(url, location)


def _prepare_outgoing_headers(
    headers: Headers | list[tuple[str, str]] | None,
) -> HTTPMessage:
    if headers is None:
        headers = HTTPMessage()
    elif not isinstance(headers, HTTPMessage):
        new_headers = HTTPMessage()
        if isinstance(headers, list):
            for k, v in headers:
                new_headers[k] = v
        else:
            for k, v in headers.items():
                new_headers[k] = v
        headers = new_headers
    _setdefault_header(headers, "User-Agent", DEFAULT_UA)
    return headers


# XXX: Issue #15 join multi-headers together so that get(), __getitem__(),
# etc. behave intuitively, then stuff them back in an HTTPMessage.
def _prepare_incoming_headers(headers: Headers) -> HTTPMessage:
    headers_dict: dict[str, list[str]] = {}
    for k, v in headers.items():
        headers_dict.setdefault(k, []).append(v)
    result = HTTPMessage()
    # note that iterating over headers_dict preserves the original
    # insertion order in all versions since Python 3.6:
    # XXX: Issue #15: this is incorrect for some headers, notably Set-Cookie
    for k, vlist in headers_dict.items():
        result[k] = ",".join(vlist)
    return result


def _setdefault_header(headers: Headers, name: str, value: str) -> None:
    if name not in headers:
        headers[name] = value  # type: ignore[index]


def _prepare_body(
    body: bytes | None,
    form: dict[str, str | bytes] | list[tuple[str, str | bytes]] | None,
    json: JsonValue | None,
    headers: Headers,
) -> bytes | str | None:
    if body is not None:
        if not isinstance(body, bytes):
            raise TypeError("body must be bytes or None", type(body))
        return body

    if json is not None:
        _setdefault_header(headers, "Content-Type", _JSON_CONTENTTYPE)
        import json as jsonlib  # noqa: PLC0415

        return jsonlib.dumps(json).encode("utf-8")

    if form is not None:
        _setdefault_header(headers, "Content-Type", _FORM_CONTENTTYPE)
        return urllib.parse.urlencode(form, doseq=True)

    return None


def _prepare_params(
    params: dict[str, str | bytes] | list[tuple[str, str | bytes]] | None,
) -> str:
    if params is None:
        return ""
    return urllib.parse.urlencode(params, doseq=True)


def _path_with_query_or_params(
    enc_params: str,
    parsed_url: urllib.parse.ParseResult,
) -> str:
    path = parsed_url.path
    if parsed_url.query:
        if enc_params:
            path = f"{path}?{parsed_url.query}&{enc_params}"
        else:
            path = f"{path}?{parsed_url.query}"
    elif enc_params:
        path = f"{path}?{enc_params}"
    return path


def _prepare_request(  # noqa: C901, PLR0913
    url: str,
    *,
    enc_params: str = "",
    timeout: float | None = DEFAULT_TIMEOUT,
    source_address: str | tuple[str, int] | None = None,
    unix_socket: str | None = None,
    verify: bool = True,
    ssl_context: ssl.SSLContext | None = None,
) -> tuple[str, HTTPConnection | UnixHTTPConnection | HTTPSConnection, str]:
    """Parses the URL, returns the path and the right HTTPConnection subclass."""
    parsed_url = urllib.parse.urlparse(url)

    scheme = parsed_url.scheme.lower()
    if scheme.endswith("+unix"):
        scheme = scheme[:-5]
        if unix_socket is None:
            unix_socket = urllib.parse.unquote(parsed_url.netloc)
        if scheme == "https":
            raise ValueError("https+unix is not implemented")

    if scheme not in ("http", "https"):
        raise ValueError("unrecognized scheme", scheme)

    is_https = scheme == "https"
    host = parsed_url.hostname
    if host is None:
        raise ValueError("host is missing from url")
    port = 443 if is_https else 80
    if parsed_url.port:
        port = parsed_url.port

    path = _path_with_query_or_params(enc_params, parsed_url)

    if isinstance(source_address, str):
        source_address = (source_address, 0)

    conn: HTTPConnection | UnixHTTPConnection | HTTPSConnection
    if unix_socket is not None:
        conn = UnixHTTPConnection(unix_socket, timeout=timeout)
    elif is_https:
        if ssl_context is None:
            ssl_context = ssl.create_default_context()
            if not verify:
                ssl_context.check_hostname = False
                ssl_context.verify_mode = ssl.CERT_NONE
        conn = HTTPSConnection(
            host,
            port,
            source_address=source_address,
            timeout=timeout,
            context=ssl_context,
        )
    else:
        conn = HTTPConnection(
            host,
            port,
            source_address=source_address,
            timeout=timeout,
        )

    munged_url = str(
        urllib.parse.urlunparse(
            (
                parsed_url.scheme,
                parsed_url.netloc,
                path,
                parsed_url.params,
                "",
                parsed_url.fragment,
            ),
        ),
    )
    return munged_url, conn, path
