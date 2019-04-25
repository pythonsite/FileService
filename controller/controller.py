import os
import logging
import datetime
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
        self.queues = ""
        self.count = 1

    def scan_file(self, file_path):

        if not os.path.exists(temp_file_path):
            os.makedirs(temp_file_path)
        
        while True:
            try:
                if not file_path:
                    logging.warning("file path [%s] is empty" %file_path)
                    continue
                files =self.load_filename(file_path)
                for file in files:
                    src_file = os.path.join(file_path, file)
                    dst_file = os.path.join(temp_file_path, file)
                    if os.path.exists(dst_file):
                        continue
                    self.move_file(src_file, dst_file)
                    if os.path.exists(dst_file):
                        pass
            except Exception as e:
                pass

    
    def load_filename(self, file_path):
        dir_list = os.listdir(file_path)
        if not dir_list:
            return list()
        return dir_list

    def move_file(self, src_file, dst_file):
        try:
            command = 'mv %s %s' % (src_file, dst_file)
            return os.system(command)
        except Exception as e:
            logging.error(e)

    
