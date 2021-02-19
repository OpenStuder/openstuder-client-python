from __future__ import annotations
from typing import Callable, Optional, Tuple, List
from enum import Enum, Flag, auto
from threading import Thread
import datetime
import json
import websocket


class SIStatus(Enum):
    """
    Status of operations on the OpenStuder gateway.

    - **SIStatus.SUCCESS**: Operation was successfully completed.
    - **SIStatus.IN_PROGRESS**: Operation is already in progress or another operation is occupying the resource.
    - **SIStatus.ERROR**: General (unspecified) error.
    - **SIStatus.NO_PROPERTY**: The property does not exist or the user's access level does not allow to access the property.
    - **SIStatus.NO_DEVICE**: The device does not exist.
    - **SIStatus.NO_DEVICE_ACCESS**: The device access instance does not exist.
    - **SIStatus.TIMEOUT**: A timeout occurred when waiting for the completion of the operation.
    - **SIStatus.INVALID_VALUE**: A invalid value was passed.
    """

    SUCCESS = 0
    IN_PROGRESS = 1
    ERROR = -1
    NO_PROPERTY = -2
    NO_DEVICE = -3
    NO_DEVICE_ACCESS = -4
    TIMEOUT = -5
    INVALID_VALUE = -6

    @staticmethod
    def from_string(string: str) -> SIStatus:
        if string == 'Success':
            return SIStatus.SUCCESS
        elif string == 'InProgress':
            return SIStatus.IN_PROGRESS
        elif string == 'Error':
            return SIStatus.ERROR
        elif string == 'NoProperty':
            return SIStatus.NO_PROPERTY
        elif string == 'NoDevice':
            return SIStatus.NO_DEVICE
        elif string == 'NoDeviceAccess':
            return SIStatus.NO_DEVICE_ACCESS
        elif string == 'Timeout':
            return SIStatus.TIMEOUT
        elif string == 'InvalidValue':
            return SIStatus.INVALID_VALUE
        else:
            return SIStatus.ERROR


class SIConnectionState(Enum):
    """
    State of the connection to the OpenStuder gateway.

    - **SIConnectionState.DISCONNECTED**: The client is not connected.
    - **SIConnectionState.CONNECTING**: The client is establishing the WebSocket connection to the gateway.
    - **SIConnectionState.AUTHORIZING**: The WebSocket connection to the gateway has been established and the client is authorizing.
    - **SIConnectionState.CONNECTED**: The WebSocket connection is established and the client is authorized, ready to use.
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
    - **QUALIFIED_SERVICE_PERSONNEL**: Expert and all configuration and service properties only for qualified service personnel.
    """

    NONE = 0
    BASIC = auto()
    INSTALLER = auto()
    EXPERT = auto()
    QUALIFIED_SERVICE_PERSONNEL = auto()

    @staticmethod
    def from_string(string: str) -> SIAccessLevel:
        if string == 'None':
            return SIAccessLevel.NONE
        elif string == 'Basic':
            return SIAccessLevel.BASIC
        elif string == 'Installer':
            return SIAccessLevel.INSTALLER
        elif string == 'Expert':
            return SIAccessLevel.EXPERT
        elif string == 'QSP':
            return SIAccessLevel.QUALIFIED_SERVICE_PERSONNEL
        else:
            return SIAccessLevel.NONE


class SIDescriptionFlags(Flag):
    """
    Flags to control the format of the **DESCRIBE** functionality.

    - **SIDescriptionFlags.NONE**: No description flags.
    - **SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION**: Includes device access instances information.
    - **SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION**: Include device information.
    - **SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION**: Include device property information.
    - **SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION**: Include device access driver information.
    """

    NONE = 0
    INCLUDE_ACCESS_INFORMATION = auto()
    INCLUDE_DEVICE_INFORMATION = auto()
    INCLUDE_PROPERTY_INFORMATION = auto()
    INCLUDE_DRIVER_INFORMATION = auto()


class SIWriteFlags(Flag):
    """
        Flags to control write property operation.

        - **SIWriteFlags.NONE**: No write flags.
        - **SIWriteFlags.PERMANENT**: Write the change to the persistent storage, eg the change lasts reboots.
        """

    NONE = 0
    PERMANENT = auto()


class SIProtocolError(IOError):
    """
    Class for reporting all OpenStuder protocol errors.
    """

    def __init__(self, message):
        super(SIProtocolError, self).__init__(message)

    def reason(self) -> str:
        """
        Returns the actual reason for the error.

        :return: Reason for the error.
        """
        return super(SIProtocolError, self).args[0]


class SIDeviceMessage:
    """
    The SIDeviceMessage class represents a message a device connected to the OpenStuder gateway has broadcast.
    """
    def __init__(self, access_id: str, device_id: str, message_id: str, message: str, timestamp: datetime.datetime):
        self.timestamp = timestamp
        """
        Timestamp when the device message was received by the gateway.
        """

        self.access_id = access_id
        """
        ID of the device access driver that received the message.
        """

        self.device_id = device_id
        """
        ID of the device that broadcast the message.
        """

        self.message_id = message_id
        """
        Message ID.
        """

        self.message = message
        """
        String representation of the message.
        """

    @staticmethod
    def from_dict(d: dict) -> SIDeviceMessage:
        return SIDeviceMessage(d['access_id'], d['device_id'], d['message_id'], d['message'], datetime.datetime.fromisoformat(d['timestamp']))


