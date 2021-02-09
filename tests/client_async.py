from siclient import SIAsyncGatewayClient
import time


client = SIAsyncGatewayClient()


def on_connected(access_level):
    client.subscribe_to_property('dummy.0.3000')
    print(f'CONNECTED, access_level={access_level}')


def on_enumerated(status, device_count):
    print(f'ENUMERATED status={status}, count={device_count}')


def on_property_read(status, property_id, value):
    print(f'PROPERTY READ status={status}, id={property_id}, value={value}')


def on_property_written(status, property_id):
    print(f'PROPERTY WRITE status={status}, id={property_id}')


def on_property_subscribed(status, property_id):
    print(f'PROPERTY SUBSCRIBED status={status}, id={property_id}')


def on_property_unsubscribed(status, property_id):
    print(f'PROPERTY UNSUBSCRIBED status={status}, id={property_id}')


def on_property_updated(property_id, value):
    print(f'PROPERTY UPDATED id={property_id}, value={value}')


def on_device_message(id, message_id, message):
    print(f'DEVICE MESSAGE id={id}, message_id={message_id}, message={message}')


def on_disconnected():
    print('DISCONNECTED')


def on_error(error):
    print(f'ERROR reason:{error}')


if __name__ == "__main__":
    client.on_connected = on_connected
    client.on_enumerated = on_enumerated
    client.on_property_read = on_property_read
    client.on_property_written = on_property_written
    client.on_property_subscribed = on_property_subscribed
    client.on_property_unsubscribed = on_property_unsubscribed
    client.on_property_updated = on_property_updated
    client.on_disconnected = on_disconnected
    client.on_error = on_error
    client.connect('localhost')
    print("HELLOOO?")
    time.sleep(2)
    client.subscribe_to_property('demo.inv.3136')
    time.sleep(10)
    client.disconnect()
