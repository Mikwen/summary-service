import os
import sys
import time

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import Bot

summary_file_suffix = '_summary.pdf'

summary_tool = Bot.SummaryTool()

class NewSummaryCreator(FileSystemEventHandler):
    def on_created(self, event):
        create_summary_if_appropriate(event.src_path)

def get_summary_filename(file_path):
    # strip ".pdf" and add suffix
    return file_path[:-4] + summary_file_suffix

def is_summary_file(filename):
    return filename.endswith(summary_file_suffix)

def summary_exists(file_path):
    return os.path.isfile(get_summary_filename(file_path))

def create_summary_if_appropriate(file_path):
    if (not summary_exists(file_path)) and (not is_summary_file(file_path)):
        summary_filename = get_summary_filename(file_path)
        try:
            summary_tool.summaryRun(file_path, summary_filename);
        except Exception as ex:
            print(ex)

def update_all(root_dir):
    for root, subdirs, files in os.walk(root_dir):
        for filename in files:
            file_path = os.path.join(root, filename)
            create_summary_if_appropriate(file_path)

def main():
    root_dir = os.path.abspath(sys.argv[1])
    update_all(root_dir)
    observer = Observer()
    event_handler = NewSummaryCreator()
    observer.schedule(event_handler, path=root_dir, recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == '__main__':
    main()
