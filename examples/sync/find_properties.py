from openstuder import SIGatewayClient, SIProtocolError, SIDescriptionFlags

try:
    client = SIGatewayClient()
    client.connect('localhost')
    status, id_, count, properties = client.find_properties('*.*.3136')
    print(f'Found properties for {id_}, status = {status}, count = {count} : {properties}')

except SIProtocolError as error:
    print(f'Error: {error.reason()}')
