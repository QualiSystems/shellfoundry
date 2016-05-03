from qpm.packaging.auto_argument_parser import AutoArgumentParser
from shellfoundry.gateway import ShellFoundryGateway


def main():
    argument_parser = AutoArgumentParser(ShellFoundryGateway)
    argument_parser.parse_args()

if __name__ == "__main__":
    main()
