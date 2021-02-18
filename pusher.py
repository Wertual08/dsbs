import os
import shutil
from pathlib import Path
from utils import RemoveEmptyDirectories



class Pusher:
    def __init__(self, path):
        self.ReportProgress = callable(None)
        self.path = path

    def Push(self, dest):
        total_files = 0
        for _, _, files in os.walk(self.path):
            total_files += len(files)
            
        for _, _, files in os.walk(dest):
            total_files += len(files)

        current_files = 0
        for path, _, files in os.walk(self.path):
            rel_pref = os.path.relpath(path, self.path)

            for name in files:
                rel_path = os.path.join(rel_pref, name)
                src_path = os.path.join(self.path, rel_path)
                dst_path = os.path.join(dest, rel_path)

                sstamp = os.path.getmtime(src_path)
                dstamp = -1
                if os.path.isfile(dst_path):
                    dstamp = os.path.getmtime(dst_path)
                    
                if sstamp != dstamp:
                    if os.path.isfile(dst_path):
                        os.remove(dst_path)
                    if os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    
                    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)
                    
                if self.ReportProgress:
                    self.ReportProgress(current_files / total_files, total_files)
                current_files += 1

        for path, _, files in os.walk(dest):
            rel_pref = os.path.relpath(path, dest)

            for name in files:
                rel_path = os.path.join(rel_pref, name)
                src_path = os.path.join(dest, rel_path)
                dst_path = os.path.join(self.path, rel_path)

                if not os.path.isfile(dst_path):
                    os.remove(src_path)

                if self.ReportProgress:
                    self.ReportProgress(current_files / total_files, total_files)
                current_files += 1
        
        RemoveEmptyDirectories(dest)