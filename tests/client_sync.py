from openstuder import SIGatewayClient, SIDescriptionFlags, SIDeviceFunctions

if __name__ == "__main__":
    # Establish connection.
    client = SIGatewayClient()
    client.connect('localhost', 1987, "expert", "expert")

    # Client/gateway information.
    print(f'CONNECTED: access_level = {client.access_level()}, gateway_version = {client.gateway_version()}')

    # Enumerate devices.
    status, count = client.enumerate()
    print(f'ENUMERATE -> ENUMERATED: status = {status}, count = {count}')

    # Retrieve description.
    status, id_, desc = client.describe(flags=SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION |
                                              SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
    print(f'DESCRIBE -> DESCRIPTION: status = {status}, id = {id_}, description={desc}')

    # Find properties.
    status, id_, count, virtual, functions, props = client.find_properties('*.*.3136', False, SIDeviceFunctions.ALL)
    print(f'FIND PROPERTY -> PROPERTIES FOUND: status = {status}, id = {id_}, count={count}, virtual={virtual}, functions={functions}, props={props}')

    # Read property.
    status, id_, value = client.read_property('demo.inv.3136')
    print(f'READ PROPERTY -> PROPERTY READ: status = {status}, id = {id_}, value={value}')

    # Read properties.
    results = client.read_properties(['demo.inv.3136', 'demo.inv.3137'])
    for result in results:
        print(f'READ PROPERTIES -> PROPERTIES READ: status = {result.status}, id = {result.id}, value={result.value}')

    # Write property.
    status, id_ = client.write_property('demo.inv.1399')
    print(f'WRITE PROPERTY -> PROPERTY WRITTEN: status = {status}, id = {id_}')

    # Read datalog.
    status, id_, count, values = client.read_datalog_csv('demo.inv.3136')
    print(f'READ DATALOG -> DATALOG READ: status = {status}, id = {id_}, count = {count}, values = {values}')

    # Read messages.
    status, count, messages = client.read_messages()
    print(f'READ MESSAGES -> MESSAGES READ: status = {status}, count = {count}, messages = {messages}')

    # Call extension.
    status, params, body = client.call_extension("WifiConfig", "status")
    print(f'EXTENSION CALLED (WiFi status) -> status = {status}, params = {params}')

    # Disconnect.
    client.disconnect()
