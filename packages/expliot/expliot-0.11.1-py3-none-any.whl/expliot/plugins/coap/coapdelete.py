"""Test for deleting data from a CoAP device."""

from expliot.core.protocols.internet.coap import (
    COAP_PORT,
    ROOTPATH,
    CoapClient,
)
from expliot.core.tests.test import (
    TCategory,
    Test,
    TLog,
    TTarget,
)


class CoapDelete(Test):
    """Test for Sending DELETE request to a CoAP device.

    Output Format:
    [
        {
            "response_code": 69  # Ex. 69=0b01000101 (0b010=2, 0b00101=5)
            "response_code_str": "2.05 Content",
            "response_payload": "Foo bar" # or "" if no payload in response
        }
    ]
    """

    def __init__(self):
        """Initialize the test."""
        super().__init__(
            name="delete",
            summary="CoAP DELETE request",
            descr="This test allows you to send a CoAP DELETE request (Message) "
            "to a CoAP server on a specified resource path.",
            author="Aseem Jakhar",
            email="aseem@expliot.io",
            ref=["https://tools.ietf.org/html/rfc7252"],
            category=TCategory(TCategory.COAP, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="Hostname/IP address of the target CoAP Server",
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=COAP_PORT,
            type=int,
            help=f"Port number of the target CoAP Server. Default " f"is {COAP_PORT}",
        )
        self.argparser.add_argument(
            "-u",
            "--path",
            default=ROOTPATH,
            help=f"Resource URI path of the DELETE request. Default "
            f"is URI path {ROOTPATH}",
        )

    def execute(self):
        """Execute the test."""
        TLog.generic(
            f"Sending DELETE request for URI Path ({self.args.path}) "
            f"to CoAP Server {self.args.rhost} on port {self.args.rport}"
        )
        try:
            client = CoapClient(self.args.rhost, port=self.args.rport)
            response = client.delete(path=self.args.path)
            if not response.code.is_successful():
                self.result.setstatus(
                    passed=False,
                    reason=f"Error Response: {CoapClient.response_dict(response)}",
                )
                return
            self.output_handler(
                response_code=int(response.code),
                response_code_str=str(response.code),
                response_payload=response.payload,
            )
        except:
            self.result.exception()
