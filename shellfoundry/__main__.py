# -*- coding: utf-8 -*-


"""bootstrap.cli: executed when bootstrap directory is called as script."""
from bootstrap import cli
cli()

# Alternative way to create the script which supports arguments
# import sys
# from bootstrap import cli
#
# def main(args=None):
#     if args is None:
#         args = sys.argv[1:]
#     cli()
#
# if __name__ == "__main__":
#     main()
