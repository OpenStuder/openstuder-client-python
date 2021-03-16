from typing import List
from openstuder import SIAsyncGatewayClient, SIProtocolError, SIStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.read_datalog_properties()


def on_datalog_properties_read(status: SIStatus, properties: List[str]):
    print(f'Read datalog properties, status = {status}:')
    for property in properties:
        print(f'  - {property}')
    client.disconnect()


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_datalog_properties_read = on_datalog_properties_read
client.connect('localhost', background=False)