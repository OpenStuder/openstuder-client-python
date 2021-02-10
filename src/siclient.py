import websocket
import json
from enum import Enum, Flag, auto
from threading import Thread
import datetime
from typing import Callable, Optional, Tuple


class SIProtocolError(IOError):
    """
    Class for all OpenStuder communication errors.
    """

    def __init__(self, message):
        super().__init__(message)

    def reason(self) -> str:
        """
        Returns the actual reason for the error.

        :return: Reason for the error.
        """
        return super().args[0]


class SIConnectionState(Enum):
    """
    State of the connection to the OpenStuder gateway of a client.

    - **SIConnectionState.DISCONNECTED**: The client is not connected at all.
    - **SIConnectionState.CONNECTING**: The client tries to connect to the WebSocket server on the gateway.
    - **SIConnectionState.AUTHORIZING**: The WebSocket connection to the gateway has been established and the user is actually authorized.
    - **SIConnectionState.CONNECTED**: The WebSocket connection is established and the user is authorized, the client is ready to be used.
    """

    DISCONNECTED = auto()
    CONNECTING = auto()
    AUTHORIZING = auto()
    CONNECTED = auto()


class SIAccessLevel(Enum):
    """
    Level of access granted to a client from the OpenStuder gateway.

    - **NONE**: No access at all.
    - **BASIC**: Basic access to device information properties (configuration excluded).
    - **INSTALLER**: Basic access + additional access to most common configuration properties.
    - **EXPERT**: Installer + additional advanced configuration properties.
    - **QSP**: Expert and all configuration and service properties.
    """

    NONE = auto()
    BASIC = auto()
    INSTALLER = auto()
    EXPERT = auto()
    QSP = auto()

    @staticmethod
    # TODO: Why can't I specify the return type to be SIAccessLevel?
    def from_string(string_: str):
        if string_ == 'None':
            return SIAccessLevel.NONE
        elif string_ == 'Basic':
            return SIAccessLevel.BASIC
        elif string_ == 'Installer':
            return SIAccessLevel.INSTALLER
        elif string_ == 'Expert':
            return SIAccessLevel.EXPERT
        elif string_ == 'QSP':
            return SIAccessLevel.QSP
        else:
            return SIAccessLevel.NONE


class SIDescriptionFlags(Flag):
    """
    Flags to control the format of the **DESCRIBE** functionality.

    - **SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION**: Includes device access instances information.
    - **SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION**: Include device information.
    - **SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION**: Include device property information.
    - **SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION**: Include driver information.
    """

    INCLUDE_ACCESS_INFORMATION = auto()
    INCLUDE_DEVICE_INFORMATION = auto()
    INCLUDE_PROPERTY_INFORMATION = auto()
    INCLUDE_DRIVER_INFORMATION = auto()


