"""Module-wide fixtures for testing hrm-omero."""

import logging
import pytest
from _pytest.logging import caplog as _caplog
from loguru import logger


### pytest setup ###


def pytest_addoption(parser):
    """Add a command line option '--online' to pytest."""
    parser.addoption(
        "--online",
        action="store_true",
        default=False,
        help="enable online tests communicating to a real OMERO instance",
    )


def pytest_collection_modifyitems(config, items):
    """Add the 'skip' marker to tests decorated with 'pytest.mark.online'."""
    if config.getoption("--online"):
        # --online given in cli: do not skip online tests
        return
    skip_online = pytest.mark.skip(reason="need --online option to run")
    for item in items:
        if "online" in item.keywords:
            item.add_marker(skip_online)


### caplog special loguru setup ###


@pytest.fixture
def caplog(_caplog):
    """Fixture adding a sink that propagates Loguru messages to the builtin logging.

    This ensures that pytest will be able to capture log messages via the "normal"
    `caplog` fixture that are actually logged through Loguru.
    """

    class PropagateHandler(logging.Handler):
        """Helper class to propagate emitted messages to the `logging` module."""

        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropagateHandler(), format="{message} {extra}")
    yield _caplog
    logger.remove(handler_id)
