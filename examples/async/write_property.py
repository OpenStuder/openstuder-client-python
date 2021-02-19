from openstuder import SIAsyncGatewayClient, SIProtocolError, SIStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.write_property('demo.inv.1415')


def on_property_written(status: SIStatus, id_: str):
    print(f'Property written, status = {status}, id = {id_}')
    client.disconnect()


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_property_written = on_property_written
client.connect('localhost', background=False)
