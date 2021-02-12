import unittest
from openstuder import SIStatus, SIAccessLevel


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


class SIAccessLevelTest(unittest.TestCase):
    def test_from_string(self):
        self.assertEqual(SIAccessLevel.from_string('None'), SIAccessLevel.NONE)
        self.assertEqual(SIAccessLevel.from_string('Basic'), SIAccessLevel.BASIC)
        self.assertEqual(SIAccessLevel.from_string('Installer'), SIAccessLevel.INSTALLER)
        self.assertEqual(SIAccessLevel.from_string('Expert'), SIAccessLevel.EXPERT)
        self.assertEqual(SIAccessLevel.from_string('QSP'), SIAccessLevel.QUALIFIED_SERVICE_PERSONNEL)


if __name__ == '__main__':
    unittest.main()
