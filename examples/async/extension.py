from openstuder import SIAsyncGatewayClient, SIProtocolError, SIExtensionStatus
import json


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    print(f'Connected, available extensions = {client.available_extensions()}')
    if 'WifiConfig' in client.available_extensions():
        client.call_extension('WifiConfig', 'scan')


def on_extension_called(extension: str, command: str, status: SIExtensionStatus, parameters: dict, body: str):
    print(f'WiFi scan, status = {status}')
    if status == SIExtensionStatus.SUCCESS:
        networks = json.loads(body)
        for network in networks:
            print(f'{network["ssid"]}, {network["signal"]}dBm, encrypted={network["encrypted"]}')
    client.disconnect()


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_extension_called = on_extension_called
client.connect('openstuder.lan', user='expert', password='expert', background=False)