from openstuder import SIGatewayClient, SIProtocolError

host = 'localhost'
user = 'garfield'
password = 'lasagne'

client = SIGatewayClient()
try:
    access_level = client.connect(host, user=user, password=password)

except SIProtocolError as error:
    print(f'Unable to connect: {error.reason()}')
    quit(1)

print(f'Connected, access level = {access_level}, gateway runs version {client.gateway_version()}')