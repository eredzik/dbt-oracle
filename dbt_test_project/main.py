from dbt.main import main
import logging

from dbt.logger import GLOBAL_LOGGER as logger

# logger.setLevel(logging.DEBUG)
main(["seed", "--profiles-dir", "./"])
