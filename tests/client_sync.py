from siclient import SIGatewayClient, SIDescriptionFlags


if __name__ == "__main__":
    # Test connection.
    client = SIGatewayClient()
    client.connect('localhost')

    # Test enumeration.
    status, count = client.enumerate()
    print(f'ENUMERATE -> ENUMERATED: status = {status}, count = {count}')

    # Test description.
    status, id_, desc = client.describe(flags=SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
    print(f'DESCRIBE -> DESCRIPTION: status = {status}, id = {id_}, desc={desc}')

    # Test property read.
    status, id_, value = client.read_property('demo.inv.3000')
    print(f'READ PROPERTY -> PROPERTY READ: status = {status}, id = {id_}, value={value}')

    # Test property write.
    status, id_ = client.write_property('demo.inv.1399')
    print(f'WRITE PROPERTY -> PROPERTY WRITTEN: status = {status}, id = {id_}')

    # Test datalog read.
    status, id_, count, values = client.read_datalog('demo.inv.3136')
    print(f'READ DATALOG -> DATALOG READ: status = {status}, id = {id_}, count = {count}, values = {values}')

    # Test message read.
    status, count, messages = client.read_messages()
    print(f'READ MESSAGES -> MESSAGES READ: status = {status}, count = {count}, messages = {messages}')