class _SIAbstractGatewayClient:
    def __init__(self):
        super(_SIAbstractGatewayClient, self).__init__()

    @staticmethod
    def encode_authorize_frame_without_credentials() -> str:
        return 'AUTHORIZE\nprotocol_version:1\n\n'

    @staticmethod
    def encode_authorize_frame_with_credentials(user: str, password: str) -> str:
        return 'AUTHORIZE\nuser:{user}\npassword:{password}\nprotocol_version:1\n\n'.format(user=user, password=password)

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
        return 'ENUMERATE\n\n'

    @staticmethod
    def decode_enumerated_frame(frame: str) -> Tuple[SIStatus, int]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'ENUMERATED' and 'status' in headers and 'device_count' in headers:
            return SIStatus.from_string(headers['status']), int(headers['device_count'])
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during device enumeration')

    @staticmethod
    def encode_describe_frame(device_access_id: Optional[str], device_id: Optional[str], property_id: Optional[int], flags: Optional[SIDescriptionFlags]) -> str:
        frame = 'DESCRIBE\n'
        if device_access_id is not None:
            frame += 'id:{device_access_id}'.format(device_access_id=device_access_id)
            if device_id is not None:
                frame += '.{device_id}'.format(device_id=device_id)
                if property_id is not None:
                    frame += '.{property_id}'.format(property_id=property_id)
            frame += '\n'
        if flags is not None and isinstance(flags, SIDescriptionFlags):
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
        frame += '\n'
        return frame

    @staticmethod
    def decode_description_frame(frame: str) -> Tuple[SIStatus, Optional[str], object]:
        command, headers, body = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'DESCRIPTION' and 'status' in headers:
            status = SIStatus.from_string(headers['status'])
            if status == SIStatus.SUCCESS:
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
        return 'READ PROPERTY\nid:{property_id}\n\n'.format(property_id=property_id)

    @staticmethod
    def decode_property_read_frame(frame: str) -> Tuple[SIStatus, str, Optional[any]]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY READ' and 'status' in headers and 'id' in headers:
            status = SIStatus.from_string(headers['status'])
            if status == SIStatus.SUCCESS and 'value' in headers:
                try:
                    value = float(headers['value'])
                except ValueError:
                    string = headers['value'].lower()
                    if string == 'true':
                        value = True
                    elif string == 'false':
                        value = False
                    else:
                        value = string
                return status, headers['id'], value
            else:
                return status, headers['id'], None
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during property read')

    @staticmethod
    def encode_write_property_frame(property_id: str, value: Optional[any], flags: Optional[SIWriteFlags]) -> str:
        frame = 'WRITE PROPERTY\nid:{property_id}\n'.format(property_id=property_id)
        if flags is not None and isinstance(flags, SIWriteFlags):
            frame += 'flags:'
            if flags & SIWriteFlags.PERMANENT:
                frame += 'Permanent'
            frame += '\n'
        if value is not None:
            frame += 'value:{value}\n'.format(value=value)
        frame += '\n'
        return frame

    @staticmethod
    def decode_property_written_frame(frame: str) -> Tuple[SIStatus, str]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY WRITTEN' and 'status' in headers and 'id' in headers:
            return SIStatus.from_string(headers['status']), headers['id']
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during property write')

    @staticmethod
    def encode_subscribe_property_frame(property_id: str) -> str:
        return 'SUBSCRIBE PROPERTY\nid:{property_id}\n\n'.format(property_id=property_id)

    @staticmethod
    def decode_property_subscribed_frame(frame: str) -> Tuple[SIStatus, str]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY SUBSCRIBED' and 'status' in headers and 'id' in headers:
            return SIStatus.from_string(headers['status']), headers['id']
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during property subscribe')

    @staticmethod
    def encode_unsubscribe_property_frame(property_id: str) -> str:
        return 'UNSUBSCRIBE PROPERTY\nid:{property_id}\n\n'.format(property_id=property_id)

    @staticmethod
    def decode_property_unsubscribed_frame(frame: str) -> Tuple[SIStatus, str]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY UNSUBSCRIBED' and 'status' in headers and 'id' in headers:
            return SIStatus.from_string(headers['status']), headers['id']
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during property unsubscribe')

    @staticmethod
    def decode_property_update_frame(frame: str) -> Tuple[str, any]:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'PROPERTY UPDATE' and 'id' in headers and 'value' in headers:
            try:
                value = float(headers['value'])
            except ValueError:
                string = headers['value'].lower()
                if string == 'true':
                    value = True
                elif string == 'false':
                    value = False
                else:
                    value = string
            return headers['id'], value
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error receiving property update')

    @staticmethod
    def encode_read_datalog_frame(property_id: str, from_: Optional[datetime.datetime], to: Optional[datetime.datetime], limit: Optional[int]) -> str:
        frame = 'READ DATALOG\nid:{property_id}\n'.format(property_id=property_id)
        frame += _SIAbstractGatewayClient.get_timestamp_header_if_present('from', from_)
        frame += _SIAbstractGatewayClient.get_timestamp_header_if_present('to', to)
        if limit is not None:
            frame += 'limit:{limit}\n'.format(limit=limit)
        frame += '\n'
        return frame

    @staticmethod
    def decode_datalog_read_frame(frame: str) -> Tuple[SIStatus, str, int, str]:
        command, headers, body = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'DATALOG READ' and 'status' in headers and 'id' in headers and 'count' in headers:
            return SIStatus.from_string(headers['status']), headers['id'], int(headers['count']), body
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error receiving datalog read')

    @staticmethod
    def encode_read_messages_frame(from_: Optional[datetime.datetime], to: Optional[datetime.datetime], limit: Optional[int]) -> str:
        frame = 'READ MESSAGES\n'
        frame += _SIAbstractGatewayClient.get_timestamp_header_if_present('from', from_)
        frame += _SIAbstractGatewayClient.get_timestamp_header_if_present('to', to)
        if limit is not None:
            frame += 'limit:{limit}\n'.format(limit=limit)
        frame += '\n'
        return frame

    @staticmethod
    def decode_messages_read_frame(frame: str) -> Tuple[SIStatus, int, List[SIDeviceMessage]]:
        command, headers, body = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'MESSAGES READ' and 'status' in headers and 'count' in headers:
            status = SIStatus.from_string(headers['status'])
            if status == SIStatus.SUCCESS:
                messages = json.loads(body, object_hook=SIDeviceMessage.from_dict)
                return status, int(headers['count']), messages
            else:
                return status, int(headers['count']), []
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error during description')

    @staticmethod
    def decode_device_message_frame(frame: str) -> SIDeviceMessage:
        command, headers, _ = _SIAbstractGatewayClient.decode_frame(frame)
        if command == 'DEVICE MESSAGE' and 'access_id' in headers and 'device_id' in headers and 'message_id' in headers and 'message' in headers and 'timestamp' in headers:
            return SIDeviceMessage.from_dict(headers)
        elif command == 'ERROR':
            raise SIProtocolError(headers['reason'])
        else:
            raise SIProtocolError('unknown error receiving device message')

    @staticmethod
    def peek_frame_command(frame: str) -> str:
        return frame[:frame.index('\n')]

    @staticmethod
    def decode_frame(frame: str) -> Tuple[str, dict, str]:
        lines = frame.split('\n')

        if len(lines) < 2:
            raise SIProtocolError('invalid frame')

        command = lines[0]

        line = 1
        headers = {}
        while line < len(lines) and lines[line]:
            components = lines[line].split(':')
            if len(components) >= 2:
                headers[components[0]] = ':'.join(components[1:])
            line += 1
        line += 1

        if line >= len(lines):
            raise SIProtocolError('invalid frame')

        body = '\n'.join(lines[line:])

        return command, headers, body

    @staticmethod
    def get_timestamp_header_if_present(key: str, timestamp: Optional[datetime.datetime]):
        if timestamp is not None and isinstance(timestamp, datetime.datetime):
            return '{key}:{timestamp}\n'.format(key=key, timestamp=timestamp.replace(microsecond=0).isoformat())
        else:
            return ''


