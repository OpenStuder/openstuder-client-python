from openstuder import SIAsyncGatewayClient, SIProtocolError, SIStatus


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.read_property('demo.sol.11004')


def on_property_read(status: SIStatus, id_: str, value: any):
    print(f'Property read, status = {status}, id = {id_}, value = {value}')
    client.disconnect()


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_property_read = on_property_read
client.connect('localhost', background=False)