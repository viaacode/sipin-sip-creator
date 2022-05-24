#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

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
from app.helpers.sidecar import Sidecar
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
            # Parse watchfolder
            message = WatchfolderMessage(body)

            essence_path = message.get_essence_path()
            xml_path = message.get_xml_path()

            # Check if essence and XML file exist
            if not essence_path.exists() or not xml_path.exists():
                # TODO: write event
                return

            # filesize of essence. Essence is moved when creating the bag.
            essence_filesize = essence_path.stat().st_size

            # Parse sidecar
            sidecar = Sidecar(xml_path)

            bag_path, bag = create_sip_bag(message, sidecar)

            # Regex to match essence paths in bag to fetch md5
            regex = re.compile("data/representations/.*/data/.*")

            for filepath, fixity in bag.entries.items():
                if regex.match(filepath):
                    md5_essence = fixity["md5"]

            # Send Pulsar event
            attributes = EventAttributes(
                type=PRODUCER_TOPIC,
                source=APP_NAME,
                subject=essence_path.stem,
                outcome=EventOutcome.SUCCESS,
            )

            data = {
                "host": self.config["host"],
                "path": str(bag_path),
                "outcome": EventOutcome.SUCCESS.to_str(),
                "message": f"SIP created: '{bag_path}'",
                "essence_filename:": essence_path.name,
                "md5_hash_essence": md5_essence,
                "cp_id": message.flow_id,
                "local_id": sidecar.local_id,
                "essence_filesize": essence_filesize,
                "bag_filesize": bag_path.stat().st_size,
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
