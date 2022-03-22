import datetime
from typing import List, Tuple

from openstuder import SIBluetoothGatewayClient, SIProtocolError, SIStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.read_datalog('demo.inv.3136', limit=50)


def on_datalog_read(status: SIStatus, id_: str, entries: int, data: List[Tuple[datetime.datetime, any]]):
    print(f'Read datalog for {id_}, status = {status}, entries = {entries}')
    for entry in data:
        print(f'  |- timestamp = {entry[0]}, value = {entry[1]}')
    client.disconnect()


client = SIBluetoothGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_datalog_read = on_datalog_read

gateways = client.discover()
if len(gateways) > 0:
    client.connect(gateways[0], background=False)
