from datetime import datetime


class VersionUtilities:
    @staticmethod
    def get_timestamped_build_and_revision():
        days = (datetime.utcnow() - datetime(2000, 1, 1)).days
        now = datetime.now()
        seconds_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds()
        revision = str(days) + '.' + str(int(seconds_since_midnight / 2))
        return revision
