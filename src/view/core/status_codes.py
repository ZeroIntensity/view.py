from __future__ import annotations

import traceback
from enum import IntEnum
from typing import ClassVar
import sys

from view.core.response import TextResponse

__all__ = "HTTPError", "Success", "status_exception"

STATUS_EXCEPTIONS: dict[int, type[HTTPError]] = {}
STATUS_STRINGS: dict[int, str] = {
    100: "Continue",
    101: "Switching protocols",
    102: "Processing",
    103: "Early Hints",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "Switch Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Payload Too Large",
    414: "URI Too Long",
    415: "Unsupported Media Type",
    416: "Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a Teapot",
    421: "Misdirected Request",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    425: "Too Early",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    510: "Not Extended",
    511: "Network Authentication Required",
}


class Success(IntEnum):
    OK = 200
    """
    The request succeeded. The result and meaning of "success" depends on
    the HTTP method:

    GET: The resource has been fetched and transmitted in the message body.
    HEAD: Representation headers are included in the response without any
          message body.
    PUT or POST: The resource describing the result of the action is
                 transmitted in the message body.
    TRACE: The message body contains the request as received by the server.
    """

    CREATED = 201
    """
    The request succeeded, and a new resource was created as a result. This is
    typically the response sent after POST requests, or some PUT requests.
    """

    ACCEPTED = 202
    """
    The request has been received but not yet acted upon. It is noncommittal,
    since there is no way in HTTP to later send an asynchronous response
    indicating the outcome of the request. It is intended for cases where
    another process or server handles the request, or for batch processing.
    """

    NONAUTHORITATIVE_INFORMATION = 203
    """
    This response code means the returned metadata is not exactly the same as
    is available from the origin server, but is collected from a local or a
    third-party copy. This is mostly used for mirrors or backups of another
    resource. Except for that specific case, the 200 OK response is preferred
    to this status.
    """

    NO_CONTENT = 204
    """
    There is no content to send for this request, but the headers are useful.
    The user agent may update its cached headers for this resource with the
    new ones.
    """

    RESET_CONTENT = 205
    """
    Tells the user agent to reset the document which sent this request.
    """

    PARTIAL_CONTENT = 206
    """
    This response code is used in response to a range request when the client
    has requested a part or parts of a resource.
    """

    MULTISTATUS = 207
    """
    Conveys information about multiple resources, for situations where
    multiple status codes might be appropriate.
    """

    ALREADY_REPORTED = 208
    """
    Used inside a <dav:propstat> response element to avoid repeatedly
    enumerating the internal members of multiple bindings to the same
    collection.
    """

    IM_USED = 226
    """
    The server has fulfilled a GET request for the resource, and the response
    is a representation of the result of one or more instance-manipulations
    applied to the current instance.
    """


HTTP_ERROR_TRACEBACK_NOTE = """
-----

If you're seeing this message, then something has gone horribly wrong.
HTTP errors should never be in a real traceback, and instead only
be used for indicating something to a caller. If you meant to
access the message included with this HTTP error, use the
.message attribute.

-----
"""


class HTTPError(Exception):
    """
    Base class for all HTTP errors.

    Raising this type, or a subclass of this type, will be converted
    to a status code at runtime.
    """

    status_code: ClassVar[int] = 0
    description: ClassVar[str] = ""

    def __init__(self, *msg: object) -> None:
        if msg:
            self.message: str | None = " ".join([str(item) for item in msg])
        else:
            self.message = None

        if sys.version_info < (3, 11):
            super().__init__(*msg, HTTP_ERROR_TRACEBACK_NOTE)
        else:
            super().__init__(*msg)
            super().add_note(HTTP_ERROR_TRACEBACK_NOTE)

    def __init_subclass__(cls, ignore: bool = False) -> None:
        if not ignore:
            assert cls.status_code != 0, cls
            STATUS_EXCEPTIONS[cls.status_code] = cls
            cls.description = STATUS_STRINGS[cls.status_code]

        global __all__
        __all__ += (cls.__name__,)

    def as_response(self) -> TextResponse[str]:
        cls = type(self)
        if cls.status_code == 0:
            raise TypeError(f"{cls} is not a real response")

        if self.message is None:
            message = f"{cls.status_code} {cls.description}"
        else:
            message = self.message

        return TextResponse.from_content(message, status_code=cls.status_code)


