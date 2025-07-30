import json

import boto3


class AWSIoTHandler:
    def __init__(self, opts):
        self.client = boto3.client(
            "iot-data",
            region_name=opts.get("aws_region"),
            endpoint_url=opts.get("endpoint"),
        )

    def publish(self, topic, data, qos=1):
        self.client.publish(
            topic=f"{topic}",
            qos=qos,
            # retain=False, #depends on boto version
            payload=json.dumps(data),
        )
