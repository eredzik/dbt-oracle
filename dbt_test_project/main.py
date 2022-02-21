from dbt.main import main
import logging

from dbt.logger import GLOBAL_LOGGER as logger

# logger.setLevel(logging.DEBUG)
# main(["seed", "--profiles-dir", "./"])
# main(["run", "--profiles-dir", "./"])
# main(["run", "--profiles-dir", "./", "--select", "person_inc"])

# main(["test", "--profiles-dir", "./"])
main(["docs", "generate", "--profiles-dir", "./"])
