import os
import argparse
import importlib
import time
import threading
import datetime

from core.app import App


class FileChangeHandler:
    def __init__(self, app: App, module_name, view_name):
        self.app = app
        self.module_name = module_name
        self.view_name = view_name

    def dispatch(self, event):
        current_time = datetime.datetime.now().time()
        print(f'[{current_time}] Reloading...')
        module = importlib.import_module(self.module_name)
        view_class = getattr(module, self.view_name)
        self.app.root_view = view_class()
        # self.app.draw()


class FileWatcher(threading.Thread):
    def __init__(self, filename: str, handler: FileChangeHandler):
        super().__init__()
        self.filename = filename
        self.last_modified = os.stat(self.filename).st_mtime
        self.handler = handler
        self.stop = False

    def run(self):
        while not self.stop:
            last_modified = os.stat(self.filename).st_mtime
            if last_modified > self.last_modified:
                self.last_modified = last_modified
                self.handler.dispatch(last_modified)
            time.sleep(1)


def launch_preview(module_name, view_name):
    module = importlib.import_module(module_name)
    view_class = getattr(module, view_name)

    app = App(view_class(), window_title=f'{view_name} Live Preview')

    file_change_handler = FileChangeHandler(app, module_name, view_name)

    file_watcher = FileWatcher(module.__file__, file_change_handler)
    file_watcher.start()
    print(f'Watching updates on {module.__file__}')

    app.execute()
    file_watcher.stop = True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Skooter Live Preview')
    parser.add_argument('module')
    parser.add_argument('view')
    arguments: argparse.Namespace = parser.parse_args()
    launch_preview(arguments.module, arguments.view)
