from openstuder import SIGatewayClient, SIProtocolError

try:
    client = SIGatewayClient()
    client.connect('localhost')
    status, properties = client.read_datalog_properties()
    print(f'Read datalog properties, status = {status}:')
    for property in properties:
        print(f'  - {property}')
    client.disconnect()

except SIProtocolError as error:
    print(f'Error: {error.reason()}')