class _SIAbstractGatewayClient:
    def __init__(self):
        pass

    @staticmethod
    def encode_authorize_frame_without_credentials() -> str:
        return f'AUTHORIZE\nprotocol_version:1\n\n'

    @staticmethod
    def encode_authorize_frame_with_credentials(user: str, password: str) -> str:
        return f'AUTHORIZE\nuser:{user}\npassword:{password}\nprotocol_version:1\n\n'

    @staticmethod
    def decode_authorized_frame(frame: str) -> Tuple[SIAccessLevel, str]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'AUTHORIZED' and 'access_level' in headers and 'protocol_version' in headers and 'gateway_version' in headers:
            if headers['protocol_version'] == '1':
                return SIAccessLevel.from_string(headers['access_level']), headers['gateway_version']
            else:
                raise SIProtocolError('protocol version 1 not supported by server')
        elif command == 'ERROR' and 'reason' in headers:
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during authorization')

    @staticmethod
    def encode_enumerate_frame() -> str:
        return 'ENUMERATE'

    @staticmethod
    def decode_enumerated_frame(frame: str) -> Tuple[str, int]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'ENUMERATED':
            return headers['status'], int(headers['device_count'])
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during device enumeration')

    @staticmethod
    def encode_describe_frame(device_access_id: str, device_id: str, flags: SIDescriptionFlags) -> str:
        frame = 'DESCRIBE\n'
        if isinstance(flags, SIDescriptionFlags):
            frame += 'flags:'
            if flags & SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION:
                frame += 'IncludeAccessInformation,'
            if flags & SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION:
                frame += 'IncludeDeviceInformation,'
            if flags & SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION:
                frame += 'IncludePropertyInformation,'
            if flags & SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION:
                frame += 'IncludeDriverInformation,'
            frame = frame[:-1]
            frame += '\n'
        if device_access_id is not None:
            frame += f'id:{device_access_id}'
            if device_id is not None:
                frame += f'.{device_id}'
            frame += '\n'
        frame += '\n'
        return frame

    @staticmethod
    def decode_description_frame(frame: str) -> Tuple[str, Optional[str], object]:
        command, headers, body = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'DESCRIPTION' and 'status' in headers:
            status = headers['status']
            if status == 'Success':
                description = json.loads(body)
                return status, headers.get('id', None), description
            else:
                return status, headers.get('id', None), {}
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during description')

    @staticmethod
    def encode_read_property_frame(property_id: str) -> str:
        return f'READ PROPERTY\nid:{property_id}\n\n'

    @staticmethod
    def decode_property_read_frame(frame: str) -> Tuple[str, str, Optional[any]]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY READ' and 'status' in headers and 'id' in headers:
            status = headers['status']
            if status == 'Success' and 'value' in headers:
                return status, headers['id'], headers['value']
            else:
                return status, headers['id'], None
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during property read')

    @staticmethod
    def encode_write_property_frame(property_id: str, value: any) -> str:
        frame = f'WRITE PROPERTY\nid:{property_id}\n'
        if value is not None:
            frame += f'value:{value}\n'
        frame += '\n'
        return frame

    @staticmethod
    def decode_property_written_frame(frame: str) -> Tuple[str, str]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY WRITTEN' and 'status' in headers and 'id' in headers:
            return headers['status'], headers['id']
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during property write')

    @staticmethod
    def encode_subscribe_property_frame(property_id: str) -> str:
        return f'SUBSCRIBE PROPERTY\nid:{property_id}\n\n'

    @staticmethod
    def decode_property_subscribed_frame(frame: str) -> Tuple[str, str]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY SUBSCRIBED' and 'status' in headers and 'id' in headers:
            return headers['status'], headers['id']
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during property subscribe')

    @staticmethod
    def encode_unsubscribe_property_frame(property_id: str) -> str:
        return f'UNSUBSCRIBE PROPERTY\nid:{property_id}\n\n'

    @staticmethod
    def decode_property_unsubscribed_frame(frame: str) -> Tuple[str, str]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY UNSUBSCRIBED' and 'status' in headers and 'id' in headers:
            return headers['status'], headers['id']
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during property unsubscribe')

    @staticmethod
    def decode_property_update_frame(frame: str) -> Tuple[str, any]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY UPDATE' and 'id' in headers and 'value' in headers:
            return headers['id'], headers['value']
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error receiving property update')

    @staticmethod
    def encode_read_datalog_frame(property_id: str, from_: datetime.datetime, to: datetime.datetime, limit: int) -> str:
        frame = f'READ DATALOG\nid:{property_id}\n'
        if from_ is not None and isinstance(from_, datetime.datetime):
            frame += f'from:{from_.replace(microsecond=0).isoformat()}\n'
        if to is not None and isinstance(to, datetime.datetime):
            frame += f'to:{to.replace(microsecond=0).isoformat()}\n'
        if limit is not None:
            frame += f''
        frame += '\n'
        return frame

    @staticmethod
    def decode_datalog_read_frame(frame: str) -> Tuple[str, str, int, str]:
        command, headers, body = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'DATALOG READ' and 'status' in headers and 'id' in headers and 'count' in headers:
            return headers['status'], headers['id'], int(headers['count']), body
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error receiving property update')

    @staticmethod
    def encode_read_messages_frame(from_: datetime.datetime, to: datetime.datetime, limit: int) -> str:
        frame = f'READ MESSAGES\n'
        if from_ is not None and isinstance(from_, datetime.datetime):
            frame += f'from:{from_.replace(microsecond=0).isoformat()}\n'
        if to is not None and isinstance(to, datetime.datetime):
            frame += f'to:{to.replace(microsecond=0).isoformat()}\n'
        if limit is not None:
            frame += f'limit:{limit}'
        frame += '\n'
        return frame

    @staticmethod
    def decode_messages_read_frame(frame: str) -> Tuple[str, int, list]:
        command, headers, body = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'MESSAGES READ' and 'status' in headers and 'count' in headers:
            status = headers['status']
            if status == 'Success':
                messages = json.loads(body)
                if isinstance(messages, list):
                    for message in messages:
                        if 'timestamp' in message:
                            message['timestamp'] = datetime.datetime.fromisoformat(message['timestamp'])
                return status, headers['count'], messages
            else:
                return status, headers['count'], []
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during description')

    @staticmethod
    def decode_device_message_frame(frame: str) -> Tuple[str, str, str]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'DEVICE MESSAGE' and 'access_id' in headers and 'device_id' in headers and 'message_id' in headers and 'message' in headers:
            return f'{headers["access_id"]}.{headers["device.id"]}', headers['message_id'], headers['message']
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error receiving device message')

    @staticmethod
    def peek_frame_command(frame: str) -> str:
        return frame[:frame.index('\n')]

    @staticmethod
    def decode_frame(frame: str) -> Tuple[str, dict, str]:
        command = 'INVALID'
        headers = {}

        lines = frame.split('\n')
        if len(lines) >= 1:
            command = lines[0]

        line = 1
        while lines[line] and line < len(lines):
            components = lines[line].split(':')
            if len(components) == 2:
                headers[components[0]] = components[1]
            line += 1
        line += 1

        body = '\n'.join(lines[line:])

        return command, headers, body


