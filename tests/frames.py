import random
import string
import unittest
# noinspection PyProtectedMember
from openstuder import _SIAbstractGatewayClient, SIAccessLevel, SIStatus


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


    # TODO: Tests for remaining frames.


if __name__ == '__main__':
    unittest.main()