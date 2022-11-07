from openstuder import SIAsyncGatewayClient, SIProtocolError, SIStatus, SIDeviceFunctions


def on_error(error: SIProtocolError):
    print(f'Unable to connect: {error.reason()}')


def on_connected(access_level: str, gateway_version: str):
    client.find_properties('*.*.3136')


def on_properties_found(status: SIStatus, id_: str, count: int, virtual: bool, functions_mask: SIDeviceFunctions,
                        properties: list):
    print(f'Found properties for {id_}, status = {status}, count = {count}, virtual = {virtual}, '
          f'functions = {functions_mask} : {properties}')
    client.disconnect()


client = SIAsyncGatewayClient()
client.on_error = on_error
client.on_connected = on_connected
client.on_properties_found = on_properties_found
client.connect('localhost', background=False)