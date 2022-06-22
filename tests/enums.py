import unittest
from openstuder import SIStatus, SIAccessLevel, SIExtensionStatus


class SIStatusTest(unittest.TestCase):
    def test_from_string(self):
        self.assertEqual(SIStatus.from_string('Success'), SIStatus.SUCCESS)
        self.assertEqual(SIStatus.from_string('InProgress'), SIStatus.IN_PROGRESS)
        self.assertEqual(SIStatus.from_string('Error'), SIStatus.ERROR)
        self.assertEqual(SIStatus.from_string('NoProperty'), SIStatus.NO_PROPERTY)
        self.assertEqual(SIStatus.from_string('NoDevice'), SIStatus.NO_DEVICE)
        self.assertEqual(SIStatus.from_string('NoDeviceAccess'), SIStatus.NO_DEVICE_ACCESS)
        self.assertEqual(SIStatus.from_string('Timeout'), SIStatus.TIMEOUT)
        self.assertEqual(SIStatus.from_string('InvalidValue'), SIStatus.INVALID_VALUE)

    def test_from_ordinal(self):
        self.assertEqual(SIStatus.SUCCESS, SIStatus.from_ordinal(0))
        self.assertEqual(SIStatus.IN_PROGRESS, SIStatus.from_ordinal(1))
        self.assertEqual(SIStatus.ERROR, SIStatus.from_ordinal(-1))
        self.assertEqual(SIStatus.NO_PROPERTY, SIStatus.from_ordinal(-2))
        self.assertEqual(SIStatus.NO_DEVICE, SIStatus.from_ordinal(-3))
        self.assertEqual(SIStatus.NO_DEVICE_ACCESS, SIStatus.from_ordinal(-4))
        self.assertEqual(SIStatus.TIMEOUT, SIStatus.from_ordinal(-5))
        self.assertEqual(SIStatus.INVALID_VALUE, SIStatus.from_ordinal(-6))


class SIAccessLevelTest(unittest.TestCase):
    def test_from_string(self):
        self.assertEqual(SIAccessLevel.from_string('None'), SIAccessLevel.NONE)
        self.assertEqual(SIAccessLevel.from_string('Basic'), SIAccessLevel.BASIC)
        self.assertEqual(SIAccessLevel.from_string('Installer'), SIAccessLevel.INSTALLER)
        self.assertEqual(SIAccessLevel.from_string('Expert'), SIAccessLevel.EXPERT)
        self.assertEqual(SIAccessLevel.from_string('QSP'), SIAccessLevel.QUALIFIED_SERVICE_PERSONNEL)


class SIExtensionStatusTest(unittest.TestCase):
    def test_from_string(self):
        self.assertEqual(SIExtensionStatus.SUCCESS, SIExtensionStatus.from_string("Success"))
        self.assertEqual(SIExtensionStatus.UNSUPPORTED_EXTENSION, SIExtensionStatus.from_string("UnsupportedExtension"))
        self.assertEqual(SIExtensionStatus.UNSUPPORTED_COMMAND, SIExtensionStatus.from_string("UnsupportedCommand"))
        self.assertEqual(SIExtensionStatus.INVALID_HEADERS, SIExtensionStatus.from_string("InvalidHeaders"))
        self.assertEqual(SIExtensionStatus.INVALID_PARAMETERS, SIExtensionStatus.from_string("InvalidParameters"))
        self.assertEqual(SIExtensionStatus.INVALID_BODY, SIExtensionStatus.from_string("InvalidBody"))
        self.assertEqual(SIExtensionStatus.FORBIDDEN, SIExtensionStatus.from_string("Forbidden"))
        self.assertEqual(SIExtensionStatus.ERROR, SIExtensionStatus.from_string("Error"))

    def test_from_ordinal(self):
        self.assertEqual(SIExtensionStatus.SUCCESS, SIExtensionStatus.from_ordinal(0))
        self.assertEqual(SIExtensionStatus.UNSUPPORTED_EXTENSION, SIExtensionStatus.from_ordinal(-1))
        self.assertEqual(SIExtensionStatus.UNSUPPORTED_COMMAND, SIExtensionStatus.from_ordinal(-2))
        self.assertEqual(SIExtensionStatus.INVALID_HEADERS, SIExtensionStatus.from_ordinal(-3))
        self.assertEqual(SIExtensionStatus.INVALID_PARAMETERS, SIExtensionStatus.from_ordinal(-3))
        self.assertEqual(SIExtensionStatus.INVALID_BODY, SIExtensionStatus.from_ordinal(-4))
        self.assertEqual(SIExtensionStatus.FORBIDDEN, SIExtensionStatus.from_ordinal(-5))
        self.assertEqual(SIExtensionStatus.ERROR, SIExtensionStatus.from_ordinal(-6))


if __name__ == '__main__':
    unittest.main()
