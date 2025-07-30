import paho.mqtt.publish as mqtt_pub
import salt.utils.json


class MQTTHandler:
    def __init__(self, opts):
        self.opts = opts

    def publish(self, topic, data, qos=1):
        mqtt_pub.single(
            f"{topic}",
            payload=bytes(salt.utils.json.dumps(data), "utf-8"),
            qos=qos,
            hostname=self.opts.get("endpoint", ""),
            port=self.opts.get("port", ""),
            client_id=self.opts.get("client_id"),
        )
