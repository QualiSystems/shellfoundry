from freezegun import freeze_time
from shellfoundry.utilities.version_utilities import VersionUtilities
from unittest import TestCase

class TestVersionUtilities(TestCase):
    def test_it_gets_the_expected_build_and_revision_values__according_to_timestamp(self):
        with freeze_time("2012-01-14 12:00:01"):
            version_freezed = VersionUtilities.get_timestamped_build_and_revision()

        self.assertEquals(version_freezed, '4396.21600')

    def test_it_gets_a_higher_build_and_revision_values_each_time(self):
        with freeze_time("2012-01-14 12:00:01"):
            version1 = VersionUtilities.get_timestamped_build_and_revision()

        with freeze_time("2012-01-14 12:00:10"):
            version2 = VersionUtilities.get_timestamped_build_and_revision()

        self.assertNotEquals(version1, version2)
        self.assertEquals(version1, '4396.21600')
        self.assertEquals(version2, '4396.21605')

