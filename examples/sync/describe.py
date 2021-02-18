from openstuder import SIGatewayClient, SIProtocolError, SIDescriptionFlags

try:
    client = SIGatewayClient()
    client.connect('localhost')
    status, id_, description = client.describe('demo', flags=SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
    print(f'Description for {id_} demo, status = {status}')
    print(description)

except SIProtocolError as error:
    print(f'Error: {error.reason()}')
