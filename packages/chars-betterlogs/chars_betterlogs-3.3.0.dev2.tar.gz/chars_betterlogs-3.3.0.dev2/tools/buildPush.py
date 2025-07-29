import subprocess, os
from chars_betterlogs.logs import Logging
os.chdir('../')
subprocess.call(["python", "-m", "build"], timeout=180)
paths = os.listdir("dist/")
for path in paths:
    if path.__contains__(Logging.version.toString()): os.remove(path)
subprocess.call(["twine", "upload", "dist/*"])