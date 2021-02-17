import random
import string
import unittest
# noinspection PyProtectedMember
from openstuder import _SIAbstractGatewayClient, SIAccessLevel, SIStatus, SIDescriptionFlags


def random_int(start: int, end: int) -> int:
    return random.randint(start, end)


def random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length))


class AUTHORIZEFrame(unittest.TestCase):
    def test_encode_without_credentials(self):
        frame = _SIAbstractGatewayClient.encode_authorize_frame_without_credentials()
        self.assertEqual(frame, 'AUTHORIZE\nprotocol_version:1\n\n')

    def test_encode_with_credentials(self):
        for _ in range(1000):
            user = random_string(random_int(3, 32))
            password = random_string(random_int(1, 64))
            frame = _SIAbstractGatewayClient.encode_authorize_frame_with_credentials(user, password)
            self.assertEqual(frame, f'AUTHORIZE\nuser:{user}\npassword:{password}\nprotocol_version:1\n\n')


class AUTHORIZEDFrame(unittest.TestCase):
    def test_decode_basic(self):
        access_level, gateway_version = _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:Basic\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        self.assertEqual(access_level, SIAccessLevel.BASIC)
        self.assertEqual(gateway_version, '0.0.0.348734')

    def test_decode_installer(self):
        access_level, gateway_version = _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:Installer\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        self.assertEqual(access_level, SIAccessLevel.INSTALLER)
        self.assertEqual(gateway_version, '0.0.0.348734')

    def test_decode_expert(self):
        access_level, gateway_version = _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:Expert\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        self.assertEqual(access_level, SIAccessLevel.EXPERT)
        self.assertEqual(gateway_version, '0.0.0.348734')

    def test_decode_qsp(self):
        access_level, gateway_version = _SIAbstractGatewayClient.decode_authorized_frame('AUTHORIZED\naccess_level:QSP\nprotocol_version:1\ngateway_version:0.0.0.348734\n\n')
        self.assertEqual(access_level, SIAccessLevel.QUALIFIED_SERVICE_PERSONNEL)
        self.assertEqual(gateway_version, '0.0.0.348734')


class ENUMERATEFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractGatewayClient.encode_enumerate_frame()
        self.assertEqual(frame, 'ENUMERATE\n\n')


