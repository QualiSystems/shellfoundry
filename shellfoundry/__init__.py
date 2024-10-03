from os.path import dirname, join

ALTERNATIVE_TEMPLATES_PATH = join(dirname(__file__), "data", "templates.yml")
ALTERNATIVE_STANDARDS_PATH = join(dirname(__file__), "data", "standards.json")

MASTER_BRANCH_NAME = "master"

PACKAGE_NAME = __package__.split(".")[0]
