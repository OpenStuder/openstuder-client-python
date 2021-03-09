import datetime
import random
import string
import unittest
# noinspection PyProtectedMember
from openstuder import _SIAbstractGatewayClient, SIAccessLevel, SIStatus, SIDescriptionFlags, SIWriteFlags, SIProtocolError


def random_int(start: int, end: int) -> int:
    return random.randint(start, end)


def random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length))


class AUTHORIZEFrame(unittest.TestCase):
    def test_encode_without_credentials(self):
        frame = _SIAbstractGatewayClient.encode_authorize_frame_without_credentials()
        self.assertEqual('AUTHORIZE\nprotocol_version:1\n\n', frame)

    def test_encode_with_credentials(self):
        for _ in range(1000):
            user = random_string(random_int(3, 32))
            password = random_string(random_int(1, 64))
            frame = _SIAbstractGatewayClient.encode_authorize_frame_with_credentials(user, password)
            self.assertEqual(f'AUTHORIZE\nuser:{user}\npassword:{password}\nprotocol_version:1\n\n', frame)


class AUTHORIZEDFrame(unittest.TestCase):
    def test_decode_basic(self):
        access_level, gateway_version = _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:Basic\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        self.assertEqual(SIAccessLevel.BASIC, access_level)
        self.assertEqual('0.0.0.348734', gateway_version)

    def test_decode_installer(self):
        access_level, gateway_version = _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:Installer\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        self.assertEqual(SIAccessLevel.INSTALLER, access_level)
        self.assertEqual('0.0.0.348734', gateway_version)

    def test_decode_expert(self):
        access_level, gateway_version = _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:Expert\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        self.assertEqual(SIAccessLevel.EXPERT, access_level)
        self.assertEqual('0.0.0.348734', gateway_version)

    def test_decode_qsp(self):
        access_level, gateway_version = _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:QSP\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        self.assertEqual(SIAccessLevel.QUALIFIED_SERVICE_PERSONNEL, access_level)
        self.assertEqual('0.0.0.348734', gateway_version)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_authorized_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZE\naccess_level:Basic\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:Basic\nprotocol_version:1\ngateway_version:0.0.0.348734\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:Basic\ngateway_version:0.0.0.348734\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:Basic\nprotocol_version:1\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\n\n')


class ENUMERATEFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractGatewayClient.encode_enumerate_frame()
        self.assertEqual('ENUMERATE\n\n', frame)


