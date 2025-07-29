from datetime import datetime
from .args import ScriptArgs

class CheckTime:
    message:str = ""
    args:ScriptArgs

    def __init__(self):
        self.args = ScriptArgs()
        if datetime.today().strftime('%d/%m') == "18/08":
            self.message = "\n<!-- Today is CharGoldenYT's birthday! -->"

        if self.args.containsTSBLP:
            self.message = "\n<!-- Today is CharGoldenYT's birthday! -->"