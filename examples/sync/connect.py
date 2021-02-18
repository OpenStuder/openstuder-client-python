from openstuder import SIGatewayClient, SIProtocolError

host = 'localhost'

client = SIGatewayClient()
try:
    access_level = client.connect(host)

except SIProtocolError as error:
    print(f'Unable to connect: {error.reason()}')
    quit(1)

print(f'Connected, access level = {access_level}, gateway runs version {client.gateway_version()}')