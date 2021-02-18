from openstuder import SIGatewayClient, SIProtocolError

try:
    client = SIGatewayClient()
    client.connect('localhost')
    status, device_count = client.enumerate()
    print(f'Enumeration complete, status = {status}, device count = {device_count}')

except SIProtocolError as error:
    print(f'Error: {error.reason()}')

