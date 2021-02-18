from openstuder import SIGatewayClient, SIProtocolError

try:
    client = SIGatewayClient()
    client.connect('localhost')
    status, id_, entries, csv = client.read_datalog_csv('demo.inv.3136', limit=50)
    print(f'Read datalog for {id_}, status = {status}, entries = {entries}')
    with open('demo.inv.3136.csv', 'w') as file:
        file.write(csv)

except SIProtocolError as error:
    print(f'Error: {error.reason()}')