class ENUMERATEDFrame(unittest.TestCase):
    def test_decode_success(self):
        for count in range(1000):
            status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:Success\ndevice_count:{count}\n\n')
            self.assertEqual(status, SIStatus.SUCCESS)
            self.assertEqual(device_count, count)

    def test_decode_in_progress(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:InProgress\ndevice_count:0\n\n')
        self.assertEqual(status, SIStatus.IN_PROGRESS)
        self.assertEqual(device_count, 0)

    def test_decode_error(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:Error\ndevice_count:0\n\n')
        self.assertEqual(status, SIStatus.ERROR)
        self.assertEqual(device_count, 0)

    def test_decode_no_property(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:NoProperty\ndevice_count:0\n\n')
        self.assertEqual(status, SIStatus.NO_PROPERTY)
        self.assertEqual(device_count, 0)

    def test_decode_no_device(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:NoDevice\ndevice_count:0\n\n')
        self.assertEqual(status, SIStatus.NO_DEVICE)
        self.assertEqual(device_count, 0)

    def test_decode_no_device_access(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:NoDeviceAccess\ndevice_count:0\n\n')
        self.assertEqual(status, SIStatus.NO_DEVICE_ACCESS)
        self.assertEqual(device_count, 0)

    def test_decode_timeout(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:Timeout\ndevice_count:0\n\n')
        self.assertEqual(status, SIStatus.TIMEOUT)
        self.assertEqual(device_count, 0)

    def test_decode_invalid_value(self):
        status, device_count = _SIAbstractGatewayClient.decode_enumerated_frame(f'ENUMERATED\nstatus:InvalidValue\ndevice_count:0\n\n')
        self.assertEqual(status, SIStatus.INVALID_VALUE)
        self.assertEqual(device_count, 0)


class DESCRIBEFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, None)
        self.assertEqual(frame, 'DESCRIBE\n\n')

    def test_encode_with_access_id(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            frame = _SIAbstractGatewayClient.encode_describe_frame(access_id, None, None)
            self.assertEqual(frame, f'DESCRIBE\nid:{access_id}\n\n')

    def test_encode_with_device_id(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            device_id = random_string(random_int(3, 32))
            frame = _SIAbstractGatewayClient.encode_describe_frame(access_id, device_id, None)
            self.assertEqual(frame, f'DESCRIBE\nid:{access_id}.{device_id}\n\n')

    def test_encode_with_flags(self):
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeAccessInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeDeviceInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludePropertyInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeDriverInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeAccessInformation,IncludeDeviceInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeAccessInformation,IncludePropertyInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeAccessInformation,IncludeDriverInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeDeviceInformation,IncludePropertyInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION | SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeDeviceInformation,IncludeDriverInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION | SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludePropertyInformation,IncludeDriverInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION |
                                                               SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeAccessInformation,IncludeDeviceInformation,IncludePropertyInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION |
                                                               SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeAccessInformation,IncludeDeviceInformation,IncludeDriverInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_ACCESS_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION |
                                                               SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeAccessInformation,IncludePropertyInformation,IncludeDriverInformation\n\n')
        frame = _SIAbstractGatewayClient.encode_describe_frame(None, None, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION | SIDescriptionFlags.INCLUDE_PROPERTY_INFORMATION |
                                                               SIDescriptionFlags.INCLUDE_DRIVER_INFORMATION)
        self.assertEqual(frame, 'DESCRIBE\nflags:IncludeDeviceInformation,IncludePropertyInformation,IncludeDriverInformation\n\n')

    def test_encode_complete(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            device_id = random_string(random_int(3, 32))
            frame = _SIAbstractGatewayClient.encode_describe_frame(access_id, device_id, SIDescriptionFlags.INCLUDE_DEVICE_INFORMATION)
            self.assertEqual(frame, f'DESCRIBE\nid:{access_id}.{device_id}\nflags:IncludeDeviceInformation\n\n')


class DESCRIPTIONFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Success\n\n{"a": "b"}')
        self.assertEqual(status, SIStatus.SUCCESS)
        self.assertIsNone(id_)
        self.assertEqual(body, {"a": "b"})

    def test_decode_error(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Error\n\n')
        self.assertEqual(status, SIStatus.ERROR)
        self.assertIsNone(id_)
        self.assertEqual(body, {})

    def test_decode_with_access_id_success(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Success\nid:demo\n\n{"a": "b"}')
        self.assertEqual(status, SIStatus.SUCCESS)
        self.assertEqual(id_, 'demo')
        self.assertEqual(body, {"a": "b"})

    def test_decode_with_access_id_error(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Error\nid:demo\n\n')
        self.assertEqual(status, SIStatus.ERROR)
        self.assertEqual(id_, 'demo')
        self.assertEqual(body, {})

    def test_decode_with_device_id_success(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Success\nid:demo.inv\n\n{"a": "b"}')
        self.assertEqual(status, SIStatus.SUCCESS)
        self.assertEqual(id_, 'demo.inv')
        self.assertEqual(body, {"a": "b"})

    def test_decode_with_device_id_error(self):
        status, id_, body = _SIAbstractGatewayClient.decode_description_frame('DESCRIPTION\nstatus:Error\nid:demo.bat\n\n')
        self.assertEqual(status, SIStatus.ERROR)
        self.assertEqual(id_, 'demo.bat')
        self.assertEqual(body, {})


class READPROPERTYFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractGatewayClient.encode_read_property_frame('demo.inv.3136')
        self.assertEqual(frame, 'READ PROPERTY\nid:demo.inv.3136\n\n')


class PROPERTYREADFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_, value = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Success\nid:demo.inv.3136\nvalue:0.123\n\n')
        self.assertEqual(status, SIStatus.SUCCESS)
        self.assertEqual(id_, 'demo.inv.3136')
        self.assertEqual(value, 0.123)

    def test_decode_error(self):
        status, id_, value = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Error\nid:demo.inv.3136\n\n')
        self.assertEqual(status, SIStatus.ERROR)
        self.assertEqual(id_, 'demo.inv.3136')
        self.assertIsNone(value)

    def test_decode_no_property(self):
        status, id_, value = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:NoProperty\nid:demo.inv.3136\n\n')
        self.assertEqual(status, SIStatus.NO_PROPERTY)
        self.assertEqual(id_, 'demo.inv.3136')
        self.assertIsNone(value)

    def test_decode_no_device(self):
        status, id_, value = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:NoDevice\nid:demo.inv.3136\n\n')
        self.assertEqual(status, SIStatus.NO_DEVICE)
        self.assertEqual(id_, 'demo.inv.3136')
        self.assertIsNone(value)

    def test_decode_no_device_access(self):
        status, id_, value = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:NoDeviceAccess\nid:demo.inv.3136\n\n')
        self.assertEqual(status, SIStatus.NO_DEVICE_ACCESS)
        self.assertEqual(id_, 'demo.inv.3136')
        self.assertIsNone(value)

    def test_decode_timeout(self):
        status, id_, value = _SIAbstractGatewayClient.decode_property_read_frame('PROPERTY READ\nstatus:Timeout\nid:demo.inv.3136\n\n')
        self.assertEqual(status, SIStatus.TIMEOUT)
        self.assertEqual(id_, 'demo.inv.3136')
        self.assertIsNone(value)


if __name__ == '__main__':
    unittest.main()
