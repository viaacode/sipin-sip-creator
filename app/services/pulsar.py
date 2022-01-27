#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pulsar

from viaa.configuration import ConfigParser
from cloudevents.events import Event, CEMessageMode, PulsarBinding

PRODUCER_TOPIC = "be.meemoo.sipin.sip.create"


class PulsarClient:
    def __init__(self):
        config_parser = ConfigParser()
        self.pulsar_config = config_parser.app_cfg["pulsar"]
        self.client = pulsar.Client(
            f'pulsar://{self.pulsar_config["host"]}:{self.pulsar_config["port"]}'
        )
        self.producer = self.client.create_producer(PRODUCER_TOPIC)

    def produce_event(self, event: Event):
        """Produce a cloudevent on a topic
        Args:
            event: The cloudevent to send to the topic.
        """

        msg = PulsarBinding.to_protocol(event, CEMessageMode.STRUCTURED)
        self.producer.send(
            msg.data,
            properties=msg.attributes,
            event_timestamp=event.get_event_time_as_int(),
        )

    def close(self):
        """Close the open producers"""
        self.producer.close()
