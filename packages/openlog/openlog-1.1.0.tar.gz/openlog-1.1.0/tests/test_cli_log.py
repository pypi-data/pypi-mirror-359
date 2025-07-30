from openlog import Logger

# Basic console-only logger
logger = Logger()
logger.log("This is an info message")
logger.error("Something went wrong")
logger.warn("This is a warning")
logger.init("System initialized")