class ENUMERATEDFrame(unittest.TestCase):
    def test_decode_success(self):
        for count in range(1000):
            status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:Success\ndevice_count:{count}\n\n')
            self.assertEqual(SIStatus.SUCCESS, status)
            self.assertEqual(count, device_count)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_enumerated_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_enumerated_frame('ENUMRATED\nstatus:Success\ndevice_count:3\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_enumerated_frame('ENUMERATED\nstatus:Success\ndevice_count:3\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_enumerated_frame('ENUMERATED\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_enumerated_frame('ENUMERATED')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_enumerated_frame('ENUMERATED\ndevice_count:3\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_enumerated_frame('ENUMERATED\nstatus:Success\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_enumerated_frame('ENUMERATED\n\n')

    def test_decode_in_progress(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:InProgress\ndevice_count:0\n\n')
        self.assertEqual(SIStatus.IN_PROGRESS, status)
        self.assertEqual(0, device_count)

    def test_decode_error(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:Error\ndevice_count:0\n\n')
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual(0, device_count)

    def test_decode_no_property(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:NoProperty\ndevice_count:0\n\n')
        self.assertEqual(SIStatus.NO_PROPERTY, status)
        self.assertEqual(0, device_count)

    def test_decode_no_device(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:NoDevice\ndevice_count:0\n\n')
        self.assertEqual(SIStatus.NO_DEVICE, status)
        self.assertEqual(0, device_count)

    def test_decode_no_device_access(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:NoDeviceAccess\ndevice_count:0\n\n')
        self.assertEqual(SIStatus.NO_DEVICE_ACCESS, status)
        self.assertEqual(0, device_count)

    def test_decode_timeout(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:Timeout\ndevice_count:0\n\n')
        self.assertEqual(SIStatus.TIMEOUT, status)
        self.assertEqual(0, device_count)

    def test_decode_invalid_value(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:InvalidValue\ndevice_count:0\n\n')
        self.assertEqual(SIStatus.INVALID_VALUE, status)
        self.assertEqual(0, device_count)


class DESCRIBEFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, None)
        self.assertEqual('DESCRIBE\n\n', frame)

    def test_encode_with_access_id(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            frame = _SIAbstractGatewayClient.encode_describe_frame(access_id, None, None, None)
            self.assertEqual(f'DESCRIBE\nid:{access_id}\n\n', frame)

    def test_encode_with_device_id(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            device_id = random_string(random_int(3, 32))
            frame = _SIAbstractGatewayClient.encode_describe_frame(access_id, device_id, None, None)
            self.assertEqual(f'DESCRIBE\nid:{access_id}.{device_id}\n\n', frame)

    def test_encode_with_property_id(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            device_id = random_string(random_int(3, 32))
            property_id = random_int(0, 32000)
            frame = _SIAbstractGatewayClient.encode_describe_frame(access_id, device_id, property_id, None)
            self.assertEqual(f'DESCRIBE\nid:{access_id}.{device_id}.{property_id}\n\n', frame)

    def test_encode_with_flags(self):
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeAccessInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeDeviceInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludePropertyInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeDriverInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeAccessInformation,IncludeDeviceInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeAccessInformation,IncludePropertyInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeAccessInformation,IncludeDriverInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeDeviceInformation,IncludePropertyInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION | SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeDeviceInformation,IncludeDriverInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION | SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludePropertyInformation,IncludeDriverInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION |
                                                               SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeAccessInformation,IncludeDeviceInformation,IncludePropertyInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION |
                                                               SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeAccessInformation,IncludeDeviceInformation,IncludeDriverInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION |
                                                               SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeAccessInformation,IncludePropertyInformation,IncludeDriverInformation\n\n', frame)
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION |
                                                               SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual('DESCRIBE\nflags:IncludeDeviceInformation,IncludePropertyInformation,IncludeDriverInformation\n\n', frame)

    def test_encode_complete(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            device_id = random_string(random_int(3, 32))
            property_id = random_int(0, 32000)
            frame = _SIAbstractGatewayClient.encode_describe_frame(access_id, device_id, property_id, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION)
            self.assertEqual(f'DESCRIBE\nid:{access_id}.{device_id}.{property_id}\nflags:IncludeDeviceInformation\n\n', frame)


class DESCRIPTIONFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Success\n\n{"a": "b"}')
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertIsNone(id_)
        self.assertEqual({"a": "b"}, body)

    def test_decode_error(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Error\n\n')
        self.assertEqual(SIStatus.ERROR, status)
        self.assertIsNone(id_)
        self.assertEqual({}, body)

    def test_decode_with_access_id_success(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Success\nid:demo\n\n{"a": "b"}')
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo', id_)
        self.assertEqual({"a": "b"}, body)

    def test_decode_with_access_id_error(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Error\nid:demo\n\n')
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo', id_)
        self.assertEqual({}, body)

    def test_decode_with_device_id_success(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Success\nid:demo.inv\n\n{"a": "b"}')
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.inv', id_)
        self.assertEqual({"a": "b"}, body)

    def test_decode_with_device_id_error(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Error\nid:demo.bat\n\n')
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.bat', id_)
        self.assertEqual({}, body)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_description_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_description_frame('DSCRIPTION\nstatus:Success\n\n{"a": "b"}')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Success\n{"a": "b"}')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Success\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\n\n{"a": "b"}')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION')


class READPROPERTYFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractGatewayClient.encode_read_property_frame('demo.inv.3136')
        self.assertEqual('READ PROPERTY\nid:demo.inv.3136\n\n', frame)


class PROPERTYREADFrame(unittest.TestCase):
    def test_decode_success_float(self):
        result = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Success\nid:demo.inv.3136\nvalue:0.123\n\n')
        self.assertEqual(SIStatus.SUCCESS, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertEqual(0.123, result.value)

    def test_decode_success_false(self):
        result = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Success\nid:demo.inv.3136\nvalue:false\n\n')
        self.assertEqual(SIStatus.SUCCESS, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertEqual(False, result.value)

    def test_decode_success_true(self):
        result = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Success\nid:demo.inv.3136\nvalue:true\n\n')
        self.assertEqual(SIStatus.SUCCESS, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertEqual(True, result.value)

    def test_decode_error(self):
        result = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Error\nid:demo.inv.3136\n\n')
        self.assertEqual(SIStatus.ERROR, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_no_property(self):
        result = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:NoProperty\nid:demo.inv.3136\n\n')
        self.assertEqual(SIStatus.NO_PROPERTY, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_no_device(self):
        result = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:NoDevice\nid:demo.inv.3136\n\n')
        self.assertEqual(SIStatus.NO_DEVICE, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_no_device_access(self):
        result = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:NoDeviceAccess\nid:demo.inv.3136\n\n')
        self.assertEqual(SIStatus.NO_DEVICE_ACCESS, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_timeout(self):
        result = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Timeout\nid:demo.inv.3136\n\n')
        self.assertEqual(SIStatus.TIMEOUT, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_property_read_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_read_frame('PROPRTY READ\nstatus:Success\nid:demo.inv.3136\nvalue:0.123\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Success\nid:demo.inv.3136\nvalue:0.123\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Success\nvalue:0.123\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nid:demo.inv.3136\nvalue:0.123\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nvalue:0.123\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ')


class READPROPERTIESFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractGatewayClient.encode_read_properties_frame(['demo.inv.3136', 'demo.inv.3137'])
        self.assertEqual('READ PROPERTIES\n\n["demo.inv.3136", "demo.inv.3137"]', frame)


class PROPERTIESREADFrame(unittest.TestCase):
    def test_decode_success_float(self):
        results = _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"status": "Success", "id": "demo.inv.3136", "value": 0.123}]')
        self.assertEqual(1, len(results))
        self.assertEqual(SIStatus.SUCCESS, results[0].status)
        self.assertEqual('demo.inv.3136', results[0].id)
        self.assertEqual(0.123, results[0].value)

    def test_decode_success_false(self):
        results = _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"status": "Success", "id": "demo.inv.3136", "value": false}]')
        self.assertEqual(1, len(results))
        self.assertEqual(SIStatus.SUCCESS, results[0].status)
        self.assertEqual('demo.inv.3136', results[0].id)
        self.assertEqual(False, results[0].value)

    def test_decode_success_true(self):
        results = _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"status": "Success", "id": "demo.inv.3136", "value": true}]')
        self.assertEqual(1, len(results))
        self.assertEqual(SIStatus.SUCCESS, results[0].status)
        self.assertEqual('demo.inv.3136', results[0].id)
        self.assertEqual(True, results[0].value)

    def test_decode_error(self):
        results = _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"status": "Error", "id": "demo.inv.3136"}]')
        self.assertEqual(1, len(results))
        self.assertEqual(SIStatus.ERROR, results[0].status)
        self.assertEqual('demo.inv.3136', results[0].id)
        self.assertIsNone(results[0].value)

    def test_decode_no_property(self):
        results = _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"status": "NoProperty", "id": "demo.inv.3136"}]')
        self.assertEqual(1, len(results))
        self.assertEqual(SIStatus.NO_PROPERTY, results[0].status)
        self.assertEqual('demo.inv.3136', results[0].id)
        self.assertIsNone(results[0].value)

    def test_decode_no_device(self):
        results = _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"status": "NoDevice", "id": "demo.inv.3136"}]')
        self.assertEqual(1, len(results))
        self.assertEqual(SIStatus.NO_DEVICE, results[0].status)
        self.assertEqual('demo.inv.3136', results[0].id)
        self.assertIsNone(results[0].value)

    def test_decode_no_device_access(self):
        results = _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"status": "NoDeviceAccess", "id": "demo.inv.3136"}]')
        self.assertEqual(1, len(results))
        self.assertEqual(SIStatus.NO_DEVICE_ACCESS, results[0].status)
        self.assertEqual('demo.inv.3136', results[0].id)
        self.assertIsNone(results[0].value)

    def test_decode_timeout(self):
        results = _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"status": "Timeout", "id": "demo.inv.3136"}]')
        self.assertEqual(1, len(results))
        self.assertEqual(SIStatus.TIMEOUT, results[0].status)
        self.assertEqual('demo.inv.3136', results[0].id)
        self.assertIsNone(results[0].value)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_properties_read_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_properties_read_frame('PROPRTIES READ\nstatus:Success\n\n[]')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n[]')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"status": "Success", "value": 0.123}]')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"id": "demo.inv.3136", "value": 0.123}]')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\nstatus:Success\n\n[{"value": 0.123}]')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_properties_read_frame('PROPERTIES READ')


class WRITEPROPERTYFrame(unittest.TestCase):
    def test_encode_without_value(self):
        frame = _SIAbstractGatewayClient.encode_write_property_frame('demo.inv.1415', None, None)
        self.assertEqual('WRITE PROPERTY\nid:demo.inv.1415\n\n', frame)

    def test_encode_with_value(self):
        frame = _SIAbstractGatewayClient.encode_write_property_frame('demo.inv.3333', 42.24, None)
        self.assertEqual('WRITE PROPERTY\nid:demo.inv.3333\nvalue:42.24\n\n', frame)

    def test_encode_with_value_empty_flags(self):
        frame = _SIAbstractGatewayClient.encode_write_property_frame('demo.inv.3333', 42.24, SIWriteFlags.NONE)
        self.assertEqual('WRITE PROPERTY\nid:demo.inv.3333\nflags:\nvalue:42.24\n\n', frame)

    def test_encode_with_value_permanent_flag(self):
        frame = _SIAbstractGatewayClient.encode_write_property_frame('demo.inv.3333', 42.24, SIWriteFlags.PERMANENT)
        self.assertEqual('WRITE PROPERTY\nid:demo.inv.3333\nflags:Permanent\nvalue:42.24\n\n', frame)


class PROPERTYWRITTENFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\nstatus:Success\nid:demo.inv.1399\n\n')
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_error(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\nstatus:Error\nid:demo.inv.1399\n\n')
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_no_property(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\nstatus:NoProperty\nid:demo.inv.1399\n\n')
        self.assertEqual(SIStatus.NO_PROPERTY, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_no_device(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\nstatus:NoDevice\nid:demo.inv.1399\n\n')
        self.assertEqual(SIStatus.NO_DEVICE, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_no_device_access(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\nstatus:NoDeviceAccess\nid:demo.inv.1399\n\n')
        self.assertEqual(SIStatus.NO_DEVICE_ACCESS, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_timeout(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\nstatus:Timeout\nid:demo.inv.1399\n\n')
        self.assertEqual(SIStatus.TIMEOUT, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_property_written_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITEN\nstatus:Success\nid:demo.inv.1399\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\nstatus:Success\nid:demo.inv.1399\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\nstatus:Success\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\nid:demo.inv.1399\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_written_frame('PROPERTY WRITTEN')


class SUBSCRIBEPROPERTYFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractGatewayClient.encode_subscribe_property_frame('demo.bat.7003')
        self.assertEqual('SUBSCRIBE PROPERTY\nid:demo.bat.7003\n\n', frame)


class PROPERTYSUBSCRIBEDFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCRIBED\nstatus:Success\nid:demo.bat.7003\n\n')
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_error(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCRIBED\nstatus:Error\nid:demo.bat.7003\n\n')
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_no_property(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCRIBED\nstatus:NoProperty\nid:demo.bat.7003\n\n')
        self.assertEqual(SIStatus.NO_PROPERTY, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_property_subscribed_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCIBED\nstatus:Success\nid:demo.bat.7003\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCRIBED\nstatus:Success\nid:demo.bat.7003\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCRIBED\nstatus:Success\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCRIBED\nid:demo.bat.7003\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCRIBED\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCRIBED\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_subscribed_frame('PROPERTY SUBSCRIBED')


class PROPERTYUPDATEFrame(unittest.TestCase):
    def test_decode_float(self):
        id_, value = _SIAbstractGatewayClient.decode_property_update_frame('PROPERTY UPDATE\nid:demo.bat.7003\nvalue:3.874\n\n')
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(3.874, value)

    def test_decode_false(self):
        id_, value = _SIAbstractGatewayClient.decode_property_update_frame('PROPERTY UPDATE\nid:demo.bat.7003\nvalue:false\n\n')
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(False, value)

    def test_decode_true(self):
        id_, value = _SIAbstractGatewayClient.decode_property_update_frame('PROPERTY UPDATE\nid:demo.bat.7003\nvalue:true\n\n')
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(True, value)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_property_update_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_update_frame('PROPRTY UPDATE\nid:demo.bat.7003\nvalue:3.874\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_update_frame('PROPERTY UPDATE\nid:demo.bat.7003\nvalue:3.874\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_update_frame('PROPERTY UPDATE\nid:demo.bat.7003\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_update_frame('PROPERTY UPDATE\nvalue:3.874\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_update_frame('PROPERTY UPDATE\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_update_frame('PROPERTY UPDATE\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_update_frame('PROPERTY UPDATE')


class UNSUBSCRIBEPROPERTYFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractGatewayClient.encode_unsubscribe_property_frame('demo.bat.7003')
        self.assertEqual('UNSUBSCRIBE PROPERTY\nid:demo.bat.7003\n\n', frame)


class PROPERTYUNSUBSCRIBEDFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY UNSUBSCRIBED\nstatus:Success\nid:demo.bat.7003\n\n')
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_error(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY UNSUBSCRIBED\nstatus:Error\nid:demo.bat.7003\n\n')
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_no_property(self):
        status, id_ = _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY UNSUBSCRIBED\nstatus:NoProperty\nid:demo.bat.7003\n\n')
        self.assertEqual(SIStatus.NO_PROPERTY, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_property_unsubscribed_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY UNSUBSCIBED\nstatus:Success\nid:demo.bat.7003\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY SUNUBSCRIBED\nstatus:Success\nid:demo.bat.7003\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY UNSUBSCRIBED\nstatus:Success\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY UNSUBSCRIBED\nid:demo.bat.7003\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY UNSUBSCRIBED\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY UNSUBSCRIBED\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_property_unsubscribed_frame('PROPERTY UNSUBSCRIBED')


class READDATALOGFrame(unittest.TestCase):
    def test_encode_minimal(self):
        frame = _SIAbstractGatewayClient.encode_read_datalog_frame('demo.inv.3137', None, None, None)
        self.assertEqual('READ DATALOG\nid:demo.inv.3137\n\n', frame)

    def test_encode_from_date(self):
        frame = _SIAbstractGatewayClient.encode_read_datalog_frame('demo.inv.3137', datetime.datetime(year=1987, month=12, day=19), None, None)
        self.assertEqual('READ DATALOG\nid:demo.inv.3137\nfrom:1987-12-19T00:00:00\n\n', frame)

    def test_encode_from_datetime(self):
        frame = _SIAbstractGatewayClient.encode_read_datalog_frame('demo.inv.3137', datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None, None)
        self.assertEqual('READ DATALOG\nid:demo.inv.3137\nfrom:1987-12-19T13:10:30\n\n', frame)

    def test_encode_to_date(self):
        frame = _SIAbstractGatewayClient.encode_read_datalog_frame('demo.inv.3137', None, datetime.datetime(year=1987, month=12, day=19), None)
        self.assertEqual('READ DATALOG\nid:demo.inv.3137\nto:1987-12-19T00:00:00\n\n', frame)

    def test_encode_to_datetime(self):
        frame = _SIAbstractGatewayClient.encode_read_datalog_frame('demo.inv.3137', None, datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None)
        self.assertEqual('READ DATALOG\nid:demo.inv.3137\nto:1987-12-19T13:10:30\n\n', frame)

    def test_encode_limit(self):
        frame = _SIAbstractGatewayClient.encode_read_datalog_frame('demo.inv.3137', None, None, 42)
        self.assertEqual('READ DATALOG\nid:demo.inv.3137\nlimit:42\n\n', frame)

    def test_encode_from_to(self):
        frame = _SIAbstractGatewayClient.encode_read_datalog_frame('demo.inv.3137', datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30),
                                                                   datetime.datetime(year=1987, month=12, day=20, hour=13, minute=10, second=30), None)
        self.assertEqual('READ DATALOG\nid:demo.inv.3137\nfrom:1987-12-19T13:10:30\nto:1987-12-20T13:10:30\n\n', frame)

    def test_encode_complete(self):
        frame = _SIAbstractGatewayClient.encode_read_datalog_frame('demo.inv.3137', datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30),
                                                                   datetime.datetime(year=1987, month=12, day=20, hour=13, minute=10, second=30), 13)
        self.assertEqual('READ DATALOG\nid:demo.inv.3137\nfrom:1987-12-19T13:10:30\nto:1987-12-20T13:10:30\nlimit:13\n\n', frame)


class DATALOGREADFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_, count, csv = _SIAbstractGatewayClient.decode_datalog_read_frame('DATALOG READ\nstatus:Success\nid:demo.bat.7003\ncount:2\n\n2021-02-07T20:18:00,0.03145\n2021-02-07T20:17:00,0.84634')
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(2, count)
        self.assertEqual('2021-02-07T20:18:00,0.03145\n2021-02-07T20:17:00,0.84634', csv)

    def test_decode_error(self):
        status, id_, count, csv = _SIAbstractGatewayClient.decode_datalog_read_frame('DATALOG READ\nstatus:Error\nid:demo.bat.7003\ncount:0\n\n')
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(0, count)
        self.assertEqual('', csv)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_datalog_read_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_datalog_read_frame('DATLOG READ\nstatus:Success\nid:demo.bat.7003\ncount:2\n\n2021-02-07T20:18:00,0.03145\n2021-02-07T20:17:00,0.84634')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_datalog_read_frame('DATALOG READ\nstatus:Success\nid:demo.bat.7003\ncount:2\n2021-02-07T20:18:00,0.03145\n2021-02-07T20:17:00,0.84634')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_datalog_read_frame('DATALOG READ\nstatus:Success\nid:demo.bat.7003\n\n2021-02-07T20:18:00,0.03145\n2021-02-07T20:17:00,0.84634')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_datalog_read_frame('DATALOG READ\nstatus:Success\ncount:2\n\n2021-02-07T20:18:00,0.03145\n2021-02-07T20:17:00,0.84634')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_datalog_read_frame('DATALOG READ\nid:demo.bat.7003\ncount:2\n\n2021-02-07T20:18:00,0.03145\n2021-02-07T20:17:00,0.84634')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_datalog_read_frame('DATALOG READ\ncount:2\n\n2021-02-07T20:18:00,0.03145\n2021-02-07T20:17:00,0.84634')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_datalog_read_frame('DATALOG READ\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_datalog_read_frame('DATALOG READ\n')


class DEVICEMESSAGEFrame(unittest.TestCase):
    def test_decode(self):
        message = _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\ntimestamp:2020-01-01T00:00:00\naccess_id:A303\ndevice_id:11\nmessage_id:210\nmessage:AUX2 relay deactivation\n\n')
        self.assertEqual(datetime.datetime(year=2020, month=1, day=1), message.timestamp)
        self.assertEqual('A303', message.access_id)
        self.assertEqual('11', message.device_id)
        self.assertEqual('210', message.message_id)
        self.assertEqual('AUX2 relay deactivation', message.message)

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESAGE\ntimestamp:2020-01-01T00:00:00\naccess_id:A303\ndevice_id:11\nmessage_id:210\nmessage:AUX2 relay deactivation\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\ntimestamp:2020-01-01T00:00:00\naccess_id:A303\ndevice_id:11\nmessage_id:210\nmessage:AUX2 relay deactivation\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\ntimestamp:2020-01-01T00:00:00\naccess_id:A303\ndevice_id:11\nmessage_id:210\nmessage:AUX2 relay deactivation')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\naccess_id:A303\ndevice_id:11\nmessage_id:210\nmessage:AUX2 relay deactivation\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\ntimestamp:2020-01-01T00:00:00\ndevice_id:11\nmessage_id:210\nmessage:AUX2 relay deactivation\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\ntimestamp:2020-01-01T00:00:00\naccess_id:A303\nmessage_id:210\nmessage:AUX2 relay deactivation\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\ntimestamp:2020-01-01T00:00:00\naccess_id:A303\ndevice_id:11\nmessage:AUX2 relay deactivation\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\ntimestamp:2020-01-01T00:00:00\naccess_id:A303\ndevice_id:11\nmessage_id:210\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_device_message_frame('DEVICE MESSAGE')


class READMESSAGESFrame(unittest.TestCase):
    def test_encode_minimal(self):
        frame = _SIAbstractGatewayClient.encode_read_messages_frame(None, None, None)
        self.assertEqual('READ MESSAGES\n\n', frame)

    def test_encode_from_date(self):
        frame = _SIAbstractGatewayClient.encode_read_messages_frame(datetime.datetime(year=1987, month=12, day=19), None, None)
        self.assertEqual('READ MESSAGES\nfrom:1987-12-19T00:00:00\n\n', frame)

    def test_encode_from_datetime(self):
        frame = _SIAbstractGatewayClient.encode_read_messages_frame(datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None, None)
        self.assertEqual('READ MESSAGES\nfrom:1987-12-19T13:10:30\n\n', frame)

    def test_encode_to_date(self):
        frame = _SIAbstractGatewayClient.encode_read_messages_frame(None, datetime.datetime(year=1987, month=12, day=19), None)
        self.assertEqual('READ MESSAGES\nto:1987-12-19T00:00:00\n\n', frame)

    def test_encode_to_datetime(self):
        frame = _SIAbstractGatewayClient.encode_read_messages_frame(None, datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None)
        self.assertEqual('READ MESSAGES\nto:1987-12-19T13:10:30\n\n', frame)

    def test_encode_limit(self):
        frame = _SIAbstractGatewayClient.encode_read_messages_frame(None, None, 42)
        self.assertEqual('READ MESSAGES\nlimit:42\n\n', frame)

    def test_encode_from_to(self):
        frame = _SIAbstractGatewayClient.encode_read_messages_frame(datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30),
                                                                   datetime.datetime(year=1987, month=12, day=20, hour=13, minute=10, second=30), None)
        self.assertEqual('READ MESSAGES\nfrom:1987-12-19T13:10:30\nto:1987-12-20T13:10:30\n\n', frame)

    def test_encode_complete(self):
        frame = _SIAbstractGatewayClient.encode_read_messages_frame(datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30),
                                                                   datetime.datetime(year=1987, month=12, day=20, hour=13, minute=10, second=30), 13)
        self.assertEqual('READ MESSAGES\nfrom:1987-12-19T13:10:30\nto:1987-12-20T13:10:30\nlimit:13\n\n', frame)


class MESSAGESREADFrame(unittest.TestCase):
    def test_decode_success(self):
        status, count, messages = _SIAbstractGatewayClient.decode_messages_read_frame("""MESSAGES READ
status:Success
count:2

[
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay activation",
        "message_id": 209,
        "timestamp": "2020-01-01T00:00:00"
    },
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay deactivation",
        "message_id": 210,
        "timestamp": "2020-01-01T00:15:00"
    }
]""")
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual(2, count)
        self.assertEqual(datetime.datetime(year=2020, month=1, day=1), messages[0].timestamp)
        self.assertEqual('demo', messages[0].access_id)
        self.assertEqual('inv', messages[0].device_id)
        self.assertEqual(209, messages[0].message_id)
        self.assertEqual('AUX2 relay activation', messages[0].message)

        self.assertEqual(datetime.datetime(year=2020, month=1, day=1, hour=0, minute=15), messages[1].timestamp)
        self.assertEqual('demo', messages[1].access_id)
        self.assertEqual('inv', messages[1].device_id)
        self.assertEqual(210, messages[1].message_id)
        self.assertEqual('AUX2 relay deactivation', messages[1].message)

    def test_decode_error(self):
        status, count, messages = _SIAbstractGatewayClient.decode_messages_read_frame('MESSAGES READ\nstatus:Error\ncount:0\n\n')
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual(0, count)
        self.assertEqual(0, len(messages))

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractGatewayClient.decode_messages_read_frame('ERROR\nreason:test\n\n')
        self.assertEqual('test', context.exception.reason())

    def test_decode_invalid_frame(self):
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_messages_read_frame("""MESAGES READ
status:Success
count:2

[
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay activation",
        "message_id": 209,
        "timestamp": "2020-01-01T00:00:00"
    },
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay deactivation",
        "message_id": 210,
        "timestamp": "2020-01-01T00:15:00"
    }
]""")
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_messages_read_frame("""MESSAGES READ
count:2

[
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay activation",
        "message_id": 209,
        "timestamp": "2020-01-01T00:00:00"
    },
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay deactivation",
        "message_id": 210,
        "timestamp": "2020-01-01T00:15:00"
    }
]""")
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_messages_read_frame("""MESSAGES READ
status:Success

[
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay activation",
        "message_id": 209,
        "timestamp": "2020-01-01T00:00:00"
    },
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay deactivation",
        "message_id": 210,
        "timestamp": "2020-01-01T00:15:00"
    }
]""")
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_messages_read_frame("""MESSAGES READ

[
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay activation",
        "message_id": 209,
        "timestamp": "2020-01-01T00:00:00"
    },
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay deactivation",
        "message_id": 210,
        "timestamp": "2020-01-01T00:15:00"
    }
]""")
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_messages_read_frame("""MESSAGES READ
status:Success
count:2
[
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay activation",
        "message_id": 209,
        "timestamp": "2020-01-01T00:00:00"
    },
    {
        "access_id": "demo",
        "device_id": "inv",
        "message": "AUX2 relay deactivation",
        "message_id": 210,
        "timestamp": "2020-01-01T00:15:00"
    }
]""")
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_messages_read_frame('MESSAGES READ\n\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_messages_read_frame('MESSAGES READ\n')
        with self.assertRaises(SIProtocolError):
            _SIAbstractGatewayClient.decode_messages_read_frame('MESSAGES READ')


if __name__ == '__main__':
    unittest.main()
