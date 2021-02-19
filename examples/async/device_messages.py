from openstuder import SIAsyncGatewayClient, SIProtocolError, SIDeviceMessage


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    print(f'Connected, access level = {access_level}, gateway runs version {client.gateway_version()}')


def on_device_message(message: SIDeviceMessage):
    print(f'{message.timestamp}: [{message.access_id}.{message.device_id}] {message.message} ({message.message_id})')


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_device_message = on_device_message
client.connect('localhost', background=False)