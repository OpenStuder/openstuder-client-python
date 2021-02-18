from openstuder import SIGatewayClient, SIProtocolError

try:
    client = SIGatewayClient()
    client.connect('localhost')
    status, count, messages = client.read_messages()
    print(f'Read messages, status = {status}, count = {count}')
    for message in messages:
        print(f'{message.timestamp}: [{message.access_id}.{message.device_id}] {message.message} ({message.message_id})')

except SIProtocolError as error:
    print(f'Error: {error.reason()}')
