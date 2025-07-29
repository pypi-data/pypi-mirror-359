"""Plugin to publish to a topic on an MQTT broker."""

from expliot.core.protocols.internet.mqtt import (
    DEFAULT_MQTT_PORT,
    MQTT_ERR_SUCCESS,
    MqttClient,
)
from expliot.core.tests.test import TCategory, Test, TLog, TTarget
from expliot.plugins.mqtt import MQTT_REFERENCE


class MqttPub(Test):
    """Publish a MQTT message to a given MQTT broker.

    Output Format:
    There is no output.
    """

    def __init__(self):
        """Initialize the test."""

        super().__init__(
            name="pub",
            summary="MQTT Publisher",
            descr="This test case publishes a message on a topic to a"
            "specified MQTT broker on a specified port.",
            author="Aseem Jakhar",
            email="aseemjakhar@gmail.com",
            ref=[MQTT_REFERENCE],
            category=TCategory(TCategory.MQTT, TCategory.SW, TCategory.RECON),
            target=TTarget(TTarget.GENERIC, TTarget.GENERIC, TTarget.GENERIC),
        )

        self.argparser.add_argument(
            "-r",
            "--rhost",
            required=True,
            help="Hostname/IP address of the target MQTT broker",
        )
        self.argparser.add_argument(
            "-p",
            "--rport",
            default=DEFAULT_MQTT_PORT,
            type=int,
            help="Port number of the target MQTT broker. Default is 1883",
        )
        self.argparser.add_argument(
            "-t",
            "--topic",
            required=True,
            help="Topic name on which message has to be published",
        )
        self.argparser.add_argument(
            "-m",
            "--msg",
            required=True,
            help="Message to be published on the specified topic",
        )
        self.argparser.add_argument(
            "-i",
            "--id",
            help="The client ID to be used for the connection. Default is "
            "random client ID",
        )
        self.argparser.add_argument(
            "-u",
            "--user",
            help="Specify the user name to be used. If not specified, it "
            "connects without authentication",
        )
        self.argparser.add_argument(
            "-w",
            "--passwd",
            help="Specify the password to be used. If not specified, it "
            "connects with without authentication",
        )

    def execute(self):
        """Execute the plugin."""
        TLog.generic(
            f"Publishing message on topic ({self.args.topic}) to MQTT Broker ({self.args.rhost}) on port ({self.args.rport})"
        )
        try:
            client = MqttClient(client_id=self.args.id)
            client.easy_config(
                user=self.args.user,
                passwd=self.args.passwd,
                on_connect=client.on_connectcb,
                on_publish=client.on_publishcb,
            )
            client.connect(self.args.rhost, self.args.rport)
            client.publish(self.args.topic, self.args.msg, 1)
            client.loop_forever()
            if client.connect_rc != MQTT_ERR_SUCCESS:
                self.result.setstatus(
                    passed=False, reason=client.rcstr(client.connect_rc)
                )
                TLog.fail(
                    f"MQTT Connection Failed. Return code ({client.connect_rc}:{client.rcstr(client.connect_rc)})"
                )
            else:
                TLog.success("Message published")
        except:
            self.result.exception()
