import time
from typing import List
from openstuder import SIAsyncGatewayClient, SIProtocolError, SIStatus, SIPropertySubscriptionResult


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.subscribe_to_properties(['demo.sol.11004', 'demo.inv.3136'])


def on_properties_subscribed(statuses: List[SIPropertySubscriptionResult]):
    for status in statuses:
        print(f'Subscribed to {status.id}, status = {status.status}')


def on_property_updated(id_: str, value: any):
    print(f'Property {id_} updated, value = {value}')


def on_properties_unsubscribed(statuses: List[SIPropertySubscriptionResult]):
    for status in statuses:
        print(f'Unsubscribed from {status.id}, status = {status.status}')


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_properties_subscribed = on_properties_subscribed
client.on_property_updated = on_property_updated
client.on_properties_unsubscribed = on_properties_unsubscribed
client.connect('localhost')
time.sleep(10)
client.unsubscribe_from_properties(['demo.sol.11004', 'demo.inv.3136'])
time.sleep(2)
