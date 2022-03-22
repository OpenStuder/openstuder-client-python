from openstuder import SIBluetoothGatewayClient, SIProtocolError, SIStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    print(f'Connected, access level = {access_level}, gateway runs version {gateway_version}')
    client.enumerate()


def on_enumerated(status: SIStatus, device_count: int):
    print(f'Enumerated, status = {status}, device count = {device_count}')
    client.disconnect()


client = SIBluetoothGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_enumerated = on_enumerated

gateways = client.discover()
if len(gateways) > 0:
    client.connect(gateways[0], background=False)
