from typing import List
from openstuder import SIAsyncGatewayClient, SIProtocolError, SIStatus, SIPropertyReadResult


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.read_properties(['demo.sol.11004', "demo.inv.3136"])


def on_properties_read(results: List[SIPropertyReadResult]):
    for result in results:
        print(f'Property read, status = {result.status}, id = {result.id}, value = {result.value}')
    client.disconnect()


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_properties_read = on_properties_read
client.connect('localhost', background=False)