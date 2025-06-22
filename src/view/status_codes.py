from __future__ import annotations
from typing import ClassVar

STATUS_EXCEPTIONS: dict[int, type[HTTPError]] = {}


class HTTPError(Exception):
    status_code: ClassVar[int]

    def __init_subclass__(cls) -> None:
        STATUS_EXCEPTIONS[cls.status_code] = cls


def status_exception(status: int) -> type[HTTPError]:
    """
    Get an exception for the given status.
    """
    try:
        status_type: type[HTTPError] = STATUS_EXCEPTIONS[status]
    except KeyError as error:
        raise ValueError(f"{status} is not a valid HTTP error status code") from error

    return status_type


class ClientSideError(HTTPError):
    pass


class ServerSideError(HTTPError):
    pass


class BadRequest(ClientSideError):
    """The server cannot or will not process the request due to something that is perceived to be a client error (e.g., malformed request syntax, invalid request message framing, or deceptive request routing)."""

    status_code = 400


class Unauthorized(ClientSideError):
    """Although the HTTP standard specifies "unauthorized", semantically this response means "unauthenticated". That is, the client must authenticate itself to get the requested response."""

    status_code = 401


class PaymentRequired(ClientSideError):
    """The initial purpose of this code was for digital payment systems, however this status code is rarely used and no standard convention exists."""

    status_code = 402


class Forbidden(ClientSideError):
    """The client does not have access rights to the content; that is, it is unauthorized, so the server is refusing to give the requested resource. Unlike 401 Unauthorized, the client's identity is known to the server."""

    status_code = 403


class NotFound(ClientSideError):
    """The server cannot find the requested resource. In the browser, this means the URL is not recognized. In an API, this can also mean that the endpoint is valid but the resource itself does not exist. Servers may also send this response instead of 403 Forbidden to hide the existence of a resource from an unauthorized client. This response code is probably the most well known due to its frequent occurrence on the web."""

    status_code = 404


class MethodNotAllowed(ClientSideError):
    """The request method is known by the server but is not supported by the target resource. For example, an API may not allow DELETE on a resource, or the TRACE method entirely."""

    status_code = 405


class NotAcceptable(ClientSideError):
    """This response is sent when the web server, after performing server-driven content negotiation, doesn't find any content that conforms to the criteria given by the user agent."""

    status_code = 406


class ProxyAuthenticationRequired(ClientSideError):
    """This is similar to 401 Unauthorized but authentication is needed to be done by a proxy."""

    status_code = 407


class RequestTimeout(ClientSideError):
    """This response is sent on an idle connection by some servers, even without any previous request by the client. It means that the server would like to shut down this unused connection. This response is used much more since some browsers use HTTP pre-connection mechanisms to speed up browsing. Some servers may shut down a connection without sending this message."""

    status_code = 408


class Conflict(ClientSideError):
    """This response is sent when a request conflicts with the current state of the server. In WebDAV remote web authoring, 409 responses are errors sent to the client so that a user might be able to resolve a conflict and resubmit the request."""

    status_code = 409


class Gone(ClientSideError):
    """This response is sent when the requested content has been permanently deleted from server, with no forwarding address. Clients are expected to remove their caches and links to the resource. The HTTP specification intends this status code to be used for "limited-time, promotional services". APIs should not feel compelled to indicate resources that have been deleted with this status code."""

    status_code = 410


class LengthRequired(ClientSideError):
    """Server rejected the request because the Content-Length header field is not defined and the server requires it."""

    status_code = 411


class PreconditionFailed(ClientSideError):
    """In conditional requests, the client has indicated preconditions in its headers which the server does not meet."""

    status_code = 412


class ContentTooLarge(ClientSideError):
    """The request body is larger than limits defined by server. The server might close the connection or return an Retry-After header field."""

    status_code = 413


class URITooLong(ClientSideError):
    """The URI requested by the client is longer than the server is willing to interpret."""

    status_code = 414


class UnsupportedMediaType(ClientSideError):
    """The media format of the requested data is not supported by the server, so the server is rejecting the request."""

    status_code = 415


class RangeNotSatisfiable(ClientSideError):
    """The ranges specified by the Range header field in the request cannot be fulfilled. It's possible that the range is outside the size of the target resource's data."""

    status_code = 416


