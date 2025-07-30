# t8386

A simple Python logger class with colored output and timestamps.

## Installation

```bash
pip install t8386

from t8386 import Logger

# Basic logging
Logger.log_info("This is an info message")
Logger.log_error("This is an error message")
Logger.log_success("This is a success message")
Logger.log_warning("This is a warning message")
Logger.log_debug("This is a debug message")
Logger.log("This is a generic message")
Logger.log_hana("This is a HANA style message")