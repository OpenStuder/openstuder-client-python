from openstuder import SIBluetoothGatewayClient, SIProtocolError, SIStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.describe('demo')


def on_description(status: SIStatus, id_: str, description: object):
    print(f'Description for {id_}, status = {status}')
    print(description)
    client.disconnect()


client = SIBluetoothGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_description = on_description

gateways = client.discover()
if len(gateways) > 0:
    client.connect(gateways[0], background=False)
