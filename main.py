from worker import Worker
from pusher import Pusher
from progressbar import ProgressBar
import getpass
import os


PROGRESS_LENGTH = 40



def ShowHelp():
    print("Help for dsbs:")
    print("help                display user instruction.")
    print("index               run indexer on the directory.")
    print("    -i <path>       (optional) specify root directory.")
    print("    -m <comment>    (optional) specify comment.")
    print("log                 display indexation history.")
    print("status              display file statuses.")
    print("    -i <path>       (optional) specify root directory.")
    print("    -w <width>      (optional) set entry column width.")
    print("    -t              (optional) show time stamps.")
    print("merge <paths...>    merge directories.")
    print("    -f              (optional) merge without indexing.")
    print("push <paths...>     make directories identical to source.")
    print("    -s              set source directory.")
    print("version             display the version.")
    print("clean <paths...>    clean indexations.")

def ParseArgs(argv):
    args = {}
    ind = 0
    cur = None
    for arg in argv:
        if arg.startswith("-"):
            cur = arg
            args[arg] = ""
        else:
            if cur == None:
                args[ind] = arg
                ind += 1
            else:
                args[cur] = arg
            cur = None
    return args

def Index(args):
    directory = args["-i"] if "-i" in args.keys() else "."
    user = getpass.getuser()
    message = args["-m"] if "-m" in args.keys() else None

    progressbar = ProgressBar(PROGRESS_LENGTH, "", True)
    progressbar.Start(f"Indexing \"{directory}\": ")

    worker = Worker(directory)
    worker.ReportProgress = progressbar.ReportProgress
    worker.Index(user, message)
    worker.Dispose()

    progressbar.Finish()

def Log(args):
    directory = args["-i"] if "-i" in args.keys() else "."

    worker = Worker(directory)
    for row in worker.Log():
        print(f"[{row[0][0:19]}]{row[1]}: {row[2]}")
    worker.Dispose()

def Status(args):
    directory = args["-i"] if "-i" in args.keys() else "."
    width = int(args["-w"]) if "-w" in args.keys() else 80

    show_created = "-t" in args.keys()
    show_changed = "-t" in args.keys()
    
    worker = Worker(directory)
    print(f"|status |entry{' ' * (width - 5)}|", end='')
    if show_created:
        print(f"created            |", end='')
    if show_changed:
        print(f"changed            |", end='')
    print()
    print(f"+-------+{'-' * width}+", end='')
    if show_created:
        print(f"-------------------+", end='')
    if show_changed:
        print(f"-------------------+", end='')
    print()
    for row in worker.Status():
        print(f"|{Worker.StatusToStr(row[4])}|", end='')
        print(f"{row[0][0:width]:{width}}|", end='')
        if show_created:
            print(f"{row[1][0:19]}|", end='')
        if show_changed:
            print(f"{row[2][0:19]}|", end='')
        print()
    worker.Dispose()

def Merge(args):
    workers = []
    ind = 0
    while args.get(ind) != None:
        workers.append(Worker(args.get(ind))) 
        ind += 1
    
    user = getpass.getuser()

    if not "-f" in args.keys():
        for worker in workers:
            progressbar = ProgressBar(PROGRESS_LENGTH, "", True)
            progressbar.Start(f"Indexing \"{worker.directory_path}\": ")
            worker.ReportProgress = progressbar.ReportProgress
            worker.Index(user, "Merge indexation.")
            progressbar.Finish()
            

    origin = workers.pop(0)
    for worker in workers:
        progressbar = ProgressBar(PROGRESS_LENGTH, "", True)
        progressbar.Start(f"Merging into \"{origin.directory_path}\": ")
        origin.ReportProgress = progressbar.ReportProgress
        origin.Merge(worker)
        progressbar.Finish()

    for worker in workers:
        progressbar = ProgressBar(PROGRESS_LENGTH, "", True)
        progressbar.Start(f"Merging into \"{worker.directory_path}\": ")
        worker.ReportProgress = progressbar.ReportProgress
        worker.Merge(origin)
        progressbar.Finish()

    origin.Dispose()
    for worker in workers:
        worker.Dispose()

def Push(args):
    directories = []
    ind = 0
    while args.get(ind) != None:
        directories.append(args[ind]) 
        ind += 1

    source = args.get("-s")
    if source:
        pusher = Pusher(source)
        for d in directories:
            progressbar = ProgressBar(PROGRESS_LENGTH, "", True)
            progressbar.Start(f"Pushing into \"{d}\": ")
            pusher.ReportProgress = progressbar.ReportProgress
            pusher.Push(d)
            progressbar.Finish()

    else:
        print("Push error: Source directory was not specified.")

def Clean(args):
    ind = 0
    while args.get(ind) != None:
        path = os.path.join(args[ind], "dsbs_data.db").replace("\\", "/")
        if os.path.isfile(path):
            os.remove(path)
        ind += 1
        print(f"Indexation cleaned \"{path}\".")