#!/usr/bin/env python3
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
import logging
from datetime import datetime
from time import sleep
import os
import sys

libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from PUStatusReporter import reporter

config_file = open('config.yml', 'r')
config = yaml.safe_load(config_file)

logging.basicConfig(level=logging.INFO)

bus_service = ServiceBusClient(
    service_namespace=config['namespace'],
    shared_access_key_name=config['shared_access_key_name'],
    shared_access_key_value=config['shared_access_key_value'])

queue_client = bus_service.get_queue(config['queue_name'])


while True:
	try:

		logging.info('Spawning simple-temp-readout')

		proc = subprocess.Popen(['./simple-temp-readout', '/dev/hidraw1', '0x01', '0x80', '0x33', '0x01', '0x00', '0x00', '0x00', '0x00'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		output, err = proc.communicate()

		date_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
		err_string = err.decode('ascii').strip() + f' {date_string}'
		if len(err_string) > 0:
			logging.warning(f'Completed with stderr: {err_string}')
			try:
				if not reporter.get_context('cupboard_temperature_fail', config['status_reporter_key']):
					reporter.create_context('cupboard_temperature_fail', config['status_reporter_key'])
				reporter.set_status('cupboard_temperature_fail', err_string, config['status_reporter_key'])
			except IOError as e:
				logging.error(f'Failed to communicate with StatusReporter: {e}')

		try:
			#print(output.decode('ascii').strip())
			actual_temp = float(output.decode('ascii').strip())
			logging.info(f"Temperature: {actual_temp}. Panic threshold: {config['panic_temperature']}")
			
			try:
				if not reporter.get_context('cupboard_temperature', config['status_reporter_key']):
					reporter.create_context('cupboard_temperature', config['status_reporter_key'])

				date_string = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
				actual_temp_with_date = f'{actual_temp} {date_string}'
				reporter.set_status('cupboard_temperature', actual_temp_with_date, config['status_reporter_key'])
			except IOError as e:
				logging.error(f'Failed to communicate with StatusReporter: {e}')
			
			if actual_temp > config['panic_temperature']:
				logging.error(f'Panic at {actual_temp}')
				actions = subprocess.Popen(['./temp-panic-actions'])
				actions_out, actions_err = actions.communicate()

		except Exception as e:
			logging.error(f'parse fail? {e}')

		if len(output) > 0:
			message_object = { 'time': datetime.now().isoformat(), 'temp': output.decode('ascii').strip() }
			queue_client.send(Message(json.dumps(message_object)))
	except Exception as outer_e:
		logging.error(f'Outer loop failed: {outer_e}')

	sleep(60)
