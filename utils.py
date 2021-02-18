import os



def RemoveEmptyDirectories(path, removeRoot=True):
    if not os.path.isdir(path):
        return
    files = os.listdir(path)
    if len(files):
        for f in files:
            fullpath = os.path.join(path, f)
            if os.path.isdir(fullpath):
                RemoveEmptyDirectories(fullpath)

    files = os.listdir(path)
    if len(files) == 0 and removeRoot:
        os.rmdir(path)