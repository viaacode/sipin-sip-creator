#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from viaa.configuration import ConfigParser
from viaa.observability import logging

import pika


class RabbitClient:
    def __init__(self):
        self.stopped = False
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

        self.prefetch_count = int(self.rabbit_config["prefetch_count"])

    def listen(self, on_message_callback, queue=None):
        if queue is None:
            queue = self.rabbit_config["queue"]

        try:
            while not self.stopped:
                try:
                    self.channel = self.connection.channel()

                    self.channel.basic_qos(
                        prefetch_count=self.prefetch_count, global_qos=False
                    )

                    self.channel.basic_consume(
                        queue=queue, on_message_callback=on_message_callback
                    )

                    self.channel.start_consuming()
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
            self.stop_consuming()

    def stop_consuming(self):
        self.stopped = True
        self.channel.stop_consuming()
