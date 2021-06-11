import re
from datetime import datetime


class DriverVersionTimestampBased:
    @staticmethod
    def get_version(version):
        days = (datetime.utcnow() - datetime(2000, 1, 1)).days
        now = datetime.now()
        seconds_since_midnight = (
            now - now.replace(hour=0, minute=0, second=0, microsecond=0)
        ).total_seconds()
        build_and_revision = str(days) + "." + str(int(seconds_since_midnight / 2))
        newver = version.replace("*", build_and_revision)
        return newver

    @staticmethod
    def supports_version_pattern(version):
        return re.match(r"\d+\.\d+\.\*$", version)
