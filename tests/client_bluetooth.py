import datetime
from openstuder import SIBluetoothGatewayClient, SIBluetoothGatewayClientCallbacks, SIStatus, SIDeviceMessage, SIAccessLevel
from typing import List, Tuple, Optional


client = SIBluetoothGatewayClient()


class MyBluetoothCallbacks(SIBluetoothGatewayClientCallbacks):

    def on_connected(self, access_level: SIAccessLevel, gateway_version: str) -> None:
        print(f'CONNECTED, gateway version {gateway_version}, access level = {access_level}')
        client.enumerate()

    def on_disconnected(self) -> None:
        print('DISCONNECTED')

    def on_error(self, reason) -> None:
        print(f'ERROR: {reason}')

    def on_enumerated(self, status: SIStatus, device_count: int) -> None:
        print(f'ENUMERATED, status = {status}, count = {device_count}')
        client.describe()

    def on_description(self, status: SIStatus, id_: Optional[str], description: any) -> None:
        print(f'DESCRIPTION: status = {status}, id = {id_}')

        if id_ is None:
            print(' |- GATEWAY: ')
            for key in description:
                print(f'      |- {key} : {description[key]}')
            client.describe("demo")
        elif id_ == 'demo':
            print(f' |- DEVICE ACCESS: {id_}')
            for key in description:
                print(f'      |- {key} : {description[key]}')
            client.describe('demo.inv')
        elif id_ == 'demo.inv':
            print(f' |- DEVICE: {id_}')
            for pid in description:
                print(f'      |- {pid}')
            client.describe(f'demo.inv.{description[0]}')
        else:
            print(f' |- PROPERTY: {id_}')
            for key in description:
                print(f'      |- {key} = {description[key]}')
            client.read_property("demo.inv.3032")

    def on_property_read(self, status: SIStatus, property_id: str, value: Optional[any]) -> None:
        print(f'PROPERTY READ status={status}, id={property_id}, value={value}')
        client.write_property("demo.inv.1415")

    def on_property_written(self, status: SIStatus, property_id: str) -> None:
        print(f'PROPERTY WRITTEN status={status}, id={property_id}')
        client.subscribe_to_property("demo.inv.3136")

    def on_property_subscribed(self, status: SIStatus, property_id: str) -> None:
        print(f'PROPERTY SUBSCRIBED status={status}, id={property_id}')

    def on_property_unsubscribed(self, status: SIStatus, property_id: str) -> None:
        print(f'PROPERTY UNSUBSCRIBED status={status}, id={property_id}')
        client.read_datalog_properties()

    def on_property_updated(self, property_id: str, value: any) -> None:
        print(f'PROPERTY UPDATED id={property_id}, value={value}')
        client.unsubscribe_from_property("demo.inv.3136")

    def on_datalog_properties_read(self, status: SIStatus, properties: List[str]) -> None:
        print(f'DATALOG PROPERTIES status={status}, properties={properties}')
        if len(properties) > 0:
            client.read_datalog(properties[0], limit=10)

    def on_datalog_read(self, status: SIStatus, property_id: str, count: int,
                        values: List[Tuple[datetime.datetime, any]]) -> None:
        print(f'DATALOG READ status={status}, property_id={property_id}, count={count}')
        for timestamp, value in values:
            print(f'  |- timestamp={timestamp}, value={value}')
        client.read_messages()

    def on_device_message(self, message: SIDeviceMessage) -> None:
        print(f'DEVICE MESSAGE timestamp={message.timestamp}, access_id={message.access_id}, device_id={message.device_id}, message_id={message.message_id}, message={message.message}')

    def on_messages_read(self, status: SIStatus, count: int, messages: List[SIDeviceMessage]) -> None:
        print(f'MESSAGES READ status={status}, count={count}')
        for message in messages:
            print(
                f'  |- timestamp={message.timestamp}, access_id={message.access_id}, device_id={message.device_id}, message_id={message.message_id}, message={message.message}')
        client.disconnect()


callbacks = MyBluetoothCallbacks()


if __name__ == '__main__':
    client.set_callbacks(callbacks)
    print('DISCOVERING...')
    addresses = client.discover()
    if len(addresses) != 0:
        print(f'CONNECTING to {addresses[0]}...')
        client.connect(addresses[0], background=False)
