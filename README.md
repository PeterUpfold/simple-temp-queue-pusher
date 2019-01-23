# simple-temp-queue-pusher
Push a simple temperature sensor reading into an Azure Service Bus Queue

## Requirements

Python 3.x
`pip3 install azure-servicebus`

Designed to work with [simple-temp-readout](https://github.com/PeterUpfold/TEMPered) and a TEMPer thermometer as produced by
RDing Technology and sold under the name PCsensor.

## Bootstrapping

`cp config.example.yml config.yml`

Fill in details of your Azure Namespace, SAS details ("Policy" name is `shared_access_key_name`) and queue name.

Extremely simple consumer of these queue messages is in `example-queue-reader.py`

## Licence

Apache License 2.0
