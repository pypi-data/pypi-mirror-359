from chars_betterlogs.logs import Logging
from chars_betterlogs.logs import bcolors

logger:Logging = Logging("logs/TestLog.xml", "<!-- This log contains random bullshit! -->")
print(f"{bcolors.HEADER}The line numbers are real, but the script names aren't")

if hasattr(logger, "version"): print(f"{bcolors.HEADER}You may have an outdated version of betterlogs! logger.version returns: '{logger.version}' | Reminder logger.version was deprecated and will have been removed in v3.3.1")
else: print(f"{bcolors.HEADER}Reminder logger.version was deprecated and will have been removed in v3.3.1")

logger.log("Test1", "", True, True, "YoMum.py", 9)

if hasattr(logger, "log_warn"): logger.log_warn("YO THIS SHIT `log_warn()` REMOVED IN 3.3.1!")
logger.log_warning("Test warning!", True, "YoMum.py", 11)

if hasattr(logger, "log_err"): logger.log_err("YO THIS SHIT `log_err()` REMOVED IN 3.3.1!")
logger.log_error("Test Error!", True, "YoMum.py", 15)

logger.log_header("Test Header", "", True, "YoMum.py", 17)

logger.log_critical("ACK TEST CRITICAL ERROR!", True, "YoMum.py", 19)

logger.log_fatal("YOU MADE TOO MANY SKILL ISSUES!", True, "YoMum.py", 21)

from time import sleep
print(f"{bcolors.ENDC}closing in 5 seconds")
sleep(5)
logger.close()