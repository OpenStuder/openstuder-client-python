from openstuder import SIBluetoothGatewayClient

client = SIBluetoothGatewayClient()
gateways = client.discover()
for gateway in gateways:
    print(f'Found gateway with address/UUID: {gateway}')