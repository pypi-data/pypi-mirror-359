# OpenLog

A versatile Python logging utility with rich console output and file logging capabilities.

## Features

- Color-coded console output using Rich
- Optional file logging with session-based or persistent log files
- Multiple log levels (INFO, ERROR, WARN, INIT)
- In-memory log storage with flush capability

## Installation

```bash
pip install openlog
```

## Quick Start

```python
from openlog import Logger

# Basic console-only logger
logger = Logger()
logger.log("This is an info message")
logger.error("Something went wrong")
logger.warn("This is a warning")
logger.init("System initialized")

# Logger with file output
file_logger = Logger(write_to_file=True)
file_logger.log("This message goes to console and file")

# Session-based logging (new log file for each session)
session_logger = Logger(write_to_file=True, session=True)
session_logger.log("Logged with timestamp in filename")

# Store logs in a specific directory
dir_logger = Logger(in_dir=True, write_to_file=True)
dir_logger.log("Logs stored in /logs directory")

# Using custom prefixes for better log organization
module_logger = Logger(prefix="DATABASE")
module_logger.log("Connected to database")  # Will show as "[DATABASE] Connected to database"

# Retrieve logs programmatically
logs = file_logger.flush_logs()
all_logs = file_logger.flush_logs(from_start=True)
```

## Log Levels
- ```log()``` - General information (blue)
- ```error()``` - Error messages (red)
- ```warn()``` - Warning messages (yellow)
- ```init()``` - Initialization messages (purple)

## Configuration
The ```Logger``` class accepts the following parameters:
- ```in_dir``` (bool): Store logs in a '/logs' directory
- ```session``` (bool): Create unique log files with timestamps
- ```write_to_file``` (bool): Enable file logging
- ```prefix``` (str): Optional prefix added to all log messages (e.g., module name, component identifier)

## License
MIT License
