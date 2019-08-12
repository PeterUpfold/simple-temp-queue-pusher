#!/usr/bin/env python3
# example-queue-reader
# Simple script to test receiving events through the queue and dump the most recent event to
# a file on disk.
#
# Copyright 2019 Peter Upfold
#
# Licensed under the Apache 2.0 Licence.


from azure.servicebus import ServiceBusClient
import yaml

config_file = open('config.yml', 'r')
config = yaml.safe_load(config_file)

bus_service = ServiceBusClient(
    service_namespace=config['namespace'],
    shared_access_key_name=config['shared_access_key_name'],
    shared_access_key_value=config['shared_access_key_value'])

queue_client = bus_service.get_queue(config['queue_name'])

messages = queue_client.get_receiver()
for message in messages:
    if len(str(message)) > 0:
            print(message)
            with open(config['output_file'], 'w') as output_file:
              output_file.write(str(message))
    else:
            print('Zero-length message')
    message.complete()
