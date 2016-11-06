import os
import zipfile


class ArchiveCreator(object):

    @staticmethod
    def make_archive(output_filename, format, source_dir):
        """
        Creates archive in specified format recursively of source_dir
        Replaces shtutil.make_archive in order to be able to test with pyfakefs
        :param output_filename: Output archive file name. If directory does not exist, it will be created
        :param format: Archive format to be used. Currently only zip is supported
        :param source_dir: Directory to scan for archiving
        :return:
        """
        if os.path.splitext(output_filename)[1] == '':
            output_filename += '.zip'
        output_dir = os.path.dirname(output_filename)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        relroot = source_dir
        with zipfile.ZipFile(output_filename, "w", zipfile.ZIP_DEFLATED) as zip:
            for root, dirs, files in os.walk(source_dir):
                # add directory (needed for empty dirs)
                zip.write(root, os.path.relpath(root, relroot))
                for file in files:
                    filename = os.path.join(root, file)
                    if os.path.isfile(filename):  # regular files only
                        arcname = os.path.join(os.path.relpath(root, relroot), file)
                        zip.write(filename, arcname)

        return output_filename

