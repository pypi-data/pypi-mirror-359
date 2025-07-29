from .logs import Logging
from . import betterLogs
__all__ = ["Logging", "betterLogs", "getLogFile"]

getLogFile = Logging.getLogFile