def status_exception(status: int) -> type[HTTPError]:
    """
    Get an exception for the given status.
    """
    try:
        status_type: type[HTTPError] = STATUS_EXCEPTIONS[status]
    except KeyError as error:
        raise ValueError(f"{status} is not a valid HTTP error status code") from error

    return status_type


class ClientSideError(HTTPError, ignore=True):
    """
    Base class for all HTTP errors between 400 and 500.
    """


class ServerSideError(HTTPError, ignore=True):
    """
    Base class for all HTTP errors between 500 and 600.
    """


class BadRequest(ClientSideError):
    """
    The server cannot or will not process the request due to something
    that is perceived to be a client error (e.g., malformed request syntax,
    invalid request message framing, or deceptive request routing).
    """

    status_code = 400


class Unauthorized(ClientSideError):
    """
    Although the HTTP standard specifies "unauthorized", semantically this
    response means "unauthenticated". That is, the client must authenticate
    itself to get the requested response.
    """

    status_code = 401


class PaymentRequired(ClientSideError):
    """
    The initial purpose of this code was for digital payment systems,
    however this status code is rarely used and no standard convention exists.
    """

    status_code = 402


class Forbidden(ClientSideError):
    """
    The client does not have access rights to the content; that is, it is
    unauthorized, so the server is refusing to give the requested resource.
    Unlike 401 Unauthorized, the client's identity is known to the server.
    """

    status_code = 403


class NotFound(ClientSideError):
    """
    The server cannot find the requested resource. In the browser, this means
    the URL is not recognized. In an API, this can also mean that the endpoint
    is valid but the resource itself does not exist. Servers may also send this
    response instead of 403 Forbidden to hide the existence of a resource from
    an unauthorized client. This response code is probably the most well known
    due to its frequent occurrence on the web.
    """

    status_code = 404


class MethodNotAllowed(ClientSideError):
    """
    The request method is known by the server but is not supported by the
    target resource. For example, an API may not allow DELETE on a resource,
    or the TRACE method entirely.
    """

    status_code = 405


class NotAcceptable(ClientSideError):
    """
    This response is sent when the web server, after performing server-driven
    content negotiation, doesn't find any content that conforms to the
    criteria given by the user agent.
    """

    status_code = 406


class ProxyAuthenticationRequired(ClientSideError):
    """
    This is similar to 401 Unauthorized but authentication is needed to be
    done by a proxy.
    """

    status_code = 407


class RequestTimeout(ClientSideError):
    """
    This response is sent on an idle connection by some servers, even without
    any previous request by the client. It means that the server would like to
    shut down this unused connection. This response is used much more since
    some browsers use HTTP pre-connection mechanisms to speed up browsing.
    Some servers may shut down a connection without sending this message.
    """

    status_code = 408


class Conflict(ClientSideError):
    """
    This response is sent when a request conflicts with the current state of
    the server. In WebDAV remote web authoring, 409 responses are errors sent
    to the client so that a user might be able to resolve a conflict and
    resubmit the request.
    """

    status_code = 409


class Gone(ClientSideError):
    """
    This response is sent when the requested content has been permanently
    deleted from server, with no forwarding address. Clients are expected to
    remove their caches and links to the resource. The HTTP specification
    intends this status code to be used for "limited-time, promotional
    services". APIs should not feel compelled to indicate resources that have
    been deleted with this status code.
    """

    status_code = 410


class LengthRequired(ClientSideError):
    """
    Server rejected the request because the Content-Length header field is not
    defined and the server requires it.
    """

    status_code = 411


class PreconditionFailed(ClientSideError):
    """
    In conditional requests, the client has indicated preconditions in its
    headers which the server does not meet.
    """

    status_code = 412


class ContentTooLarge(ClientSideError):
    """
    The request body is larger than limits defined by server. The server might
    close the connection or return an Retry-After header field.
    """

    status_code = 413


class URITooLong(ClientSideError):
    """
    The URI requested by the client is longer than the server is willing to
    interpret.
    """

    status_code = 414


class UnsupportedMediaType(ClientSideError):
    """
    The media format of the requested data is not supported by the server,
    so the server is rejecting the request.
    """

    status_code = 415


class RangeNotSatisfiable(ClientSideError):
    """
    The ranges specified by the Range header field in the request cannot be
    fulfilled. It's possible that the range is outside the size of the target
    resource's data.
    """

    status_code = 416


class ExpectationFailed(ClientSideError):
    """
    This response code means the expectation indicated by the Expect request
    header field cannot be met by the server.
    """

    status_code = 417


