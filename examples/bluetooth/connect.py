from openstuder import SIBluetoothGatewayClient, SIProtocolError


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    print(f'Connected, access level = {access_level}, gateway runs version {gateway_version}')


client = SIBluetoothGatewayClient()
client.on_error = on_error
client.on_connected = on_connected

gateways = client.discover()
if len(gateways) > 0:
    client.connect(gateways[0], background=False)
