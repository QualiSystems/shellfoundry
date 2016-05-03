from cookiecutter.main import cookiecutter
from qpm.packaging.drivers_packager import DriversPackager
from qpm.packaging.shell_installer import ShellInstaller
from qpm.packaging.shell_packager import ShellPackager


class ShellFoundryGateway(object):
    def __init__(self):
        pass

    def create(self, template):
        cookiecutter(template)

    def pack(self, package_name):
        drivers_packager = DriversPackager()
        drivers_packager.package_drivers(package_name)
        packager = ShellPackager()
        packager.create_shell_package(package_name)

    def install(self, package_name):
        installer = ShellInstaller()
        installer.install(package_name)
