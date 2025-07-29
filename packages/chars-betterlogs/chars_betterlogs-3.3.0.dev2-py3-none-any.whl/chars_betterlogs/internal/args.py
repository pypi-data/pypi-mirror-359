from sys import argv

# args
helpArg = "-help"
testerScript = "-testingScript_BLP"

# Processor
class ScriptArgs:
    args:list[str] = []; containsHelp:bool; containsTSBLP:bool

    def __init__(self, useArgs:(bool | None)):
        if useArgs:
            a = argv
            a.pop(0)

            self.args = a
            self.containsHelp = a.__contains__(helpArg); self.containsTSBLP = a.__contains__(testerScript)