#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from uuid import uuid4

import pika.exceptions
from cloudevents.events import (
    Event,
    EventOutcome,
    EventAttributes,
)
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.services.pulsar import PulsarClient, PRODUCER_TOPIC
from app.services import rabbit
from app.helpers.bag import create_sip_bag
from app.helpers.events import WatchfolderMessage, InvalidMessageException


APP_NAME = "sipin-sip-creator"


class EventListener:
    def __init__(self):
        configParser = ConfigParser()
        self.log = logging.get_logger(__name__, config=configParser)
        self.config = configParser.app_cfg
        # Init RabbitMQ client
        try:
            self.rabbitClient = rabbit.RabbitClient()
        except pika.exceptions.AMQPConnectionError as error:
            self.log.error("Connection to RabbitMQ failed.")
            raise error
        # Init Pusar client
        self.pulsar_client = PulsarClient()

    def handle_message(self, channel, method, properties, body):
        """Main method that will handle the incoming messages.

        - Parse the message.
        - Create the SIP.
        - Make a bag of the SIP.
        - Send a cloudevent to a Pulsar topic.
        """
        try:
            self.log.debug(f"Incoming event: {body}")
            message = WatchfolderMessage(body)
            bag_path: Path = create_sip_bag(message)

            # Send Pulsar event
            attributes = EventAttributes(
                type=PRODUCER_TOPIC,
                source=APP_NAME,
                subject=message.get_essence_path().stem,
                outcome=EventOutcome.SUCCESS,
                correlation_id=str(uuid4()),
            )

            data = {
                "host": self.config["host"],
                "path": str(bag_path),
                "outcome": EventOutcome.SUCCESS,
                "message": f"SIP created: '{bag_path}'",
            }

            outgoing_event = Event(attributes, data)

            self.pulsar_client.produce_event(outgoing_event)
            self.log.info("SIP created event sent.")
        except InvalidMessageException as e:
            self.log.error(e)
            channel.basic_nack(method.delivery_tag, requeue=False)
            return
        channel.basic_ack(method.delivery_tag)

    def start(self):
        # Start listening for incoming messages
        self.log.info("Start to listen for messages...")
        self.rabbitClient.listen(self.handle_message)
        self.pulsar_client.close()
