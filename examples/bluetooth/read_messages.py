from openstuder import SIBluetoothGatewayClient, SIProtocolError, SIStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.read_messages()


def on_messages_read(status: SIStatus, count: int, messages: list):
    print(f'Read messages, status = {status}, messages = {count}')
    if status == SIStatus.SUCCESS:
        for message in messages:
            print(f'{message.timestamp}: [{message.access_id}.{message.device_id}] {message.message} ({message.message_id})')
    client.disconnect()


client = SIBluetoothGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_messages_read = on_messages_read

gateways = client.discover()
if len(gateways) > 0:
    client.connect(gateways[0], background=False)