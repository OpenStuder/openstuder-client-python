from openstuder import SIGatewayClient, SIProtocolError

try:
    client = SIGatewayClient()
    client.connect('localhost')
    results = client.read_properties(['demo.sol.11004', 'demo.inv.3136'])
    for result in results:
        print(f'Read property {result.id}, status = {result.status}, value = {result.value}')

except SIProtocolError as error:
    print(f'Error: {error.reason()}')
