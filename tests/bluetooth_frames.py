import datetime
import random
import string
import unittest
import binascii
import cbor2
# noinspection PyProtectedMember
from openstuder import _SIAbstractBluetoothGatewayClient, SIAccessLevel, SIStatus, SIDescriptionFlags, SIWriteFlags, SIProtocolError


def random_int(start: int, end: int) -> int:
    return random.randint(start, end)


def random_string(length: int) -> str:
    return ''.join(random.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(length))


class AUTHORIZEFrame(unittest.TestCase):
    def test_encode_without_credentials(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_authorize_frame_without_credentials()
        self.assertEqual(binascii.unhexlify("01f6f601"), frame)

    def test_encode_with_credentials(self):
        for _ in range(1000):
            user = random_string(random_int(3, 32))
            password = random_string(random_int(1, 64))
            frame = _SIAbstractBluetoothGatewayClient.encode_authorize_frame_with_credentials(user, password)
            self.assertEqual(binascii.unhexlify("01") + cbor2.dumps(user) + cbor2.dumps(password) +
                             binascii.unhexlify("01"), frame)


class AUTHORIZEDFrame(unittest.TestCase):
    def test_decode_basic(self):
        access_level, gateway_version = _SIAbstractBluetoothGatewayClient.decode_authorized_frame(binascii.unhexlify("188101016C302E302E302E333438373334"))
        self.assertEqual(SIAccessLevel.BASIC, access_level)
        self.assertEqual('0.0.0.348734', gateway_version)

    def test_decode_installer(self):
        access_level, gateway_version = _SIAbstractBluetoothGatewayClient.decode_authorized_frame(binascii.unhexlify("188102016C302E302E302E333438373334"))
        self.assertEqual(SIAccessLevel.INSTALLER, access_level)
        self.assertEqual('0.0.0.348734', gateway_version)

    def test_decode_expert(self):
        access_level, gateway_version = _SIAbstractBluetoothGatewayClient.decode_authorized_frame(binascii.unhexlify("188103016C302E302E302E333438373334"))
        self.assertEqual(SIAccessLevel.EXPERT, access_level)
        self.assertEqual('0.0.0.348734', gateway_version)

    def test_decode_qsp(self):
        access_level, gateway_version = _SIAbstractBluetoothGatewayClient.decode_authorized_frame(binascii.unhexlify("188104016C302E302E302E333438373334"))
        self.assertEqual(SIAccessLevel.QUALIFIED_SERVICE_PERSONNEL, access_level)
        self.assertEqual('0.0.0.348734', gateway_version)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_authorized_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())


class ENUMERATEFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_enumerate_frame()
        self.assertEqual(binascii.unhexlify("02"), frame)


class ENUMERATEDFrame(unittest.TestCase):
    def test_decode_success(self):
        for count in range(1000):
            status, device_count = _SIAbstractBluetoothGatewayClient.decode_enumerated_frame(
                binascii.unhexlify("188200") + cbor2.dumps(count))
            self.assertEqual(SIStatus.SUCCESS, status)
            self.assertEqual(count, device_count)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_enumerated_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())

    def test_decode_in_progress(self):
        status, device_count = _SIAbstractBluetoothGatewayClient.decode_enumerated_frame(binascii.unhexlify("18820100"))
        self.assertEqual(SIStatus.IN_PROGRESS, status)
        self.assertEqual(0, device_count)

    def test_decode_error(self):
        status, device_count = _SIAbstractBluetoothGatewayClient.decode_enumerated_frame(binascii.unhexlify("18822000"))
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual(0, device_count)

    def test_decode_no_property(self):
        status, device_count = _SIAbstractBluetoothGatewayClient.decode_enumerated_frame(binascii.unhexlify("18822100"))
        self.assertEqual(SIStatus.NO_PROPERTY, status)
        self.assertEqual(0, device_count)

    def test_decode_no_device(self):
        status, device_count = _SIAbstractBluetoothGatewayClient.decode_enumerated_frame(binascii.unhexlify("18822200"))
        self.assertEqual(SIStatus.NO_DEVICE, status)
        self.assertEqual(0, device_count)

    def test_decode_no_device_access(self):
        status, device_count = _SIAbstractBluetoothGatewayClient.decode_enumerated_frame(binascii.unhexlify("18822300"))
        self.assertEqual(SIStatus.NO_DEVICE_ACCESS, status)
        self.assertEqual(0, device_count)

    def test_decode_timeout(self):
        status, device_count = _SIAbstractBluetoothGatewayClient.decode_enumerated_frame(binascii.unhexlify("18822400"))
        self.assertEqual(SIStatus.TIMEOUT, status)
        self.assertEqual(0, device_count)

    def test_decode_invalid_value(self):
        status, device_count = _SIAbstractBluetoothGatewayClient.decode_enumerated_frame(binascii.unhexlify("18822500"))
        self.assertEqual(SIStatus.INVALID_VALUE, status)
        self.assertEqual(0, device_count)


class DESCRIBEFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_describe_frame(None, None, None)
        self.assertEqual(binascii.unhexlify("03f6"), frame)

    def test_encode_with_access_id(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            frame = _SIAbstractBluetoothGatewayClient.encode_describe_frame(access_id, None, None)
            self.assertEqual(binascii.unhexlify("03") + cbor2.dumps(access_id), frame)

    def test_encode_with_device_id(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            device_id = random_string(random_int(3, 32))
            frame = _SIAbstractBluetoothGatewayClient.encode_describe_frame(access_id, device_id, None)
            self.assertEqual(binascii.unhexlify("03") + cbor2.dumps(access_id + '.' + device_id), frame)

    def test_encode_with_property_id(self):
        for _ in range(1000):
            access_id = random_string(random_int(3, 32))
            device_id = random_string(random_int(3, 32))
            property_id = random_int(0, 32000)
            frame = _SIAbstractBluetoothGatewayClient.encode_describe_frame(access_id, device_id, property_id)
            self.assertEqual(
                binascii.unhexlify("03") + cbor2.dumps(access_id + '.' + device_id + '.' + str(property_id)), frame)


class DESCRIPTIONFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_, body = _SIAbstractBluetoothGatewayClient.decode_description_frame(binascii.unhexlify("188300f6a16464656d6f6444656d6f"))
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertIsNone(id_)
        self.assertEqual({"demo": "Demo"}, body)

    def test_decode_error(self):
        status, id_, body = _SIAbstractBluetoothGatewayClient.decode_description_frame(binascii.unhexlify("188320f6f6"))
        self.assertEqual(SIStatus.ERROR, status)
        self.assertIsNone(id_)
        self.assertEqual(None, body)

    def test_decode_with_access_id_success(self):
        status, id_, body = _SIAbstractBluetoothGatewayClient.decode_description_frame(binascii.unhexlify("1883006464656D6FA16464656D6F6444656D6F"))
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo', id_)
        self.assertEqual({"demo": "Demo"}, body)

    def test_decode_with_access_id_error(self):
        status, id_, body = _SIAbstractBluetoothGatewayClient.decode_description_frame(binascii.unhexlify("1883206464656D6FF6"))
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo', id_)
        self.assertEqual(None, body)

    def test_decode_with_device_id_success(self):
        status, id_, body = _SIAbstractBluetoothGatewayClient.decode_description_frame(binascii.unhexlify("1883006864656D6F2E696E76A163696E766D44656D6F20496E766572746572"))
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.inv', id_)
        self.assertEqual({"inv": "Demo Inverter"}, body)

    def test_decode_with_device_id_error(self):
        status, id_, body = _SIAbstractBluetoothGatewayClient.decode_description_frame(binascii.unhexlify("1883206864656D6F2E626174F6"))
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.bat', id_)
        self.assertEqual(None, body)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_description_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())


class READPROPERTYFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_property_frame('demo.inv.3136')
        self.assertEqual(binascii.unhexlify("046d64656d6f2e696e762e33313336"), frame)


class PROPERTYREADFrame(unittest.TestCase):
    def test_decode_success_float(self):
        result = _SIAbstractBluetoothGatewayClient.decode_property_read_frame(binascii.unhexlify("1884006D64656D6F2E696E762E33313336FB3FBF7CED916872B0"))
        self.assertEqual(SIStatus.SUCCESS, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertEqual(0.123, result.value)

    def test_decode_success_false(self):
        result = _SIAbstractBluetoothGatewayClient.decode_property_read_frame(binascii.unhexlify("1884006D64656D6F2E696E762E33313336F4"))
        self.assertEqual(SIStatus.SUCCESS, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertEqual(False, result.value)

    def test_decode_success_true(self):
        result = _SIAbstractBluetoothGatewayClient.decode_property_read_frame(binascii.unhexlify("1884006D64656D6F2E696E762E33313336F5"))
        self.assertEqual(SIStatus.SUCCESS, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertEqual(True, result.value)

    def test_decode_error(self):
        result = _SIAbstractBluetoothGatewayClient.decode_property_read_frame(binascii.unhexlify("1884206D64656D6F2E696E762E33313336F6"))
        self.assertEqual(SIStatus.ERROR, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_no_property(self):
        result = _SIAbstractBluetoothGatewayClient.decode_property_read_frame(binascii.unhexlify("1884216D64656D6F2E696E762E33313336F6"))
        self.assertEqual(SIStatus.NO_PROPERTY, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_no_device(self):
        result = _SIAbstractBluetoothGatewayClient.decode_property_read_frame(binascii.unhexlify("1884226D64656D6F2E696E762E33313336F6"))
        self.assertEqual(SIStatus.NO_DEVICE, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_no_device_access(self):
        result = _SIAbstractBluetoothGatewayClient.decode_property_read_frame(binascii.unhexlify("1884236D64656D6F2E696E762E33313336F6"))
        self.assertEqual(SIStatus.NO_DEVICE_ACCESS, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_timeout(self):
        result = _SIAbstractBluetoothGatewayClient.decode_property_read_frame(binascii.unhexlify("1884246D64656D6F2E696E762E33313336F6"))
        self.assertEqual(SIStatus.TIMEOUT, result.status)
        self.assertEqual('demo.inv.3136', result.id)
        self.assertIsNone(result.value)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_property_read_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())


class WRITEPROPERTYFrame(unittest.TestCase):
    def test_encode_without_value(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_write_property_frame('demo.inv.1415', None, None)
        self.assertEqual(binascii.unhexlify("056d64656d6f2e696e762e31343135f6f6"), frame)

    def test_encode_with_value(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_write_property_frame('demo.inv.3333', 42.24, None)
        self.assertEqual(binascii.unhexlify("056d64656d6f2e696e762e33333333f6fb40451eb851eb851f"), frame)

    def test_encode_with_value_empty_flags(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_write_property_frame('demo.inv.3333', 42.24, SIWriteFlags.NONE)
        self.assertEqual(binascii.unhexlify("056d64656d6f2e696e762e3333333300fb40451eb851eb851f"), frame)

    def test_encode_with_value_permanent_flag(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_write_property_frame('demo.inv.3333', 42.24, SIWriteFlags.PERMANENT)
        self.assertEqual(binascii.unhexlify("056d64656d6f2e696e762e3333333301fb40451eb851eb851f"), frame)


class PROPERTYWRITTENFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_written_frame(binascii.unhexlify("1885006D64656D6F2E696E762E31333939"))
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_error(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_written_frame(binascii.unhexlify("1885206D64656D6F2E696E762E31333939"))
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_no_property(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_written_frame(binascii.unhexlify("1885216D64656D6F2E696E762E31333939"))
        self.assertEqual(SIStatus.NO_PROPERTY, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_no_device(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_written_frame(binascii.unhexlify("1885226D64656D6F2E696E762E31333939"))
        self.assertEqual(SIStatus.NO_DEVICE, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_no_device_access(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_written_frame(binascii.unhexlify("1885236D64656D6F2E696E762E31333939"))
        self.assertEqual(SIStatus.NO_DEVICE_ACCESS, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_timeout(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_written_frame(binascii.unhexlify("1885246D64656D6F2E696E762E31333939"))
        self.assertEqual(SIStatus.TIMEOUT, status)
        self.assertEqual('demo.inv.1399', id_)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_property_written_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())


class SUBSCRIBEPROPERTYFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_subscribe_property_frame('demo.bat.7003')
        self.assertEqual(binascii.unhexlify("066d64656d6f2e6261742e37303033"), frame)


class PROPERTYSUBSCRIBEDFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_subscribed_frame(binascii.unhexlify("1886006D64656D6F2E6261742E37303033"))
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_error(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_subscribed_frame(binascii.unhexlify("1886206D64656D6F2E6261742E37303033"))
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_no_property(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_subscribed_frame(binascii.unhexlify("1886216D64656D6F2E6261742E37303033"))
        self.assertEqual(SIStatus.NO_PROPERTY, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_property_subscribed_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())


class PROPERTYUPDATEFrame(unittest.TestCase):
    def test_decode_float(self):
        id_, value = _SIAbstractBluetoothGatewayClient.decode_property_update_frame(binascii.unhexlify("18FE6D64656D6F2E6261742E37303033FB400EFDF3B645A1CB"))
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(3.874, value)

    def test_decode_false(self):
        id_, value = _SIAbstractBluetoothGatewayClient.decode_property_update_frame(binascii.unhexlify("18FE6D64656D6F2E6261742E37303033F4"))
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(False, value)

    def test_decode_true(self):
        id_, value = _SIAbstractBluetoothGatewayClient.decode_property_update_frame(binascii.unhexlify("18FE6D64656D6F2E6261742E37303033F5"))
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(True, value)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_property_update_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())


class UNSUBSCRIBEPROPERTYFrame(unittest.TestCase):
    def test_encode(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_unsubscribe_property_frame('demo.bat.7003')
        self.assertEqual(binascii.unhexlify("076d64656d6f2e6261742e37303033"), frame)


class PROPERTYUNSUBSCRIBEDFrame(unittest.TestCase):
    def test_decode_success(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_unsubscribed_frame(binascii.unhexlify("1887006D64656D6F2E6261742E37303033"))
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_error(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_unsubscribed_frame(binascii.unhexlify("1887206D64656D6F2E6261742E37303033"))
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_no_property(self):
        status, id_ = _SIAbstractBluetoothGatewayClient.decode_property_unsubscribed_frame(binascii.unhexlify("1887216D64656D6F2E6261742E37303033"))
        self.assertEqual(SIStatus.NO_PROPERTY, status)
        self.assertEqual('demo.bat.7003', id_)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_property_unsubscribed_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())


class READDATALOGFrame(unittest.TestCase):
    def test_encode_property_list(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame(None, None, None, None)
        self.assertEqual(binascii.unhexlify("08f6f6f6f6"), frame)

    def test_encode_property_list_from_date(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame(None, datetime.datetime(year=1987, month=12, day=19), None, None)
        print(binascii.hexlify(frame))
        self.assertEqual(binascii.unhexlify("08f61a21c9b370f6f6"), frame)

    def test_encode_property_list_from_datetime(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame(None, datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None, None)
        self.assertEqual(binascii.unhexlify("08f61a21ca6cb6f6f6"), frame)

    def test_encode_property_list_to_date(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame(None, None, datetime.datetime(year=1987, month=12, day=19), None)
        self.assertEqual(binascii.unhexlify("08f6f61a21c9b370f6"), frame)

    def test_encode_property_list_to_datetime(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame(None, None, datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None)
        self.assertEqual(binascii.unhexlify("08f6f61a21ca6cb6f6"), frame)

    def test_encode_property_list_from_to(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame(None, datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30),
                                                                   datetime.datetime(year=1987, month=12, day=20, hour=13, minute=10, second=30), None)
        self.assertEqual(binascii.unhexlify("08f61a21ca6cb61a21cbbe36f6"), frame)

    def test_encode_minimal(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame('demo.inv.3137', None, None, None)
        self.assertEqual(binascii.unhexlify("086d64656d6f2e696e762e33313337f6f6f6"), frame)

    def test_encode_from_date(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame('demo.inv.3137', datetime.datetime(year=1987, month=12, day=19), None, None)
        self.assertEqual(binascii.unhexlify("086d64656d6f2e696e762e333133371a21c9b370f6f6"), frame)

    def test_encode_from_datetime(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame('demo.inv.3137', datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None, None)
        self.assertEqual(binascii.unhexlify("086d64656d6f2e696e762e333133371a21ca6cb6f6f6"), frame)

    def test_encode_to_date(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame('demo.inv.3137', None, datetime.datetime(year=1987, month=12, day=19), None)
        self.assertEqual(binascii.unhexlify("086d64656d6f2e696e762e33313337f61a21c9b370f6"), frame)

    def test_encode_to_datetime(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame('demo.inv.3137', None, datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None)
        self.assertEqual(binascii.unhexlify("086d64656d6f2e696e762e33313337f61a21ca6cb6f6"), frame)

    def test_encode_limit(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame('demo.inv.3137', None, None, 42)
        self.assertEqual(binascii.unhexlify("086d64656d6f2e696e762e33313337f6f6182a"), frame)

    def test_encode_from_to(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame('demo.inv.3137', datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30),
                                                                   datetime.datetime(year=1987, month=12, day=20, hour=13, minute=10, second=30), None)
        self.assertEqual(binascii.unhexlify("086d64656d6f2e696e762e333133371a21ca6cb61a21cbbe36f6"), frame)

    def test_encode_complete(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_datalog_frame('demo.inv.3137', datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30),
                                                                   datetime.datetime(year=1987, month=12, day=20, hour=13, minute=10, second=30), 13)
        self.assertEqual(binascii.unhexlify("086d64656d6f2e696e762e333133371a21ca6cb61a21cbbe360d"), frame)


class DATALOGREADFrame(unittest.TestCase):
    def test_decode_property_list(self):
        status, id_, count, properties = _SIAbstractBluetoothGatewayClient.decode_datalog_read_frame(binascii.unhexlify("188800F602826D64656D6F2E6261742E373030336D64656D6F2E696E762E33313336"))
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual(None, id_)
        self.assertEqual(2, count)
        self.assertEqual(["demo.bat.7003", "demo.inv.3136"], properties)

    def test_decode_success(self):
        status, id_, count, data = _SIAbstractBluetoothGatewayClient.decode_datalog_read_frame(binascii.unhexlify("1888006D64656D6F2E6261742E3730303302841A60203CE8FB3FA01A36E2EB1C431A60203CACFB3FEB15379FA97E13"))
        self.assertEqual(SIStatus.SUCCESS, status)
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(2, count)
        self.assertEqual(4, len(data))
        self.assertEqual([1612725480, 0.03145, 1612725420, 0.84634], data)

    def test_decode_error(self):
        status, id_, count, data = _SIAbstractBluetoothGatewayClient.decode_datalog_read_frame(binascii.unhexlify("1888206D64656D6F2E6261742E373030330080"))
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual('demo.bat.7003', id_)
        self.assertEqual(0, count)
        self.assertEqual([], data)

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_datalog_read_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())


class DEVICEMESSAGEFrame(unittest.TestCase):
    def test_decode(self):
        message = _SIAbstractBluetoothGatewayClient.decode_device_message_frame(binascii.unhexlify("18FD1A5E0BD2F0644133303362313118D277415558322072656C617920646561637469766174696F6E"))
        self.assertEqual(datetime.datetime(year=2020, month=1, day=1), message.timestamp)
        self.assertEqual('A303', message.access_id)
        self.assertEqual('11', message.device_id)
        self.assertEqual(210, message.message_id)
        self.assertEqual('AUX2 relay deactivation', message.message)


class READMESSAGESFrame(unittest.TestCase):
    def test_encode_minimal(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_messages_frame(None, None, None)
        self.assertEqual(binascii.unhexlify("09f6f6f6"), frame)

    def test_encode_from_date(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_messages_frame(datetime.datetime(year=1987, month=12, day=19), None, None)
        self.assertEqual(binascii.unhexlify("091a21c9b370f6f6"), frame)

    def test_encode_from_datetime(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_messages_frame(datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None, None)
        self.assertEqual(binascii.unhexlify("091a21ca6cb6f6f6"), frame)

    def test_encode_to_date(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_messages_frame(None, datetime.datetime(year=1987, month=12, day=19), None)
        self.assertEqual(binascii.unhexlify("09f61a21c9b370f6"), frame)

    def test_encode_to_datetime(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_messages_frame(None, datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30), None)
        self.assertEqual(binascii.unhexlify("09f61a21ca6cb6f6"), frame)

    def test_encode_limit(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_messages_frame(None, None, 42)
        self.assertEqual(binascii.unhexlify("09f6f6182a"), frame)

    def test_encode_from_to(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_messages_frame(datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30),
                                                                   datetime.datetime(year=1987, month=12, day=20, hour=13, minute=10, second=30), None)
        self.assertEqual(binascii.unhexlify("091a21ca6cb61a21cbbe36f6"), frame)

    def test_encode_complete(self):
        frame = _SIAbstractBluetoothGatewayClient.encode_read_messages_frame(datetime.datetime(year=1987, month=12, day=19, hour=13, minute=10, second=30),
                                                                   datetime.datetime(year=1987, month=12, day=20, hour=13, minute=10, second=30), 13)
        self.assertEqual(binascii.unhexlify("091a21ca6cb61a21cbbe360d"), frame)


class MESSAGESREADFrame(unittest.TestCase):
    def test_decode_success(self):
        status, count, messages = _SIAbstractBluetoothGatewayClient.decode_messages_read_frame(
            binascii.unhexlify("188900028A1A5E0BD2F06464656D6F63696E7618D175415558322072656C61792061637469766174696F6E1A5E0BD6746464656D6F63696E7618D277415558322072656C617920646561637469766174696F6E"))
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
        status, count, messages = _SIAbstractBluetoothGatewayClient.decode_messages_read_frame(binascii.unhexlify("1889200080"))
        self.assertEqual(SIStatus.ERROR, status)
        self.assertEqual(0, count)
        self.assertEqual(0, len(messages))

    def test_decode_frame_error(self):
        with self.assertRaises(SIProtocolError) as context:
            _SIAbstractBluetoothGatewayClient.decode_messages_read_frame(binascii.unhexlify("18FF6474657374"))
        self.assertEqual('test', context.exception.reason())


if __name__ == '__main__':
    unittest.main()