class SIGatewayClient(_SIAbstractGatewayClient):
    """
    Simple, synchronous (blocking) OpenStuder gateway client.

    This client uses a synchronous model which has the advantage to be much simpler to use than the asynchronous version SIAsyncGatewayClient. The drawback is that device message
    indications are ignored by this client and subscriptions to property changes are not possible.
    """

    def __init__(self):
        super(SIGatewayClient, self).__init__()
        self.__state: SIConnectionState = SIConnectionState.DISCONNECTED
        self.__ws: Optional[websocket.WebSocket] = None
        self.__access_level: SIAccessLevel = SIAccessLevel.NONE
        self.__gateway_version: str = ''

    def connect(self, host: str, port: int = 1987, user: str = None, password: str = None) -> SIAccessLevel:
        """
        Establishes the WebSocket connection to the OpenStuder gateway and executes the user authorization process once the connection has been established. This method blocks the
        current thread until the operation (authorize) has been completed or an error occurred. The method returns the access level granted to the client during authorization on
        success or throws an **SIProtocolError** otherwise.

        :param host: Hostname or IP address of the OpenStuder gateway to connect to.
        :param port: TCP port used for the connection to the OpenStuder gateway, defaults to 1987.
        :param user: Username send to the gateway used for authorization.
        :param password: Password send to the gateway used for authorization.
        :return: Access Level granted to the client.
        :raises SIProtocolError: If the connection could not be established, or the authorization was refused.
        """

        # Ensure that the client is in the DISCONNECTED state.
        self.__ensure_in_state(SIConnectionState.DISCONNECTED)

        # Connect to WebSocket server.
        self.__state = SIConnectionState.CONNECTING
        self.__ws = websocket.create_connection('ws://{host}:{port}'.format(host=host, port=port))

        # Authorize client.
        self.__state = SIConnectionState.AUTHORIZING
        if user is None or password is None:
            self.__ws.send(super(SIGatewayClient, self).encode_authorize_frame_without_credentials())
        else:
            self.__ws.send(super(SIGatewayClient, self).encode_authorize_frame_with_credentials(user, password))
        try:
            self.__access_level, self.__gateway_version = super(SIGatewayClient, self).decode_authorized_frame(self.__ws.recv())
        except ConnectionRefusedError:
            self.__state = SIConnectionState.DISCONNECTED
            raise SIProtocolError('WebSocket connection refused')

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

    def enumerate(self) -> Tuple[SIStatus, int]:
        """
        Instructs the gateway to scan every configured and functional device access driver for new devices and remove devices that do not respond anymore. Returns the status of
        the operation, and the number of devices present.

        :return: Returns two values. 1: operation status, 2: the number of devices present.
        :raises SIProtocolError: On a connection, protocol of framing error.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send ENUMERATE message to gateway.
        self.__ws.send(super(SIGatewayClient, self).encode_enumerate_frame())

        # Wait for ENUMERATED message, decode it and return data.
        return super(SIGatewayClient, self).decode_enumerated_frame(self.__receive_frame_until_commands(['ENUMERATED', 'ERROR']))

    def describe(self, device_access_id: str = None, device_id: str = None, property_id: int = None, flags: SIDescriptionFlags = None) -> Tuple[SIStatus, Optional[str], object]:
        """
        This method can be used to retrieve information about the available devices and their properties from the connected gateway. Using the optional device_access_id,
        device_id and property_id parameters, the method can either request information about the whole topology, a particular device access instance, a device or a property.

        The flags control the level of detail in the gateway's response.

        :param device_access_id: Device access ID for which the description should be retrieved.
        :param device_id: Device ID for which the description should be retrieved. Note that device_access_id must be present too.
        :param property_id: Property ID for which the description should be retrieved. Note that device_access_id and device_id must be present too.
        :param flags: Flags to control level of detail of the response.
        :return: Returns three values. 1: Status of the operation, 2: the subject's id, 3: the description object.
        :raises SIProtocolError: On a connection, protocol of framing error.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send DESCRIBE message to gateway.
        self.__ws.send(super(SIGatewayClient, self).encode_describe_frame(device_access_id, device_id, property_id, flags))

        # Wait for DESCRIPTION message, decode it and return data.
        return super(SIGatewayClient, self).decode_description_frame(self.__receive_frame_until_commands(['DESCRIPTION', 'ERROR']))

    def read_property(self, property_id: str) -> Tuple[SIStatus, str, Optional[any]]:
        """
        This method is used to retrieve the actual value of a given property from the connected gateway. The property is identified by the property_id parameter.

        :param property_id: The ID of the property to read in the form '{device access ID}.{device ID}.{property ID}'.
        :return: Returns three values: 1: Status of the read operation, 2: the ID of the property read, 3: the value read.
        :raises SIProtocolError: On a connection, protocol of framing error.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send READ PROPERTY message to gateway.
        self.__ws.send(super(SIGatewayClient, self).encode_read_property_frame(property_id))

        # Wait for PROPERTY READ message, decode it and return data.
        return super(SIGatewayClient, self).decode_property_read_frame(self.__receive_frame_until_commands(['PROPERTY READ', 'ERROR']))

    def write_property(self, property_id: str, value: any = None, flags: SIWriteFlags = None) -> Tuple[SIStatus, str]:
        """
        The write_property method is used to change the actual value of a given property. The property is identified by the property_id parameter and the new value is passed by the
        optional value parameter.

        This value parameter is optional as it is possible to write to properties with the data type "Signal" where there is no actual value written, the write operation rather
        triggers an action on the device.

        :param property_id: The ID of the property to write in the form '{device access ID}.{<device ID}.{<property ID}'.
        :param value: Optional value to write.
        :param flags: Write flags, See SIWriteFlags for details, if not provided the flags are not send by the client, and the gateway uses the default flags
                      (SIWriteFlags.PERMANENT).
        :return: Returns two values: 1: Status of the write operation, 2: the ID of the property written.
        :raises SIProtocolError: On a connection, protocol of framing error.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send WRITE PROPERTY message to gateway.
        self.__ws.send(super(SIGatewayClient, self).encode_write_property_frame(property_id, value, flags))

        # Wait for PROPERTY WRITTEN message, decode it and return data.
        return super(SIGatewayClient, self).decode_property_written_frame(self.__receive_frame_until_commands(['PROPERTY WRITTEN', 'ERROR']))

    def read_datalog_csv(self, property_id: str, from_: datetime.datetime = None, to: datetime.datetime = None, limit: int = None) -> Tuple[SIStatus, str, int, str]:
        """
        This method is used to retrieve all or a subset of logged data of a given property from the gateway.

        :param property_id: Global ID of the property for which the logged data should be retrieved. It has to be in the form '{device access ID}.{device ID}.{property ID}'.
        :param from_: Optional date and time from which the data has to be retrieved, defaults to the oldest value logged.
        :param to: Optional date and time to which the data has to be retrieved, defaults to the current time on the gateway.
        :param limit: Using this optional parameter you can limit the number of results retrieved in total.
        :return: Returns four values: 1: Status of the operation, 2: id of the property, 3: number of entries, 4: Properties data in CSV format whereas the first column is the
        date and time in ISO 8601 extended format, and the second column contains the actual values.
        :raises SIProtocolError: On a connection, protocol of framing error.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send READ DATALOG message to gateway.
        self.__ws.send(super(SIGatewayClient, self).encode_read_datalog_frame(property_id, from_, to, limit))

        # Wait for DATALOG READ message, decode it and return data.
        return super(SIGatewayClient, self).decode_datalog_read_frame(self.__receive_frame_until_commands(['DATALOG READ', 'ERROR']))

    def read_messages(self, from_: datetime.datetime = None, to: datetime.datetime = None, limit: int = None) -> Tuple[SIStatus, int, List[SIDeviceMessage]]:
        """
        The read_messages() method can be used to retrieve all or a subset of stored messages send by devices on all buses in the past from the gateway.

        :param from_: Optional date and time from which the messages have to be retrieved, defaults to the oldest message saved.
        :param to: Optional date and time to which the messages have to be retrieved, defaults to the current time on the gateway.
        :param limit: Using this optional parameter you can limit the number of messages retrieved in total.
        :return: Returns three values. 1: the status of the operation, 2: the number of messages, 3: the list of retrieved messages.
        :raises SIProtocolError: On a connection, protocol of framing error.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send READ MESSAGES message to gateway.
        self.__ws.send(super(SIGatewayClient, self).encode_read_messages_frame(from_, to, limit))

        # Wait for MESSAGES READ message, decode it and return data.
        return super(SIGatewayClient, self).decode_messages_read_frame(self.__receive_frame_until_commands(['MESSAGES READ', 'ERROR']))

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
            if super(SIGatewayClient, self).peek_frame_command(frame) in commands:
                return frame


