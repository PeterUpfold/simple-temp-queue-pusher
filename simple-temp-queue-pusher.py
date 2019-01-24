# simple-temp-queue-pusher
# Push a simple temperature sensor reading into an Azure Service Bus Queue
#
# Copyright 2019 Peter Upfold
#
# Licensed under the Apache 2.0 Licence.


from azure.servicebus import ServiceBusClient, Message
import yaml
import subprocess
import json
from datetime import datetime

config_file = open('config.yml', 'r')
config = yaml.safe_load(config_file)

bus_service = ServiceBusClient(
    service_namespace=config['namespace'],
    shared_access_key_name=config['shared_access_key_name'],
    shared_access_key_value=config['shared_access_key_value'])

queue_client = bus_service.get_queue(config['queue_name'])


proc = subprocess.Popen(['./simple-temp-readout', '/dev/hidraw1', '0x01', '0x80', '0x33', '0x01', '0x00', '0x00', '0x00', '0x00'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, err = proc.communicate()


if len(output) > 0:
	message_object = { 'time': datetime.now().isoformat(), 'temp': str(output) }
	queue_client.send(Message(json.dumps(message_object)))
