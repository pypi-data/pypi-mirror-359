"""TLS/SSL fetcher."""

import socket
import ssl
from datetime import datetime

from cryptography import x509
from cryptography.hazmat.backends import default_backend


class TLSDetailsFetcher:
    """Representation of a TLS/SSL fetcher."""

    def __init__(self, host, port):
        """Initialize the TLS/SSL fetcher."""
        self.host = host
        self.port = port
        self.context = ssl.create_default_context()

    def get_tls_details(self):
        """Collect the TLS/SSL details."""
        with socket.create_connection(
            (self.host, self.port)
        ) as sock, self.context.wrap_socket(sock, server_hostname=self.host) as ssock:
            cert = ssock.getpeercert(binary_form=True)
            ssl_version = ssock.version()

        cert_obj = x509.load_der_x509_certificate(cert, default_backend())

        details = {
            "TLS Version": ssl_version,
            "Subject": cert_obj.subject,
            "Issuer": cert_obj.issuer,
            "Valid from": cert_obj.not_valid_before_utc.strftime(
                "%Y-%m-%d %H:%M:%S %Z"
            ),
            "Valid to": cert_obj.not_valid_after_utc.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "Serial number": cert_obj.serial_number,
        }

        return details
