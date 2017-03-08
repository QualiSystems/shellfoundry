from freezegun import freeze_time
from shellfoundry.utilities.version_utilities import DriverVersionTimestampBased
from unittest import TestCase


class TestDriverVersionTimestampBased(TestCase):
    def test_it_gets_the_expected_build_and_revision_values_according_to_timestamp(self):
        with freeze_time("2012-01-14 12:00:01"):
            version_freezed = DriverVersionTimestampBased.get_version('1.2.*')

        self.assertEquals(version_freezed, '1.2.4396.21600')

    def test_it_gets_a_higher_build_and_revision_values_each_time(self):
        with freeze_time("2012-01-14 12:00:01"):
            version1 = DriverVersionTimestampBased.get_version('1.2.*')

        with freeze_time("2012-01-14 12:00:10"):
            version2 = DriverVersionTimestampBased.get_version('1.2.*')

        self.assertNotEquals(version1, version2)
        self.assertEquals(version1, '1.2.4396.21600')
        self.assertEquals(version2, '1.2.4396.21605')

    def test_it_supports_one_build_wildcard(self):
        self.assertTrue(DriverVersionTimestampBased.supports_version_pattern('1.2.*'))

    def test_it_doesnt_support_no_wildcards(self):
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('1.2.3'))

    def test_it_doesnt_support_more_than_one_wildcard(self):
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('1.*.*'))
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('*.1.*'))
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('1.2.*.*'))

    def test_it_doesnt_support_major_minor_or_revision_wildcards(self):
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('1.1.1.*'))
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('*.1.1'))
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('1.*.1'))
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('1.*'))

    def test_it_supports_only_major_minor_numbers(self):
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('a.1.*'))
        self.assertFalse(DriverVersionTimestampBased.supports_version_pattern('1.b.*'))
