from openstuder import SIGatewayClient, SIProtocolError

try:
    client = SIGatewayClient()
    client.connect('localhost')
    status, id_ = client.write_property('demo.inv.1399')
    print(f'Wrote property {id_}, status = {status}')

except SIProtocolError as error:
    print(f'Error: {error.reason()}')
