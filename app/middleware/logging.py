import logging


def setup_test_logger():
    logging.basicConfig(
        filename="dashboard.log",
        level=logging.INFO,
        format="%(asctime)s -- %(name)s -- %(levelname)s -- %(message)s",
        encoding="utf-8",
        filemode="a"
    )


setup_test_logger()
logger = logging.getLogger()  # Get the root logger to use the basicConfig settings