class SIAsyncGatewayClientCallbacks:
    """
    Base class containing all callback methods that can be called by the SIAsyncGatewayClient. You can use this as your base class and register it using
    IAsyncGatewayClient.set_callbacks().
    """

    def on_connected(self, access_level: SIAccessLevel, gateway_version: str) -> None:
        """
        This method is called once the connection to the gateway could be established and the user has been successfully authorized.

        :param access_level: Access level that was granted to the user during authorization.
        :param gateway_version: Version of the OpenStuder software running on the gateway.
        """
        pass

    def on_disconnected(self) -> None:
        """
        Called when the connection to the OpenStuder gateway has been gracefully closed by either side or the connection was lost by any other reason.
        """
        pass

    def on_error(self, reason) -> None:
        """
        Called on severe errors.

        :param reason: Exception that caused the erroneous behavior.
        """
        pass

    def on_enumerated(self, status: SIStatus, device_count: int) -> None:
        """
        Called when the enumeration operation started using enumerate() has completed on the gateway.

        The callback takes two arguments. 1: , 2: the .
        :param status: Operation status.
        :param device_count: Number of devices present.
        """
        pass

    def on_description(self, status: SIStatus, id_: Optional[str], description: object) -> None:
        """
        Called when the gateway returned the description requested using the describe() method.

        :param status: Status of the operation.
        :param id_: Subject's ID.
        :param description: Description object.
        """
        pass

    def on_property_read(self, status: SIStatus, property_id: str, value: Optional[any]) -> None:
        """
        Called when the property read operation started using read_property() has completed on the gateway.

        :param status: Status of the read operation.
        :param property_id: ID of the property read.
        :param value: The value read.
        """
        pass

    def on_property_written(self, status: SIStatus, property_id: str) -> None:
        """
        Called when the property write operation started using write_property() has completed on the gateway.

        :param status: Status of the write operation.
        :param property_id: ID of the property written.
        """
        pass

    def on_property_subscribed(self, status: SIStatus, property_id: str) -> None:
        """
        Called when the gateway returned the status of the property subscription requested using the property_subscribe() method.

        :param status: The status of the subscription.
        :param property_id: ID of the property.
        """
        pass

    def on_property_unsubscribed(self, status: SIStatus, property_id: str) -> None:
        """
        Called when the gateway returned the status of the property unsubscription requested using the property_unsubscribe() method.

        :param status: The status of the unsubscription.
        :param property_id: ID of the property.
        """
        pass

    def on_property_updated(self, property_id: str, value: any) -> None:
        """
        This callback is called whenever the gateway send a property update.

        :param property_id: ID of the updated property.
        :param value: The current value of the property.
        """
        pass

    def on_datalog_read_csv(self, status: SIStatus, property_id: str, count: int, values: str) -> None:
        """
        Called when the datalog read operation started using read_datalog() has completed on the gateway. This version of the method returns the data in CSV format suitable to
        be written to a file.

        :param status: Status of the operation.
        :param property_id: ID of the property.
        :param count: Number of entries.
        :param values: Properties data in CSV format whereas the first column is the date and time in ISO 8601 extended format and the second column contains the actual values.
        """
        pass

    def on_device_message(self, message: SIDeviceMessage) -> None:
        """
        This callback is called whenever the gateway send a device message indication.

        :param message: The device message received.
        """
        pass

    def on_messages_read(self, status: SIStatus, count: int, messages: List[SIDeviceMessage]) -> None:
        """
        Called when the gateway returned the status of the read messages operation using the read_messages() method.

        :param status: The status of the operation.
        :param count: Number of messages retrieved.
        :param messages: List of retrieved messages.
        """
        pass


