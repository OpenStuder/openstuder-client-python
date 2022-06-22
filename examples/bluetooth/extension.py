from typing import List

from openstuder import SIBluetoothGatewayClient, SIProtocolError, SIStatus, SIExtensionStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    print(f'Connected, access level = {access_level}, gateway runs version {gateway_version}')
    client.call_extension('WifiConfig', 'scan')


def on_extension_called(extension: str, command: str, status: SIExtensionStatus, parameters: List[any]):
    print(f'WiFi scan, status = {status}')
    if status == SIExtensionStatus.SUCCESS:
        for network in parameters:
            print(network)
    client.disconnect()


client = SIBluetoothGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_extension_called = on_extension_called

gateways = client.discover()
if len(gateways) > 0:
    client.connect(gateways[0], user='expert', password='expert', background=False)
