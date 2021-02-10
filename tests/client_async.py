from siclient import SIAsyncGatewayClient, SIAsyncGatewayClientCallbacks
import time


client = SIAsyncGatewayClient()


class MyAsyncCallbacks(SIAsyncGatewayClientCallbacks):
    def on_connected(self, access_level, gateway_version):
        client.subscribe_to_property('demo.inv.3136')
        print(f'CONNECTED, access_level={access_level}')

    def on_disconnected(self):
        print('DISCONNECTED')

    def on_error(self, reason):
        print(f'ERROR reason={reason}')

    def on_enumerated(self, status, device_count):
        print(f'ENUMERATED status={status}, count={device_count}')

    def on_description(self, status, id_, description):
        super().on_description(status, id_, description)

    def on_property_read(self, status, property_id, value):
        print(f'PROPERTY READ status={status}, id={property_id}, value={value}')

    def on_property_written(self, status, property_id):
        print(f'PROPERTY WRITE status={status}, id={property_id}')

    def on_property_subscribed(self, status, property_id):
        print(f'PROPERTY SUBSCRIBED status={status}, id={property_id}')

    def on_property_unsubscribed(self, status, property_id):
        print(f'PROPERTY UNSUBSCRIBED status={status}, id={property_id}')

    def on_property_updated(self, property_id, value):
        print(f'PROPERTY UPDATED id={property_id}, value={value}')

    def on_datalog_read(self, status, property_id, count, values):
        print(f'DATALOG READ status={status}, property_id={property_id}, values={values}')

    def on_device_message(self, id_, message_id, message):
        print(f'DEVICE MESSAGE id={id}, message_id={message_id}, message={message}')

    def on_messages_read(self, status, count, messages):
        print(f'MESSAGE READ status={status}, count={count}, messages={messages}')


callbacks = MyAsyncCallbacks()


if __name__ == "__main__":
    client.set_callbacks(callbacks)
    client.connect('localhost')
    time.sleep(10)
    client.disconnect()
