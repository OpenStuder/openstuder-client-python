from openstuder import SIGatewayClient, SIProtocolError

try:
    client = SIGatewayClient()
    client.connect('localhost')
    status, id_, value = client.read_property('demo.sol.11004')
    print(f'Read property {id_}, status = {status}, value = {value}')

except SIProtocolError as error:
    print(f'Error: {error.reason()}')
