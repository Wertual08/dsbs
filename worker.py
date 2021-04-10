import sqlite3
from datetime import datetime
import time
import os
import shutil
from pathlib import Path
from utils import RemoveEmptyDirectories



class Worker:
    STATUS_CREATED = 0
    STATUS_CHANGED = 1
    STATUS_DELETED = 2
    STATUS_EXISTED = 3
    STATUS_IGNORED = 4

    @staticmethod
    def StatusToStr(s):
        if s == Worker.STATUS_CREATED:
            return "created"
        elif s == Worker.STATUS_CHANGED:
            return "changed"
        elif s == Worker.STATUS_DELETED:
            return "deleted"
        elif s == Worker.STATUS_EXISTED:
            return "existed"
        elif s == Worker.STATUS_IGNORED:
            return "ignored"
        else:
            return "unknown"

    def __init__(self, path : str):
        Path(path).mkdir(parents=True, exist_ok=True)
        self.ReportProgress = lambda *args: None
        self.ignore = ["dsbs_data.db", "dsbs_data.db-journal"]
        self.directory_path = path
        self.database_path = os.path.join(path, "dsbs_data.db")
        self.connection = sqlite3.connect(self.database_path)
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS indexations (
                date         TEXT PRIMARY KEY,
                user         TEXT,
                message      TEXT
            );'''
        )
        self.connection.execute('''
            CREATE TABLE IF NOT EXISTS entries (
                path         TEXT PRIMARY KEY,
                date_created TEXT,
                date_changed TEXT,
                date_indexed TEXT,
                status       INTEGER,
                FOREIGN KEY (date_indexed)
                    REFERENCES indexations(date)
            );'''
        )

    def RegisterIndexation(self, dt, usr, msg):
        self.connection.execute("INSERT OR IGNORE INTO indexations VALUES (?, ?, ?);",
            (dt, usr, msg)
        )

    def UpdateFile(self, dt, path):
        full_path = os.path.join(self.directory_path, path)
        date_changed = datetime.fromtimestamp(os.path.getmtime(full_path))
        self.connection.execute(f'''
            INSERT INTO entries 
            VALUES(?, ?, ?, ?, {self.STATUS_CREATED})
            ON CONFLICT(path) DO UPDATE SET
            date_indexed = ?,
            status = CASE WHEN status != {self.STATUS_IGNORED} THEN 
                CASE WHEN date_changed < ? THEN 
                    CASE WHEN status == {self.STATUS_DELETED} THEN {self.STATUS_CREATED}
                    ELSE {self.STATUS_CHANGED} END
                ELSE {self.STATUS_EXISTED} END
            ELSE status END,
            date_changed = ?;''',
            (path,
            datetime.fromtimestamp(os.path.getctime(full_path)),
            date_changed,
            dt,
            dt,
            date_changed,
            date_changed
            )
        )

    def Truncate(self, dt):
        self.connection.execute(f'''
            UPDATE entries 
            SET 
            status = {self.STATUS_DELETED},
            date_indexed = ?,
            date_changed = ?
            WHERE date_indexed != ? AND status != {self.STATUS_DELETED};''',
            (dt, dt, dt)
        )

    def Index(self, usr : str, msg : str):
        total_files = 0
        for _, _, files in os.walk(self.directory_path):
            total_files += len(files)

        dt = datetime.now()
        self.RegisterIndexation(dt, usr, msg)

        current_files = 0
        for path, _, files in os.walk(self.directory_path):
            if path == self.directory_path:
                path = ""
            else:
                path = os.path.relpath(path, self.directory_path)

            for name in files:
                if self.ignore.count(name) == 0:
                    entry = os.path.join(path, name).replace("\\", "/")
                    self.UpdateFile(dt, entry)
                    
                if self.ReportProgress:
                    self.ReportProgress(current_files / total_files, total_files)
                current_files += 1

        self.Truncate(dt)

    def Merge(self, worker):
        merged_in = []
        total_files = worker.connection.execute("SELECT COUNT (status) FROM entries;").fetchone()[0]
        current_files = 0

        for srow in worker.connection.execute("SELECT * FROM indexations;"):
            self.RegisterIndexation(srow[0], srow[1], srow[2])

        for srow in worker.connection.execute("SELECT * FROM entries;"):
            mrow = None
            for m in self.connection.execute("SELECT * FROM entries WHERE path == ?;", (srow[0],)):
                mrow = m

            if not mrow or mrow[2] < srow[2]:    
                src_path = os.path.join(worker.directory_path, srow[0])
                dst_path = os.path.join(self.directory_path, srow[0])

                if srow[4] == self.STATUS_IGNORED:
                    pass
                elif srow[4] == self.STATUS_DELETED:
                    if os.path.isfile(dst_path):
                        os.remove(dst_path)
                    if os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                else:
                    if os.path.isfile(dst_path):
                        os.remove(dst_path)
                    if os.path.isdir(dst_path):
                        shutil.rmtree(dst_path)
                    
                    Path(dst_path).parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src_path, dst_path)

                self.connection.execute("INSERT OR REPLACE INTO entries VALUES(?, ?, ?, ?, ?);", srow)
                merged_in.append(srow)
            
            self.ReportProgress(current_files / total_files, total_files)
            current_files += 1

        RemoveEmptyDirectories(self.directory_path)

        return merged_in

    def Log(self):
        return self.connection.execute("SELECT * FROM indexations;")

    def Status(self):
        return self.connection.execute("SELECT * FROM entries;")

    def Dispose(self):
        if self.connection:
            self.connection.commit()
            self.connection.close()