class ExpectationFailed(ClientSideError):
    """This response code means the expectation indicated by the Expect request header field cannot be met by the server."""

    status_code = 417


class IAmATeapot(ClientSideError):
    """The server refuses the attempt to brew coffee with a teapot."""

    status_code = 418


class MisdirectedRequest(ClientSideError):
    """The request was directed at a server that is not able to produce a response. This can be sent by a server that is not configured to produce responses for the combination of scheme and authority that are included in the request URI."""

    status_code = 421


class UnprocessableContent(ClientSideError):
    """The request was well-formed but was unable to be followed due to semantic errors."""

    status_code = 422


class Locked(ClientSideError):
    """The resource that is being accessed is locked."""

    status_code = 423


class FailedDependency(ClientSideError):
    """The request failed due to failure of a previous request."""

    status_code = 424


class TooEarlyExperimental(ClientSideError):
    """Indicates that the server is unwilling to risk processing a request that might be replayed."""

    status_code = 425


class UpgradeRequired(ClientSideError):
    """The server refuses to perform the request using the current protocol but might be willing to do so after the client upgrades to a different protocol. The server sends an Upgrade header in a 426 response to indicate the required protocol(s)."""

    status_code = 426


class PreconditionRequired(ClientSideError):
    """The origin server requires the request to be conditional. This response is intended to prevent the 'lost update' problem, where a client GETs a resource's state, modifies it and PUTs it back to the server, when meanwhile a third party has modified the state on the server, leading to a conflict."""

    status_code = 428


class TooManyRequests(ClientSideError):
    """The user has sent too many requests in a given amount of time (rate limiting)."""

    status_code = 429


class RequestHeaderFieldsTooLarge(ClientSideError):
    """The server is unwilling to process the request because its header fields are too large. The request may be resubmitted after reducing the size of the request header fields."""

    status_code = 431


class UnavailableForLegalReasons(ClientSideError):
    """The user agent requested a resource that cannot legally be provided, such as a web page censored by a government."""

    status_code = 451


class InternalServerError(ServerSideError):
    """The server has encountered a situation it does not know how to handle. This error is generic, indicating that the server cannot find a more appropriate 5XX status code to respond with."""

    status_code = 500


class NotImplemented(ServerSideError):
    """The request method is not supported by the server and cannot be handled. The only methods that servers are required to support (and therefore that must not return this code) are GET and HEAD."""

    status_code = 501


class BadGateway(ServerSideError):
    """This error response means that the server, while working as a gateway to get a response needed to handle the request, got an invalid response."""

    status_code = 502


class ServiceUnavailable(ServerSideError):
    """The server is not ready to handle the request. Common causes are a server that is down for maintenance or that is overloaded. Note that together with this response, a user-friendly page explaining the problem should be sent. This response should be used for temporary conditions and the Retry-After HTTP header should, if possible, contain the estimated time before the recovery of the service. The webmaster must also take care about the caching-related headers that are sent along with this response, as these temporary condition responses should usually not be cached."""

    status_code = 503


class GatewayTimeout(ServerSideError):
    """This error response is given when the server is acting as a gateway and cannot get a response in time."""

    status_code = 504


class HTTPVersionNotSupported(ServerSideError):
    """The HTTP version used in the request is not supported by the server."""

    status_code = 505


class VariantAlsoNegotiates(ServerSideError):
    """The server has an internal configuration error: during content negotiation, the chosen variant is configured to engage in content negotiation itself, which results in circular references when creating responses."""

    status_code = 506


class InsufficientStorage(ServerSideError):
    """The method could not be performed on the resource because the server is unable to store the representation needed to successfully complete the request."""

    status_code = 507


class LoopDetected(ServerSideError):
    """The server detected an infinite loop while processing the request."""

    status_code = 508


class NotExtended(ServerSideError):
    """The client request declares an HTTP Extension (RFC 2774) that should be used to process the request, but the extension is not supported."""

    status_code = 510


class NetworkAuthenticationRequired(ServerSideError):
    """Indicates that the client needs to authenticate to gain network access."""

    status_code = 511
