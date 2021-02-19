from openstuder import SIAsyncGatewayClient, SIProtocolError, SIStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.read_datalog('demo.inv.3136', limit=50)


def on_datalog_read_csv(status: SIStatus, id_: str, entries: int, csv: str):
    print(f'Read datalog for {id_}, status = {status}, entries = {entries}')
    with open('demo.inv.3136.csv', 'w') as file:
        file.write(csv)
    client.disconnect()


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_datalog_read_csv = on_datalog_read_csv
client.connect('localhost', background=False)