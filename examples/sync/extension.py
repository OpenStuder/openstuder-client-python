from openstuder import SIGatewayClient, SIProtocolError

try:
    client = SIGatewayClient()
    client.connect('localhost', 1987, 'expert', 'expert')
    print(f'Available extensions: {client.available_extensions()}')
    status, params, body = client.call_extension('WifiConfig', 'scan')
    print(f'Extension called, status = {status}, params = {params}, body = {body}')

except SIProtocolError as error:
    print(f'Error: {error.reason()}')

