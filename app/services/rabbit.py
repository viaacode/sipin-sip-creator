#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from viaa.configuration import ConfigParser
from viaa.observability import logging

import pika


class RabbitClient:
    def __init__(self):
        configParser = ConfigParser()
        self.log = logging.get_logger(__name__, config=configParser)
        self.rabbit_config = configParser.app_cfg["rabbitmq"]

        self.credentials = pika.PlainCredentials(
            self.rabbit_config["username"], self.rabbit_config["password"]
        )

        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=self.rabbit_config["host"],
                port=self.rabbit_config["port"],
                credentials=self.credentials,
            )
        )

        self.channel = self.connection.channel()

        self.prefetch_count = int(self.rabbit_config["prefetch_count"])

    def listen(self, on_message_callback, queue=None):
        if queue is None:
            queue = self.rabbit_config["queue"]

        try:
            while True:
                try:
                    channel = self.connection.channel()

                    self.channel.basic_qos(
                        prefetch_count=self.prefetch_count, global_qos=False
                    )

                    channel.basic_consume(
                        queue=queue, on_message_callback=on_message_callback
                    )

                    channel.start_consuming()
                except pika.exceptions.StreamLostError:
                    self.log.warning("RMQBridge lost connection, reconnecting...")
                    time.sleep(3)
                except pika.exceptions.ChannelWrongStateError:
                    self.log.warning(
                        "RMQBridge wrong state in channel, reconnecting..."
                    )
                    time.sleep(3)
                except pika.exceptions.AMQPHeartbeatTimeout:
                    self.log.warning("RMQBridge heartbeat timed out, reconnecting...")
                    time.sleep(3)

        except KeyboardInterrupt:
            channel.stop_consuming()

        self.connection.close()