class SIGatewayClient(_SIAbstractGatewayClient):
    """
    Simple, synchronous (blocking) OpenStuder gateway client.

    This client uses a synchronous model which has the advantage to be much simpler to use than the asynchronous version. The drawback is that device message indications are
    ignored by this client and subscriptions to property changes are not possible.
    """

    def __init__(self):
        super().__init__()
        self.__state: SIConnectionState = SIConnectionState.DISCONNECTED
        self.__ws: Optional[websocket.WebSocket] = None
        self.__access_level: SIAccessLevel = SIAccessLevel.NONE
        self.__gateway_version: str = ''

    def connect(self, host: str, port: int = None, user: str = None, password: str = None) -> SIAccessLevel:
        """
        Establishes the WebSocket connection to the OpenStuder gateway and executes the user authorization process once the connection has been established. This method blocks the
        current thread until the operation (authorize) has been completed or an error occurred. The method returns the access level granted to the client during authorization on
        success or throws an **SIProtocolError** otherwise.

        :param host: Hostname or IP address of the OpenStuder gateway to connect to.
        :param port: TCP port used for the connection to the OpenStuder gateway, defaults to 1987.
        :param user: Username send to the gateway used for authorization.
        :param password: Password send to the gateway used for authorization.
        :return: Access Level granted to the client.
        :raises SIProtocolError: If the connection could not be established or the authorization was refused.
        """

        # Ensure that the client is in the DISCONNECTED state.
        self.__ensure_in_state(SIConnectionState.DISCONNECTED)

        # Connect to WebSocket server.
        if port is None:
            port = 1987
        self.__state = SIConnectionState.CONNECTING
        self.__ws = websocket.create_connection(f'ws://{host}:{port}')

        # Authorize client.
        self.__state = SIConnectionState.AUTHORIZING
        if user is None or password is None:
            self.__ws.send(super().encode_authorize_frame_without_credentials())
        else:
            self.__ws.send(super().encode_authorize_frame_with_credentials(user, password))
        try:
            self.__access_level, self.__gateway_version = super().decode_authorized_frame(self.__ws.recv())
        except ConnectionRefusedError as exception:
            self.__state = SIConnectionState.DISCONNECTED
            raise SIProtocolError("WebSocket connection refused")

        # Change state to connected.
        self.__state = SIConnectionState.CONNECTED

        # Return access level.
        return self.__access_level

    def state(self) -> SIConnectionState:
        """
        Returns the current state of the client. See **SIConnectionState** for details.

        :return: Current state of the client.
        """

        return self.__state

    def access_level(self) -> SIAccessLevel:
        """
        Return the access level the client has gained on the gateway connected. See **SIAccessLevel** for details.

        :return: Access level granted to client.
        """

        return self.__access_level

    def gateway_version(self) -> str:
        """
        Returns the version of the OpenStuder gateway software running on the host the client is connected to.

        :return: Version of the gateway software.
        """

        return self.__gateway_version

    def enumerate(self) -> Tuple[str, int]:
        """
        Instructs the gateway to scan every configured and functional device access driver for new devices and remove devices that do not respond anymore. Returns the status of
        the operation and the number of devices present.

        :return: Returns two values. 1: operation status, 2: the number of devices present.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send ENUMERATE message to gateway.
        self.__ws.send(super().encode_enumerate_frame())

        # Wait for ENUMERATED message, decode it and return data.
        return super().decode_enumerated_frame(self.__receive_frame_until_commands(['ENUMERATED', 'ERROR']))

    def describe(self, device_access_id: str = None, device_id: str = None, flags: SIDescriptionFlags = None) -> Tuple[str, Optional[str], object]:
        """
        This method can be used to retrieve information about the available devices and their properties from the connected gateway. Using the optional device_access_id and
        device_id parameters, the method can either request information about the whole topology, a particular device access instance, a device or a property.

        The flags control the level of detail in the gateway's response.

        :param device_access_id: Device access ID for which the description should be retrieved.
        :param device_id: Device ID for which the description should be retrieved.
        :param flags: Flags to control level of detail of the response.
        :return: Status of the operation, the subject id and the description as object.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send DESCRIBE message to gateway.
        self.__ws.send(super().encode_describe_frame(device_access_id, device_id, flags))

        # Wait for DESCRIPTION message, decode it and return data.
        return super().decode_description_frame(self.__receive_frame_until_commands(['DESCRIPTION', 'ERROR']))

    def read_property(self, property_id: str) -> Tuple[str, str, Optional[any]]:
        """
        This method is used to retrieve the actual value of a given property from the connected gateway. The property is identified by the property_id parameter.

        :param property_id: The ID of the property to read in the form '{device access ID}.{device ID}.{property ID}'.
        :return: Status of the read operation, the ID of the property actually read and the value.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send READ PROPERTY message to gateway.
        self.__ws.send(super().encode_read_property_frame(property_id))

        # Wait for PROPERTY READ message, decode it and return data.
        return super().decode_property_read_frame(self.__receive_frame_until_commands(['PROPERTY READ', 'ERROR']))

    def write_property(self, property_id: str, value: any = None) -> Tuple[str, str]:
        """
        The write_property method message is used to change the actual value of a given property. The property is identified by the property_id parameter and the new value is
        passed by the value optional value parameter.

        This value parameter is optional as it is possible to write to properties with the data type "Signal" where there is no actual value written, the write operation rather
        triggers an action on the device.

        :param property_id: The ID of the property to write in the form '{device access ID}.{<device ID}.{<property ID}'.
        :param value: Optional value to write.
        :return: Status of the write operation and the ID of the property.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send WRITE PROPERTY message to gateway.
        self.__ws.send(super().encode_write_property_frame(property_id, value))

        # Wait for PROPERTY WRITTEN message, decode it and return data.
        return super().decode_property_written_frame(self.__receive_frame_until_commands(['PROPERTY WRITTEN', 'ERROR']))

    def read_datalog(self, property_id: str, from_: datetime.datetime = None, to: datetime.datetime = None, limit: int = None) -> Tuple[str, str, int, str]:
        """
        This method is used to retrieve all or a subset of logged data of a given property from the gateway.

        :param property_id: Global ID of the property for which the logged data should be retrieved. It has to be in the form '{device access ID}.{device ID}.{property ID}'.
        :param from_: Optional date and time from which the data has to be retrieved, Defaults to the begin of time.
        :param to: Optional date and time to which the data has to be retrieved, Defaults to the current time on the gateway.
        :param limit: Using this optional parameter you can limit the number of results retrieved in total.
        :return: Status of the operation, id of the property, number of entries, Properties data in CSV format whereas the first column is the date and time in ISO 8601 extended
        format and the second column contains the actual values.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send READ DATALOG message to gateway.
        self.__ws.send(super().encode_read_datalog_frame(property_id, from_, to, limit))

        # Wait for DATALOG READ message, decode it and return data.
        return super().decode_datalog_read_frame(self.__receive_frame_until_commands(['DATALOG READ', 'ERROR']))

    def read_messages(self, from_: datetime.datetime = None, to: datetime.datetime = None, limit: int = None) -> Tuple[str, int, object]:
        """
        The read_messages method can be used to retrieve all or a subset of stored messages send by devices on all buses in the past from the gateway.

        :param from_: Optional date and time from which the messages have to be retrieved, Defaults to the begin of time.
        :param to: Optional date and time to which the messages have to be retrieved, Defaults to the current time on the gateway.
        :param limit: Using this optional parameter you can limit the number of messages retrieved in total.
        :return: Returns the status of the operation, the number of messages and the list of all messages.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send READ MESSAGES message to gateway.
        self.__ws.send(super().encode_read_messages_frame(from_, to, limit))

        # Wait for MESSAGES READ message, decode it and return data.
        return super().decode_messages_read_frame(self.__receive_frame_until_commands(['MESSAGES READ', 'ERROR']))

    def disconnect(self) -> None:
        """
        Disconnects the client from the gateway.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Change state to disconnected.
        self.__state = SIConnectionState.DISCONNECTED

        # Close the WebSocket
        self.__ws.close()

    def __ensure_in_state(self, state: SIConnectionState) -> None:
        if self.__state != state:
            raise SIProtocolError("invalid client state")

    def __receive_frame_until_commands(self, commands: list) -> str:
        while True:
            frame = self.__ws.recv()
            if super().peek_frame_command(frame) in commands:
                return frame


class SIAsyncGatewayClient(_SIAbstractGatewayClient):
    """
    Complete, asynchronous (non-blocking) OpenStuder gateway client.

    This client uses an asynchronous model which has the disadvantage to be a bit harder to use than the synchronous version. The advantages are that long operations do not block
    the main thread as all results are reported using callbacks, device message indications are supported and subscriptions to property changes are possible.
    """

    def __init__(self):
        super().__init__()
        self.__state: SIConnectionState = SIConnectionState.DISCONNECTED
        self.__ws: Optional[websocket.WebSocketApp] = None
        self.__thread: Optional[Thread] = None
        self.__access_level: SIAccessLevel = SIAccessLevel.NONE
        self.__gateway_version: str = ''

        self.__user: Optional[str] = None
        self.__password: Optional[str] = None

        # General callbacks.
        self.on_connected: Optional[Callable[[SIAccessLevel, str], None]] = None
        """
        This callback is called once the connection to the gateway could be established and the user has been successfully authorized.

        The callback takes two arguments:
        
        - The first parameter is the access level that was granted to the user during authorization.
        - The second parameter is the version of the OpenStuder software running on the gateway.
        """

        self.on_disconnected: Optional[Callable[[], None]] = None
        """
        Called when the connection to the OpenStuder gateway has been gracefully closed by either side or the connection was lost by any other reason.
        
        The callback has no parameters.
        """

        self.on_error: Optional[Callable[[Exception], None]] = None
        # TODO: Continue documentation.

        self.on_enumerated: Optional[Callable[[str, int], None]] = None
        self.on_description: Optional[Callable[[str, Optional[str], object], None]] = None
        self.on_property_read: Optional[Callable[[str, str, Optional[any]], None]] = None
        self.on_property_written: Optional[Callable[[str, str], None]] = None
        self.on_property_subscribed: Optional[Callable[[str, str], None]] = None
        self.on_property_unsubscribed: Optional[Callable[[str, str], None]] = None
        self.on_property_updated: Optional[Callable[[str, any], None]] = None
        self.on_datalog_read: Optional[Callable[[str, str, int, str], None]] = None
        self.on_device_message: Optional[Callable[[str, str, str], None]] = None
        self.on_messages_read: Optional[Callable[[str, Optional[int], Optional[object]], None]] = None

    def connect(self, host: str, user: str = None, password: str = None, background: bool = True) -> None:
        self.__ensure_in_state(SIConnectionState.DISCONNECTED)
        self.__user = user
        self.__password = password
        self.__state = SIConnectionState.CONNECTING
        self.__ws = websocket.WebSocketApp(f'ws://{host}:1987',
                                           on_open=self.__on_open,
                                           on_message=self.__on_message,
                                           on_error=self.__on_error,
                                           on_close=self.__on_close
                                           )
        if background:
            self.__thread = Thread(target=self.__ws.run_forever)
            self.__thread.setDaemon(True)
            self.__thread.start()
        else:
            self.__ws.run_forever()

    def set_callbacks(self, callbacks) -> None:
        if isinstance(callbacks, SIAsyncGatewayClientCallbacks):
            self.on_connected = callbacks.on_connected
            self.on_disconnected = callbacks.on_disconnected
            self.on_error = callbacks.on_error
            self.on_enumerated = callbacks.on_enumerated
            self.on_description = callbacks.on_description
            self.on_property_read = callbacks.on_property_read
            self.on_property_written = callbacks.on_property_written
            self.on_property_subscribed = callbacks.on_property_subscribed
            self.on_property_unsubscribed = callbacks.on_property_unsubscribed
            self.on_property_updated = callbacks.on_property_updated
            self.on_datalog_read = callbacks.on_datalog_read
            self.on_device_message = callbacks.on_device_message
            self.on_messages_read = callbacks.on_messages_read

    def state(self) -> SIConnectionState:
        return self.__state

    def access_level(self) -> SIAccessLevel:
        return self.__access_level

    def gateway_version(self) -> str:
        return self.__gateway_version

    def enumerate(self) -> None:
        self.__ensure_in_state(SIConnectionState.CONNECTED)
        self.__ws.send(super().encode_enumerate_frame())

    def describe(self, device_access_id: str = None, device_id: str = None, flags: SIDescriptionFlags = None) -> None:
        self.__ensure_in_state(SIConnectionState.CONNECTED)
        self.__ws.send(super().encode_describe_frame(device_access_id, device_id, flags))

    def read_property(self, property_id: str) -> None:
        self.__ensure_in_state(SIConnectionState.CONNECTED)
        self.__ws.send(super().encode_read_property_frame(property_id))

    def write_property(self, property_id: str, value: any = None) -> None:
        self.__ensure_in_state(SIConnectionState.CONNECTED)
        self.__ws.send(super().encode_write_property_frame(property_id, value))

    def subscribe_to_property(self, property_id: str) -> None:
        self.__ensure_in_state(SIConnectionState.CONNECTED)
        self.__ws.send(super().encode_subscribe_property_frame(property_id))

    def unsubscribe_from_property(self, property_id: str) -> None:
        self.__ensure_in_state(SIConnectionState.CONNECTED)
        self.__ws.send(super().encode_unsubscribe_property_frame(property_id))

    def read_datalog(self, property_id: str, from_: datetime.datetime = None, to: datetime.datetime = None, limit: int = None) -> None:
        self.__ensure_in_state(SIConnectionState.CONNECTED)
        self.__ws.send(super().encode_read_datalog_frame(property_id, from_, to, limit))

    def read_messages(self, from_: datetime.datetime = None, to: datetime.datetime = None, limit: int = None) -> None:
        self.__ensure_in_state(SIConnectionState.CONNECTED)
        self.__ws.send(super().encode_read_messages_frame(from_, to, limit))

    def disconnect(self) -> None:
        self.__ensure_in_state(SIConnectionState.CONNECTED)
        self.__ws.close()

    def __ensure_in_state(self, state: SIConnectionState) -> None:
        if self.__state != state:
            raise SIProtocolError("invalid client state")

    def __on_open(self) -> None:
        self.__state = SIConnectionState.AUTHORIZING
        if self.__user is None or self.__password is None:
            self.__ws.send(super().encode_authorize_frame_without_credentials())
        else:
            self.__ws.send(super().encode_authorize_frame_with_credentials(self.__user, self.__password))

    def __on_message(self, frame: str) -> None:
        command = super().peek_frame_command(frame)

        try:
            if self.__state == SIConnectionState.AUTHORIZING:
                self.__access_level, self.__gateway_version = super().decode_authorized_frame(frame)
                self.__state = SIConnectionState.CONNECTED
                if callable(self.on_connected):
                    self.on_connected(self.__access_level, self.__gateway_version)
            else:
                if command == 'ERROR':
                    if callable(self.on_error):
                        _, headers, _ = super().decode_frame(frame)
                        self.on_error(SIProtocolError(headers['reason']))
                elif command == 'ENUMERATED':
                    status, device_count = super().decode_enumerated_frame(frame)
                    if callable(self.on_enumerated):
                        self.on_enumerated(status, device_count)
                elif command == 'DESCRIPTION':
                    status, id_, description = super().decode_description_frame(frame)
                    if callable(self.on_description):
                        self.on_description(status, id_, description)
                elif command == 'PROPERTY READ':
                    status, id_, value = super().decode_property_read_frame(frame)
                    if callable(self.on_property_read):
                        self.on_property_read(status, id_, value)
                elif command == 'PROPERTY WRITTEN':
                    status, id_ = super().decode_property_written_frame(frame)
                    if callable(self.on_property_written):
                        self.on_property_written(status, id_)
                elif command == 'PROPERTY SUBSCRIBED':
                    status, id_ = super().decode_property_subscribed_frame(frame)
                    if callable(self.on_property_subscribed):
                        self.on_property_subscribed(status, id_)
                elif command == 'PROPERTY UNSUBSCRIBED':
                    status, id_ = super().decode_property_unsubscribed_frame(frame)
                    if callable(self.on_property_unsubscribed):
                        self.on_property_unsubscribed(status, id_)
                elif command == 'PROPERTY UPDATE':
                    id_, value = super().decode_property_update_frame(frame)
                    if callable(self.on_property_updated):
                        self.on_property_updated(id_, value)
                elif command == 'DATALOG READ':
                    status, id_, count, values = super().decode_datalog_read_frame(frame)
                    if callable(self.on_datalog_read):
                        self.on_datalog_read(status, id_, count, values)
                elif command == 'DEVICE MESSAGE':
                    id_, message_id, frame = super().decode_device_message_frame(frame)
                    if callable(self.on_device_message):
                        self.on_device_message(id_, message_id, frame)
                elif command == 'MESSAGES READ':
                    status, count, messages = super().decode_messages_read_frame(frame)
                    if callable(self.on_messages_read):
                        self.on_messages_read(status, count, messages)
                else:
                    if callable(self.on_error):
                        self.on_error(SIProtocolError(f'unsupported frame command: {command}'))
        except SIProtocolError as error:
            if callable(self.on_error):
                self.on_error(error)

    def __on_error(self, error: Exception) -> None:
        if callable(self.on_error):
            self.on_error(error)

    def __on_close(self) -> None:
        self.__state = SIConnectionState.DISCONNECTED
        self.__access_level = SIAccessLevel.NONE
        if callable(self.on_disconnected):
            self.on_disconnected()
        self.__thread.join()


class SIAsyncGatewayClientCallbacks:
    def on_connected(self, access_level: SIAccessLevel, gateway_version: str) -> None:
        pass

    def on_disconnected(self) -> None:
        pass

    def on_error(self, reason) -> None:
        pass

    def on_enumerated(self, status: str, device_count: int) -> None:
        pass

    def on_description(self, status: str, id_: Optional[str], description: object) -> None:
        pass

    def on_property_read(self, status: str, property_id: str, value: Optional[any]) -> None:
        pass

    def on_property_written(self, status: str, property_id: str) -> None:
        pass

    def on_property_subscribed(self, status: str, property_id: str) -> None:
        pass

    def on_property_unsubscribed(self, status: str, property_id: str) -> None:
        pass

    def on_property_updated(self, property_id: str, value: any) -> None:
        pass

    def on_datalog_read(self, status: str, property_id: str, count: int, values: str) -> None:
        pass

    def on_device_message(self, id_: str, message_id: str, message: str) -> None:
        pass

    def on_messages_read(self, status: str, count: int, messages: list) -> None:
        pass
