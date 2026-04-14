import sys
import os

# Set test environment early
os.environ["ENVIRONMENT"] = "test"

# Prevent the config module from auto-loading settings
# by clearing any existing config modules before tests run
def pytest_configure(config):
    modules_to_remove = [key for key in sys.modules.keys() if key.startswith('backend.app.config')]
    for module in modules_to_remove:
        del sys.modules[module]
