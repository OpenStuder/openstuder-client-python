from openstuder import SIAsyncGatewayClient, SIProtocolError, SIStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.enumerate()


def on_enumerated(status: SIStatus, device_count: int):
    print(f'Enumerated, status = {status}, device count = {device_count}')
    client.disconnect()


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_enumerated = on_enumerated
client.connect('localhost', background=False)