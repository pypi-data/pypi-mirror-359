"""Wrapper for the CoAP communication."""

import asyncio
import logging

# pylint: disable=no-name-in-module
# pylint not able to fine GET, POST, PUT, DELETE. However
# in aiocop __init__ they are imported as from .numbers import *
from aiocoap import DELETE, GET, POST, PUT, Context, Message

from expliot.core.common import bstr
from expliot.core.discovery import Discovery

COAP_STR = "coap"
COAP_PORT = 5683
ROOTPATH = "/"
WKRPATH = "/.well-known/core"

# Disable aiocoap logging
logging.getLogger("coap").setLevel(logging.CRITICAL + 1)


class WKResource:
    """A resource on the CoAP server as advertised.

    Reading "/.well-known/core" which is in the CoRE Link Format (RFC 6690).
    For more details on CoRE Link format, https://tools.ietf.org/html/rfc6690
    """

    def __init__(self, link):
        """Create a Resource object from the link provided.

        An example of the link format:
        '</resurce/path>;title="Foo Bar";if="Foo";rt="bar";sz=100'

        Args:
            link (bytes or str): The link format containing a single resource
            from the response.

        Returns:
            Nothing

        """
        self._attributes = {}
        self.unknown = []
        self.parse(link)

    def parse(self, link):
        """Parse the link provided and extracts the attributes from it.

        An example of the link format:
        '</resurce/path>;title="Foo Bar";if="Foo";rt="bar";sz=100'
        More details about the syntax can be found here -
        https://tools.ietf.org/html/rfc6690#page-6

        Args:
            link (bytes or str): The link format containing a single link
            resource from the response.

        Returns:
            Nothing

        """
        if not link:
            raise ValueError("Empty CoRE link!")

        if link.__class__ == bytes:
            link = bstr(link)
        for item in link.split(";"):
            attr = item.split("=")
            if len(attr) == 1:
                if attr[0][0] == "<" and attr[0][-1] == ">":
                    self._attributes["path"] = attr[0][1:-1]
                else:
                    self.unknown.append(attr[0])
            elif len(attr) == 2:
                self._attributes[attr[0]] = attr[1].strip('"')
            else:
                self.unknown.append(item)

    def attributes(self):
        """Return a dict containing all attributes of a sinle link.

        The resource path is stored in "path" key for ease.

        Returns:
            dict: The dict containing all the attributes found in
                  the parsed link.

        """
        return self._attributes

    def path(self):
        """Return the path of the well-known resource."""
        return self._attributes["path"]


class CoapClient:
    """A CoAP Client Object."""

    def __init__(self, host, port=COAP_PORT, secure=False):
        """Initialize the CoapClient.

        Args:
            host (str): The hostname or IP of the CoAP server
            port (int): The CoAP port number on the host
            secure (bool): plain text (coap) or secure (coaps) request
        Returns:
            Nothing

        """
        if not host:
            raise ValueError("Empty host!")
        self.host = host
        self.port = port

    @staticmethod
    def response_dict(response):
        """Create and return a dict containing response code.

        Based on the string and the payload from the Response Object.

        Args:
            response (aiocoap.message.Message): Response message
                received from the CoAP server.

        Returns:
            dict: Dict object containing response code, string
        and payload

        """
        return {
            "code": int(response.code),
            "code_string": str(response.code),
            "payload": str(response.payload),
        }

    def makeuri(self, path=None, secure=False):
        """Make a CoAP URI from the details provided.

        Args:
            path: The resource path of the request
            secure (bool): Plain text (coap) or secure (coaps) request
        Returns:
            str: The URI created using the parameters

        """
        scheme = COAP_STR
        if secure:
            scheme += "s"
        if not path:
            raise ValueError("Empty Resource Path!")
        if path[0] != "/":
            path = "/" + path
        return f"{scheme}://{self.host}:{self.port}{path}"

    def request(self, method=GET, path=None, payload=b"", secure=True):
        """Make a sync request.

        Args:
            method (aiocoap.numbers.codes.Code): The request method, e. g. GET
            path (str): The resource path of the request
            payload (bytes): The payload to send if any
            secure (bool): plain text (coap) or secure (coaps) request

        Returns:
            Check async_request()

        """
        loop = asyncio.new_event_loop()
        response = loop.run_until_complete(
            self.async_request(method=method, path=path, payload=payload, secure=secure)
        )
        loop.close()
        return response

    async def async_request(self, method=GET, path=None, payload=b"", secure=False):
        """Send a request to a CoAP server.

        Args:
            method (aiocoap.numbers.codes.Code): The request method, e. g. GET
            path (str): The resource path of the request
            payload (bytes): The payload to send if any
            secure (bool): plain text (coap) or secure (coaps) request

        Returns:
            aiocoap.message.Message: Response message

        """
        uri = self.makeuri(path=path, secure=secure)
        # print(f"URI = ({uri})")
        ctx = await Context.create_client_context()
        request = Message(code=method, uri=uri, payload=payload)
        response = await ctx.request(request).response
        await ctx.shutdown()
        return response

    def get(self, path=None, secure=False):
        """Make a GET request.

        Args:
            path (str): The resource path of the request
            secure (bool): plain text (coap) or secure (coaps) request

        Returns:
            Check async_request()

        """
        return self.request(method=GET, path=path, secure=secure)

    def post(self, path=None, payload=b"", secure=False):
        """Make a POST request.

        Args:
            path (str): The resource path of the request
            payload (bytes): The payload to send if any
            secure (bool): plain text (coap) or secure (coaps) request

        Returns:
            Check async_request()

        """
        return self.request(method=POST, path=path, payload=payload, secure=secure)

    def put(self, path=None, payload=b"", secure=False):
        """Make a PUT request.

        Args:
            path (str): The resource path of the request
            payload (bytes): The payload to send if any
            secure (bool): plain text (coap) or secure (coaps) request

        Returns:
            Check async_request()

        """
        return self.request(method=PUT, path=path, payload=payload, secure=secure)

    def delete(self, path=None, secure=False):
        """Make a DELETE request.

        Args:
            path (str): The resource path of the request
            secure (bool): plain text (coap) or secure (coaps) request

        Returns:
            Check async_request()

        """
        return self.request(method=DELETE, path=path, secure=secure)


class CoapDiscovery(Discovery):
    """Discover the resources on a CoAP server."""

    # pylint: disable=super-init-not-called
    def __init__(self, host, port=COAP_PORT):
        """Initialize the CoAP discovery.

        Args:
            host (str): The hostname or IP of the CoAP server
            port (int): The CoAP port number on the host
        Returns:
            Nothing

        """
        if not host:
            raise ValueError("Empty host!")
        self.host = host
        self.port = port
        self.resources = []

    def scan(self):
        """Scan for resources advertised by the CoAP server.

        Args:
            Nothing
        Returns:
            Nothing

        """
        client = CoapClient(self.host, self.port)
        response = client.get(path=WKRPATH)
        if not response.code.is_successful():
            raise ConnectionError(
                f"Response Error. {CoapClient.response_dict(response)}"
            )
        for link in response.payload.split(b","):
            self.resources.append(WKResource(link).attributes())

    def services(self):
        """Return the found resources on the CoAP server.

        Args:
            Nothing
        Returns:
            list: List of resources found

        """
        return self.resources
