from datetime import datetime
from inspect import currentframe, getframeinfo
from io import TextIOWrapper
from .internal.semver import SemVer
from .internal.birdy import CheckTime, ScriptArgs

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

a = 'a'
w = 'w'
r = 'r'

class Logging:
    _version:SemVer = SemVer(3, 3, 0, '-PreRelease')
    version = _version
    filename:str = f'betterLogs_{_version.toString().replace('.', '-')}/log.xml'
    allowPrinting:bool = False
    append:bool = False
    showHelp:bool = False # Change this to true if you want to show this help dialogue.
    useCurScriptArgs:bool = False

    def getLogFile(logging) -> str:
        rawXml = open(logging.filename, 'r')
        xml = rawXml.read(); rawXml.close()
        return xml

    def __init__(self, filename:str = None, beforeBeginning:str = '', allowPrinting:bool = True, append:bool = False):
        if ScriptArgs(self.useCurScriptArgs).containsHelp:
            print("""Arguments (Char's BetterLogs):
    -help :              Displays this message.
    -testingScript_BLP : Forces the secret message to be added to logs (see `.internal.birdy.CheckTime`)""")
    

        if filename != None:
            self.filename = filename
        self._createDir(filename)
        self.allowPrinting = allowPrinting
        self.append = append
        self._initWrite()
        self._write(beforeBeginning + CheckTime().message + f'\n<!-- Log Generator: "Better Logs V{self._version.__str__()}" | Better Logs by Char @chargoldenyt on Discord | https://github.com/CharGoldenYT/betterLogs -->\n<!-- START OF LOG -->\n<logFile>\n')
        return

    def getVersion(self, isStr:bool = False)->(SemVer | str):
        if isStr: return self._version.__str__()
        else: return self._version

    def _set_filename(self, filename:str):
        oldFile = open(self.filename, r)
        oldFileStr = oldFile.read()
        oldFile.close()
        import os; os.remove(self.filename)

        self.filename = filename

        path = filename.split('/')
        filename = path[path.__len__()-1]
        basePath = ''
        for p in path:
            if p != filename:
                basePath += p + '/'
                try: os.mkdir(p)
                except: continue
        self._initWrite()
        newFile = open(self.filename, "a")
        newFile.write(oldFileStr)
        newFile.close()

    def isAppend(self)->str:
        if self.append == True: return "a"
        return "w"

    def _createDir(self, path:str):
        import os
        splitPath:list[str] = []
        if path.__contains__('/'):
            splitPath = path.split('/')
            splitPath.pop()

        if splitPath.__len__() > 0:
            for p in  splitPath:
                try:
                    os.makedirs(p.replace('.', '-'))
                except OSError as e:
                    if e.errno != 17:
                        print(f'Could not create log directory! "{str(e)}" make sure you have write access')
                        exit(1)
                    else: continue
        
        
    def _initWrite(self):
        filename = self.filename
        
        testFile = open(filename, "a")
        size  = testFile.__sizeof__()
        if not self.isAppend() == "a" and size > 1: testFile.truncate(0)
        testFile.close()

    def _write(self, content:str):
        filename = self.filename
        logfile_lock = open(filename, 'a')
        logfile_lock.write(content)
        logfile_lock.close()

    def _levelToString(self, level:str) -> str:
        level = level.lower()

        color = '[MISC    ]:'
        if level == 'info':color = '[INFO    ]:'
        if level == 'warn' or level == 'warning':color = '[WARNING ]:'
        if level == 'err' or level == 'error':color = '[ERROR   ]:'
        if level == 'critical':color = '[CRITICAL]:'
        if level == 'fatal':color = '[FATAL   ]:'

        return color

    def log(self, log:str, level:str, includeTimestamp:bool = True, isHeader:bool = False, fileFrom:str = '', pos:int = 0):
        time = str(datetime.today().strftime('%d-%m-%Y %H:%M:%S'))
        timeString = '[' + time + ']: '

        color:str = bcolors.HEADER
        
        if not isHeader:
            level = level.lower()
            if level == 'info':color = bcolors.OKBLUE
            if level == 'warn' or level == 'warning':color = bcolors.WARNING
            if level == 'err' or level == 'error':color = bcolors.FAIL
            if level == 'critical':color = bcolors.FAIL
            if level == 'fatal':color = bcolors.FAIL

        if not includeTimestamp:
            timeString = ''

        fileString = ''

        if fileFrom != '':
            fileString = fileFrom + ':' + str(pos) + ':'

        logString = self._levelToString(level) + timeString + f"'{fileString + log}'".replace('"', "'").replace('<', "[").replace('>', ']')

        if self.allowPrinting: print(color + logString)

        self._write('   <log value="' + logString.replace(fileString, '') + '" />\n')

    def log_header(self, log:str, level:str, includeTimestamps:bool = True,  fileFrom:str = '', pos:int = 0):
        self.log(log, level, includeTimestamps, True, fileFrom, pos)

    def log_info(self, log:str, includeTimestamps:bool = True, fileFrom:str = '', pos:int = 0):
        self.log_header(log, 'info', includeTimestamps, fileFrom, pos)

    def log_error(self, log:str, includeTimestamps:bool = True, fileFrom:str = '', pos:int = 0):
        self.log(log, 'error', includeTimestamps, False, fileFrom, pos)

    def log_err(self, log:str, includeTimestamps:bool = True, fileFrom:str = '', pos:int = 0):
        print(bcolors.WARNING + '[WARNING ]:betterLogs.py:80:log_err() is deprecated! use log_error() instead')
        self.log_error(log, includeTimestamps, fileFrom, pos)

    def log_warning(self, log:str, includeTimestamps:bool = True, fileFrom:str = '', pos:int = 0):
        self.log(log, 'warn', includeTimestamps, False, fileFrom, pos)

    def log_warn(self, log:str, includeTimestamps:bool = True, fileFrom:str = '', pos:int = 0):
        print(bcolors.WARNING + '[WARNING ]:betterLogs.py:87:log_warn() is deprecated! use log_warning() instead')
        self.log_warning(log, includeTimestamps, fileFrom, pos)

    def log_critical(self, log:str, includeTimestamps:bool = True, fileFrom:str = '', pos:int = 0):
        self.log(log, 'critical', includeTimestamps, False, fileFrom, pos)

    def log_fatal(self, log:str, includeTimestamps:bool = True, fileFrom:str = '', pos:int = 0):
        self.log(log, 'fatal', includeTimestamps, False, fileFrom, pos)

    def close(self):
        self._write('</logFile>\n<!--  END OF LOG  -->')