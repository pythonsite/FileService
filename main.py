import os
import logging
import uuid
import time
import traceback

from multiprocessing import cpu_count
from multiprocessing import Process
from multiprocessing import Queue

from config.settings import master_file_path
from config.settings import temp_file_path


SUBPROCESS_THRESHOLD = max(1, cpu_count())

class Controller(object):

    def __init__(self):
        self.temp_file_path = temp_file_path
        self.master_file_path = master_file_path
        self.queues = list()
        self.count = 1

    def scan_file(self, file_path):
        if not os.path.exists(temp_file_path):
            os.makedirs(temp_file_path)
        while True:
            try:
                if not file_path:
                    logging.warning("file_path [%s] is empty", file_path)
                    continue
                files = self.load_filename(file_path)
                logging.info("file_path have [%s] files" % len(files))
                for file in files:
                    src_file = os.path.join(file_path, file)
                    dst_file = os.path.join(temp_file_path, file)
                    self.move_file(src_file, dst_file)
                    if os.path.exists(dst_file):
                        # 这部分的处理是为了让处理进入不同的进程，并进行轮询
                        if self.count % len(self.queues) == 0:
                            process_queue = self.queues[self.count-1]
                            self.count = 1
                        else:
                            process_queue = self.queues[self.count-1]
                            self.count += 1
                        process_queue.put(dst_file)
                    else:
                        logging.error("move file error")
            except Exception as e:
                exc = traceback.format_exc()
                logging.error('error %s', exc)

    def load_filename(self, filepath):
        dir_list = os.listdir(filepath)
        if not dir_list:
            return list()
        return dir_list

    def move_file(self, src_file, dst_file):
        try:
            command = 'mv %s %s' % (src_file, dst_file)
            return os.system(command)
        except Exception as e:
            logging.error(e)

    def start(self):
        logging.info("FileService is start")
        self.queues = [Queue() for i in range(SUBPROCESS_THRESHOLD)]
        for queue in self.queues:
            pass

        self.scan_file(self.master_file_path)
