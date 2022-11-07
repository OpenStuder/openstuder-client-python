from openstuder import SIGatewayClient, SIProtocolError

try:
    client = SIGatewayClient()
    client.connect('localhost')
    status, id_, count, virtual, functions, properties = client.find_properties('*.*.3136')
    print(f'Found properties for {id_}, status = {status}, count = {count}, virtual = {virtual}, '
          f'functions = {functions} : {properties}')

except SIProtocolError as error:
    print(f'Error: {error.reason()}')
