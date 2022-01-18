#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pika.exceptions
from viaa.configuration import ConfigParser
from viaa.observability import logging

from app.services import rabbit


class EventListener:
    def __init__(self):
        configParser = ConfigParser()
        self.log = logging.get_logger(__name__, config=configParser)
        self.config = configParser.app_cfg
        try:
            self.rabbitClient = rabbit.RabbitClient()
        except pika.exceptions.AMQPConnectionError as error:
            self.log.error("Connection to RabbitMQ failed.")
            raise error

    def handle_message(self, channel, method, properties, body):
        # TODO:
        #  - Parse message
        #  - Transform xml metadata to METS
        #  - Create bag
        #  - Send event to transfer-controller topic
        channel.basic_ack(method.delivery_tag)

    def start(self):
        # Start listening for incoming messages
        self.log.info("Start to listen for messages...")
        self.rabbitClient.listen(self.handle_message)