class SIAsyncGatewayClient(_SIAbstractGatewayClient):
    """
    Complete, asynchronous (non-blocking) OpenStuder gateway client.

    This client uses an asynchronous model which has the disadvantage to be a bit harder to use than the synchronous version. The advantages are that long operations do not block
    the main thread as all results are reported using callbacks, device message indications are supported and subscriptions to property changes are possible.
    """

    def __init__(self):
        super(SIAsyncGatewayClient, self).__init__()
        self.__state: SIConnectionState = SIConnectionState.DISCONNECTED
        self.__ws: Optional[websocket.WebSocketApp] = None
        self.__thread: Optional[Thread] = None
        self.__access_level: SIAccessLevel = SIAccessLevel.NONE
        self.__gateway_version: str = ''

        self.__user: Optional[str] = None
        self.__password: Optional[str] = None

        self.on_connected: Optional[Callable[[SIAccessLevel, str], None]] = None
        """
        This callback is called once the connection to the gateway could be established and the user has been successfully authorized.

        The callback takes two arguments. 1: the access level that was granted to the user during authorization, 2: the version of the OpenStuder software running on the gateway.
        """

        self.on_disconnected: Optional[Callable[[], None]] = None
        """
        Called when the connection to the OpenStuder gateway has been gracefully closed by either side or the connection was lost by any other reason.
        
        This callback has no parameters.
        """

        self.on_error: Optional[Callable[[Exception], None]] = None
        """
        Called on severe errors.
        
        The single parameter passed to the callback is the exception that caused the erroneous behavior.
        """

        self.on_enumerated: Optional[Callable[[str, int], None]] = None
        """
        Called when the enumeration operation started using enumerate() has completed on the gateway.
        
        The callback takes two arguments. 1: operation status, 2: the number of devices present.
        """

        self.on_description: Optional[Callable[[str, Optional[str], object], None]] = None
        """
        Called when the gateway returned the description requested using the describe() method.
        
        The callback takes three parameters: 1: Status of the operation, 2: the subject's ID, 3: the description object.
        """

        self.on_property_read: Optional[Callable[[str, str, Optional[any]], None]] = None
        """
        Called when the property read operation started using read_property() has completed on the gateway.
        
        The callback takes three parameters: 1: Status of the read operation, 2: the ID of the property read, 3: the value read.
        """

        self.on_property_written: Optional[Callable[[str, str], None]] = None
        """
        Called when the property write operation started using write_property() has completed on the gateway.
        
        The callback takes two parameters: 1: Status of the write operation, 2: the ID of the property written.
        """

        self.on_property_subscribed: Optional[Callable[[str, str], None]] = None
        """
        Called when the gateway returned the status of the property subscription requested using the property_subscribe() method.
        
        The callback takes two parameters: 1: The status of the subscription, 2: The ID of the property.
        """

        self.on_property_unsubscribed: Optional[Callable[[str, str], None]] = None
        """
        Called when the gateway returned the status of the property unsubscription requested using the property_unsubscribe() method.

        The callback takes two parameters: 1: The status of the unsubscription, 2: The ID of the property.
        """

        self.on_property_updated: Optional[Callable[[str, any], None]] = None
        """
        This callback is called whenever the gateway send a property update.
        
        The callback takes two parameters: 1: the ID of the property that has updated, 2: the actual value.
        """

        self.on_datalog_read_csv: Optional[Callable[[str, str, int, str], None]] = None
        """
        Called when the datalog read operation started using read_datalog() has completed on the gateway. This version of the callback returns the data in CSV format suitable to 
        be written to a file.
        
        The callback takes four parameters: 1: Status of the operation, 2: ID of the property, 3: number of entries, 4: properties data in CSV format whereas the first column is
        the date and time in ISO 8601 extended format and the second column contains the actual values.
        """

        self.on_device_message: Optional[Callable[[SIDeviceMessage], None]] = None
        """
        This callback is called whenever the gateway send a device message indication.
        
        The callback takes one parameter, the device message object.
        """

        self.on_messages_read: Optional[Callable[[str, Optional[int], List[SIDeviceMessage]], None]] = None
        """
        Called when the gateway returned the status of the read messages operation using the read_messages() method.

        The callback takes three parameters: 1: the status of the operation, 2: the number of messages retrieved, 3: the list of retrieved messages.
        """

    def connect(self, host: str, port: int = 1987, user: str = None, password: str = None, background: bool = True) -> None:
        """
        Establishes the WebSocket connection to the OpenStuder gateway and executes the user authorization process once the connection has been established in the background. This
        method returns immediately and does not block the current thread.

        The status of the connection attempt is reported either by the on_connected() callback on success or the on_error() callback if the connection could not be established
        or the authorisation for the given user was rejected by the gateway.

        :param host: Hostname or IP address of the OpenStuder gateway to connect to.
        :param port: TCP port used for the connection to the OpenStuder gateway, defaults to 1987.
        :param user: Username send to the gateway used for authorization.
        :param password: Password send to the gateway used for authorization.
        :param background: If true, the handling of the WebSocket connection is done in the background, if false the current thread is took over.
        :raises SIProtocolError: If there was an error initiating the WebSocket connection.
        """

        # Ensure that the client is in the DISCONNECTED state.
        self.__ensure_in_state(SIConnectionState.DISCONNECTED)

        # Save parameter for later use.
        self.__user = user
        self.__password = password

        # Connect to WebSocket server.
        self.__state = SIConnectionState.CONNECTING
        self.__ws = websocket.WebSocketApp('ws://{host}:{port}'.format(host=host, port=port),
                                           on_open=self.__on_open,
                                           on_message=self.__on_message,
                                           on_error=self.__on_error,
                                           on_close=self.__on_close
                                           )

        # If background mode is selected, start a daemon thread for the connection handling, otherwise take over current thread.
        if background:
            self.__thread = Thread(target=self.__ws.run_forever)
            self.__thread.setDaemon(True)
            self.__thread.start()
        else:
            self.__ws.run_forever()

    def set_callbacks(self, callbacks: SIAsyncGatewayClientCallbacks) -> None:
        """
        Configures the client to use all callbacks of the passed abstract client callback class. Using this you can set all callbacks to be called on the given object and avoid
         having to set each callback individually.

        :param callbacks: Object derived from SIAsyncGatewayClientCallbacks to be used for all callbacks.
        """
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
            self.on_datalog_read_csv = callbacks.on_datalog_read_csv
            self.on_device_message = callbacks.on_device_message
            self.on_messages_read = callbacks.on_messages_read

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

    def enumerate(self) -> None:
        """
        Instructs the gateway to scan every configured and functional device access driver for new devices and remove devices that do not respond anymore.

        The status of the operation and the number of devices present are reported using the on_enumerated() callback.

        :raises SIProtocolError: If the client is not connected or not yet authorized.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send ENUMERATE message to gateway.
        self.__ws.send(super(SIAsyncGatewayClient, self).encode_enumerate_frame())

    def describe(self, device_access_id: str = None, device_id: str = None, property_id: int = None, flags: SIDescriptionFlags = None) -> None:
        """
        This method can be used to retrieve information about the available devices and their properties from the connected gateway. Using the optional device_access_id,
        device_id and property_id parameters, the method can either request information about the whole topology, a particular device access instance, a device or a property.

        The flags control the level of detail in the gateway's response.

        The description is reported using the on_description() callback.

        :param device_access_id: Device access ID for which the description should be retrieved.
        :param device_id: Device ID for which the description should be retrieved. Note that device_access_id must be present too.
        :param property_id: Property ID for which the description should be retrieved. Note that device_access_id and device_id must be present too.
        :param flags: Flags to control level of detail of the response.
        :raises SIProtocolError: If the client is not connected or not yet authorized.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send DESCRIBE message to gateway.
        self.__ws.send(super(SIAsyncGatewayClient, self).encode_describe_frame(device_access_id, device_id, property_id, flags))

    def read_property(self, property_id: str) -> None:
        """
        This method is used to retrieve the actual value of a given property from the connected gateway. The property is identified by the property_id parameter.

        The status of the read operation and the actual value of the property are reported using the on_property_read() callback.

        :param property_id: The ID of the property to read in the form '{device access ID}.{device ID}.{property ID}'.
        :raises SIProtocolError: If the client is not connected or not yet authorized.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send READ PROPERTY message to gateway.
        self.__ws.send(super(SIAsyncGatewayClient, self).encode_read_property_frame(property_id))

    def write_property(self, property_id: str, value: any = None, flags: SIWriteFlags = None) -> None:
        """
        The write_property method is used to change the actual value of a given property. The property is identified by the property_id parameter and the new value is passed by the
        optional value parameter.

        This value parameter is optional as it is possible to write to properties with the data type "Signal" where there is no actual value written, the write operation rather
        triggers an action on the device.

        The status of the write operation is reported using the on_property_written() callback.

        :param property_id: The ID of the property to write in the form '{device access ID}.{<device ID}.{<property ID}'.
        :param value: Optional value to write.
        :param flags: Write flags, See SIWriteFlags for details, if not provided the flags are not send by the client and the gateway uses the default flags
                      (SIWriteFlags.PERMANENT).
        :raises SIProtocolError: If the client is not connected or not yet authorized.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send WRITE PROPERTY message to gateway.
        self.__ws.send(super(SIAsyncGatewayClient, self).encode_write_property_frame(property_id, value, flags))

    def subscribe_to_property(self, property_id: str) -> None:
        """
        This method can be used to subscribe to a property on the connected gateway. The property is identified by the property_id parameter.

        The status of the subscribe request is reported using the on_property_subscribed() callback.

        :param property_id: The ID of the property to subscribe to in the form '{device access ID}.{device ID}.{property ID}'.
        :raises SIProtocolError: If the client is not connected or not yet authorized.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send SUBSCRIBE PROPERTY message to gateway.
        self.__ws.send(super(SIAsyncGatewayClient, self).encode_subscribe_property_frame(property_id))

    def unsubscribe_from_property(self, property_id: str) -> None:
        """
        This method can be used to unsubscribe from a property on the connected gateway. The property is identified by the property_id parameter.

        The status of the unsubscribe request is reported using the on_property_unsubscribed() callback.

        :param property_id: The ID of the property to unsubscribe from in the form '{device access ID}.{device ID}.{property ID}'.
        :raises SIProtocolError: If the client is not connected or not yet authorized.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send UNSUBSCRIBE PROPERTY message to gateway.
        self.__ws.send(super(SIAsyncGatewayClient, self).encode_unsubscribe_property_frame(property_id))

    def read_datalog(self, property_id: str, from_: datetime.datetime = None, to: datetime.datetime = None, limit: int = None) -> None:
        """
        This method is used to retrieve all or a subset of logged data of a given property from the gateway.

        The status of this operation and the respective values are reported using the on_datalog_read_csv() callback.

        :param property_id: Global ID of the property for which the logged data should be retrieved. It has to be in the form '{device access ID}.{device ID}.{property ID}'.
        :param from_: Optional date and time from which the data has to be retrieved, defaults to the oldest value logged.
        :param to: Optional date and time to which the data has to be retrieved, defaults to the current time on the gateway.
        :param limit: Using this optional parameter you can limit the number of results retrieved in total.
        :raises SIProtocolError: If the client is not connected or not yet authorized.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send READ DATALOG message to gateway.
        self.__ws.send(super(SIAsyncGatewayClient, self).encode_read_datalog_frame(property_id, from_, to, limit))

    def read_messages(self, from_: datetime.datetime = None, to: datetime.datetime = None, limit: int = None) -> None:
        """
        The read_messages method can be used to retrieve all or a subset of stored messages send by devices on all buses in the past from the gateway.

        The status of this operation and the retrieved messages are reported using the on_messages_read() callback.

        :param from_: Optional date and time from which the messages have to be retrieved, defaults to the oldest message saved.
        :param to: Optional date and time to which the messages have to be retrieved, defaults to the current time on the gateway.
        :param limit: Using this optional parameter you can limit the number of messages retrieved in total.
        :raises SIProtocolError: If the client is not connected or not yet authorized.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Encode and send READ MESSAGES message to gateway.
        self.__ws.send(super(SIAsyncGatewayClient, self).encode_read_messages_frame(from_, to, limit))

    def disconnect(self) -> None:
        """
        Disconnects the client from the gateway.
        """

        # Ensure that the client is in the CONNECTED state.
        self.__ensure_in_state(SIConnectionState.CONNECTED)

        # Close the WebSocket
        self.__ws.close()

    def __ensure_in_state(self, state: SIConnectionState) -> None:
        if self.__state != state:
            raise SIProtocolError("invalid client state")

    def __on_open(self) -> None:
        # Change state to AUTHORIZING.
        self.__state = SIConnectionState.AUTHORIZING

        # Encode and send AUTHORIZE message to gateway.
        if self.__user is None or self.__password is None:
            self.__ws.send(super(SIAsyncGatewayClient, self).encode_authorize_frame_without_credentials())
        else:
            self.__ws.send(super(SIAsyncGatewayClient, self).encode_authorize_frame_with_credentials(self.__user, self.__password))

    def __on_message(self, frame: str) -> None:

        # Determine the actual command.
        command = super(SIAsyncGatewayClient, self).peek_frame_command(frame)

        try:
            # In AUTHORIZE state we only handle AUTHORIZED messages.
            if self.__state == SIConnectionState.AUTHORIZING:
                self.__access_level, self.__gateway_version = super(SIAsyncGatewayClient, self).decode_authorized_frame(frame)

                # Change state to CONNECTED.
                self.__state = SIConnectionState.CONNECTED

                # Call callback if present.
                if callable(self.on_connected):
                    self.on_connected(self.__access_level, self.__gateway_version)

            # In CONNECTED state we handle all messages except the AUTHORIZED message.
            else:
                if command == 'ERROR':
                    if callable(self.on_error):
                        _, headers, _ = super(SIAsyncGatewayClient, self).decode_frame(frame)
                        self.on_error(SIProtocolError(headers['reason']))
                elif command == 'ENUMERATED':
                    status, device_count = super(SIAsyncGatewayClient, self).decode_enumerated_frame(frame)
                    if callable(self.on_enumerated):
                        self.on_enumerated(status, device_count)
                elif command == 'DESCRIPTION':
                    status, id_, description = super(SIAsyncGatewayClient, self).decode_description_frame(frame)
                    if callable(self.on_description):
                        self.on_description(status, id_, description)
                elif command == 'PROPERTY READ':
                    status, id_, value = super(SIAsyncGatewayClient, self).decode_property_read_frame(frame)
                    if callable(self.on_property_read):
                        self.on_property_read(status, id_, value)
                elif command == 'PROPERTY WRITTEN':
                    status, id_ = super(SIAsyncGatewayClient, self).decode_property_written_frame(frame)
                    if callable(self.on_property_written):
                        self.on_property_written(status, id_)
                elif command == 'PROPERTY SUBSCRIBED':
                    status, id_ = super(SIAsyncGatewayClient, self).decode_property_subscribed_frame(frame)
                    if callable(self.on_property_subscribed):
                        self.on_property_subscribed(status, id_)
                elif command == 'PROPERTY UNSUBSCRIBED':
                    status, id_ = super(SIAsyncGatewayClient, self).decode_property_unsubscribed_frame(frame)
                    if callable(self.on_property_unsubscribed):
                        self.on_property_unsubscribed(status, id_)
                elif command == 'PROPERTY UPDATE':
                    id_, value = super(SIAsyncGatewayClient, self).decode_property_update_frame(frame)
                    if callable(self.on_property_updated):
                        self.on_property_updated(id_, value)
                elif command == 'DATALOG READ':
                    status, id_, count, values = super(SIAsyncGatewayClient, self).decode_datalog_read_frame(frame)
                    if callable(self.on_datalog_read_csv):
                        self.on_datalog_read_csv(status, id_, count, values)
                elif command == 'DEVICE MESSAGE':
                    message = super(SIAsyncGatewayClient, self).decode_device_message_frame(frame)
                    if callable(self.on_device_message):
                        self.on_device_message(message)
                elif command == 'MESSAGES READ':
                    status, count, messages = super(SIAsyncGatewayClient, self).decode_messages_read_frame(frame)
                    if callable(self.on_messages_read):
                        self.on_messages_read(status, count, messages)
                else:
                    if callable(self.on_error):
                        self.on_error(SIProtocolError('unsupported frame command: {command}'.format(command=command)))
        except SIProtocolError as error:
            if callable(self.on_error):
                self.on_error(error)

    def __on_error(self, error: Exception) -> None:
        if callable(self.on_error):
            self.on_error(SIProtocolError(error.args[1]))

    def __on_close(self) -> None:
        # Change state to DISCONNECTED.
        self.__state = SIConnectionState.DISCONNECTED

        # Change access level to NONE.
        self.__access_level = SIAccessLevel.NONE

        # Call callback.
        if callable(self.on_disconnected):
            self.on_disconnected()

        # Wait for the end of the thread.
        self.__thread.join()
