import sys



class ProgressBar:
    def __init__(self, length : int, postfix : str = "%", report_total : bool = False):
        self.current = 0
        self.length = length - 2
        self.postfix = postfix
        self.report_total = report_total

    def Start(self, msg):
        sys.stdout.write(f"{msg}[{' ' * self.length}]")
        sys.stdout.flush()

    def ReportProgress(self, progress, total):
        p = int(progress * total)
        if p > self.current:
            sp = f"{p}{self.postfix}"
            if self.report_total:
                sp += f"/{total}{self.postfix}"

            width = len(sp)
            left = self.length // 2 - width // 2
            sys.stdout.write("\b" * (self.length + 1))
            for i in range(self.length):
                if i >= left and i < left + width:
                    sys.stdout.write(sp[i - left])
                else:
                    sys.stdout.write("=" if i < p * self.length // total else " ")
            sys.stdout.write("]")
            sys.stdout.flush()
            self.current = p
    
    def Finish(self):
        sp = f"{self.current}{self.postfix}"
        if self.report_total:
            sp += f"/{self.current}{self.postfix}"
        width = len(sp)
        left = self.length // 2 - width // 2
        sys.stdout.write("\b" * (self.length + 1))
        for i in range(self.length):
            if i >= left and i < left + width:
                sys.stdout.write(sp[i - left])
            else:
                sys.stdout.write("=")
        sys.stdout.write("]")
        sys.stdout.write('\n')
        sys.stdout.flush()