import time
from openstuder import SIAsyncGatewayClient, SIProtocolError


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    print(f'Connected, access level = {access_level}, gateway runs version {client.gateway_version()}')


host = 'localhost'

client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.connect(host, background=False)