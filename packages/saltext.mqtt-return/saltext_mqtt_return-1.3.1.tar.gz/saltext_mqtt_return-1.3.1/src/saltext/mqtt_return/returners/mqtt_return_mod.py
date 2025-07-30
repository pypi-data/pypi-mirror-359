"""
Salt returner module
"""

import logging
import re
from typing import Any

import salt.returners

from saltext.mqtt_return.utils.awsiot import AWSIoTHandler
from saltext.mqtt_return.utils.mqtt import MQTTHandler
from saltext.mqtt_return.utils.mqtt_queue import PersistentExecutor

log = logging.getLogger(__name__)

__virtualname__ = "mqtt_return"

HANDLER = None

executor = PersistentExecutor(max_workers=4)


def __virtual__():
    return __virtualname__


def _get_options(ret=None):
    defaults = {
        "endpoint": "localhost",
        "port": 1883,
        "output": "mqtt",
        "client_id": "salt-master",
        # Default this into an empty string to prevent none replace
        "topic_rewrite_replace": "",
    }

    attrs = {
        "endpoint": "endpoint",
        "port": "port",
        "output": "output",
        "client_id": "client_id",
        # AWS
        "aws_access_key_id": "aws_access_key_id",
        "aws_secret_access_key": "aws_secret_access_key",
        "aws_region": "aws_region",
        # Topic re-writing
        "topic_prefix": "topic_prefix",
        "topic_rewrite_regex": "topic_rewrite_regex",
        "topic_rewrite_replace": "topic_rewrite_replace",
    }

    _options = salt.returners.get_returner_options(
        f"returner.{__virtualname__}",
        ret,
        attrs,
        __salt__=__salt__,
        __opts__=__opts__,
        defaults=defaults,
    )
    # Ensure port is an int
    if "port" in _options:
        _options["port"] = int(_options["port"])
    return _options


def event_return(events):
    global HANDLER  # pylint: disable=global-statement
    _options = _get_options()

    if HANDLER is None:
        HANDLER = _get_handler(_options)

    for event in events:
        topic = event.get("tag", "")
        data = event.get("data", "")

        # Re-write topic
        if _options.get("topic_rewrite_regex") is not None:
            topic = re.sub(
                str(_options.get("topic_rewrite_regex")),
                str(_options.get("topic_rewrite_replace")),
                topic,
            )

        # Add prefix if specified
        if _options.get("topic_prefix") is not None:
            topic = f"{_options.get('topic_prefix')}/{topic}"

        try:
            executor.submit_job(HANDLER, topic, _sanitize_for_json(data))
        except Exception as error:  # pylint: disable=broad-exception-caught
            log.error(data)
            log.error(error)


def _sanitize_for_json(obj):
    """
    Recursively clean up an object to make it safe for JSON serialization.
    Non-serializable types are converted to strings.
    """
    if isinstance(obj, dict):
        return {_sanitize_for_json(k): _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(_sanitize_for_json(v) for v in obj)
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    return str(obj)


def _get_handler(opts) -> Any:
    if opts.get("output") == "mqtt":
        return MQTTHandler(opts).publish
    if opts.get("output") == "awsiot":
        return AWSIoTHandler(opts).publish

    raise RuntimeError(f"Unsupported handler: {opts.get('output')}")
