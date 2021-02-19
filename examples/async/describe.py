from openstuder import SIAsyncGatewayClient, SIProtocolError, SIStatus, SIDescriptionFlags


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.describe('demo', flags=SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)


def on_description(status: SIStatus, id_: str, description: object):
    print(f'Description for {id_}, status = {status}')
    print(description)
    client.disconnect()


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_description = on_description
client.connect('localhost', background=False)