class IAmATeapot(ClientSideError):
    """
    The server refuses the attempt to brew coffee with a teapot.
    """

    status_code = 418


class MisdirectedRequest(ClientSideError):
    """
    The request was directed at a server that is not able to produce a
    response. This can be sent by a server that is not configured to produce
    responses for the combination of scheme and authority that are included
    in the request URI.
    """

    status_code = 421


class UnprocessableContent(ClientSideError):
    """
    The request was well-formed but was unable to be followed due to semantic errors.
    """

    status_code = 422


class Locked(ClientSideError):
    """
    The resource that is being accessed is locked.
    """

    status_code = 423


class FailedDependency(ClientSideError):
    """
    The request failed due to failure of a previous request.
    """

    status_code = 424


class TooEarly(ClientSideError):
    """
    Indicates that the server is unwilling to risk processing a request
    that might be replayed.
    """

    status_code = 425


class UpgradeRequired(ClientSideError):
    """
    The server refuses to perform the request using the current protocol but
    might be willing to do so after the client upgrades to a different
    protocol. The server sends an Upgrade header in a 426 response to indicate
    the required protocol(s).
    """

    status_code = 426


class PreconditionRequired(ClientSideError):
    """
    The origin server requires the request to be conditional. This response is
    intended to prevent the 'lost update' problem, where a client GETs a
    resource's state, modifies it and PUTs it back to the server, when
    meanwhile a third party has modified the state on the server, leading to
    a conflict.
    """

    status_code = 428


class TooManyRequests(ClientSideError):
    """
    The user has sent too many requests in a given amount of
    time (rate limiting).
    """

    status_code = 429


class RequestHeaderFieldsTooLarge(ClientSideError):
    """
    The server is unwilling to process the request because its header fields
    are too large. The request may be resubmitted after reducing the size of
    the request header fields.
    """

    status_code = 431


class UnavailableForLegalReasons(ClientSideError):
    """
    The user agent requested a resource that cannot legally be provided,
    such as a web page censored by a government.
    """

    status_code = 451


class InternalServerError(ServerSideError):
    """
    The server has encountered a situation it does not know how to handle.
    This error is generic, indicating that the server cannot find a more
    appropriate 5XX status code to respond with.
    """

    status_code = 500

    @classmethod
    def from_current_exception(cls) -> InternalServerError:
        message = traceback.format_exc()
        return cls(message)


class NotImplemented(ServerSideError):
    """
    The request method is not supported by the server and cannot be handled.
    The only methods that servers are required to support (and therefore that
    must not return this code) are GET and HEAD.
    """

    status_code = 501


class BadGateway(ServerSideError):
    """
    This error response means that the server, while working as a gateway to
    get a response needed to handle the request, got an invalid response.
    """

    status_code = 502


class ServiceUnavailable(ServerSideError):
    """
    The server is not ready to handle the request. Common causes are a server
    that is down for maintenance or that is overloaded. Note that together
    with this response, a user-friendly page explaining the problem should be
    sent. This response should be used for temporary conditions and the
    Retry-After HTTP header should, if possible, contain the estimated time
    before the recovery of the service. The webmaster must also take care
    about the caching-related headers that are sent along with this response,
    as these temporary condition responses should usually not be cached.
    """

    status_code = 503


class GatewayTimeout(ServerSideError):
    """
    This error response is given when the server is acting as a gateway and
    cannot get a response in time.
    """

    status_code = 504


class HTTPVersionNotSupported(ServerSideError):
    """
    The HTTP version used in the request is not supported by the server.
    """

    status_code = 505


class VariantAlsoNegotiates(ServerSideError):
    """
    The server has an internal configuration error: during content
    negotiation, the chosen variant is configured to engage in content
    negotiation itself, which results in circular references when creating
    responses.
    """

    status_code = 506


class InsufficientStorage(ServerSideError):
    """
    The method could not be performed on the resource because the server is
    unable to store the representation needed to successfully complete the
    request.
    """

    status_code = 507


class LoopDetected(ServerSideError):
    """
    The server detected an infinite loop while processing the request.
    """

    status_code = 508


class NotExtended(ServerSideError):
    """
    The client request declares an HTTP Extension (RFC 2774) that should be
    used to process the request, but the extension is not supported.
    """

    status_code = 510


class NetworkAuthenticationRequired(ServerSideError):
    """
    Indicates that the client needs to authenticate to gain network access.
    """

    status_code = 511
