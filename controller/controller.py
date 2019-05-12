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
from modules.entrance import HandlerCenter
from modules.filemonitor import FileMonitor
from watchdog.observers import Observer


SUBPROCESS_THRESHOLD = max(1, cpu_count())


class Controller(object):

    def __init__(self):
        self.queues = ""
        self.count = 1
        self.event_handler = FileMonitor(self.scan_file2)

    def scan_file(self, file_path):

        if not os.path.exists(temp_file_path):
            os.makedirs(temp_file_path)
        
        while True:
            try:
                if not file_path:
                    logging.warning("file path [%s] is empty" %file_path)
                    continue
                files =self.load_filename(file_path)
                logging.info("now the path have %s files" % len(files))
                for file in files:
                    src_file = os.path.join(file_path, file)
                    dst_file = os.path.join(temp_file_path, file)
                    if os.path.exists(dst_file):
                        continue
                    self.move_file(src_file, dst_file)
                    if os.path.exists(dst_file):
                        process_queue = self.get_process_queue()
                        process_queue.put(dst_file)
                    else:
                        logging.error("move file error")
                time.sleep(0.1)                    
            except Exception as e:
                exc = traceback.format_exc()
                logging.error("error %s" %exc)
    
    def scan_file2(self, new_create_file):
        try:
            logging.info("new create file [%s]" %new_create_file)
            file = new_create_file.split("/")[-1]
            dst_file = os.path.join(temp_file_path, file)
            self.move_file(new_create_file, dst_file)
            process_queue = self.get_process_queue()
            process_queue.put(dst_file)
        except Exception as e:
            exc = traceback.format_exc()
            logging.error("error %s" %exc)  

    def get_process_queue(self):
        logging.info("start choice process queue")
        if self.count % len(self.queues) == 0:
            process_queue = self.queues[self.count - 1]
            self.count = 1
        else:
            process_queue = self.queues[self.count -1]
            self.count += 1
        return process_queue
    
    def load_filename(self, file_path):
        dir_list = os.listdir(file_path)
        if not dir_list:
            return list()
        return dir_list[:500]

    def move_file(self, src_file, dst_file):
        try:
            command = 'mv %s %s' % (src_file, dst_file)
            return os.system(command)
        except Exception as e:
            logging.error(e)

    def start(self):
        logging.info("start file service")
        self.queues = [Queue() for i in range(SUBPROCESS_THRESHOLD)]
        for queue in self.queues:
            ps = Process(target=HandlerCenter.run, args=(queue,))
            ps.start()
        observer = Observer()
        observer.schedule(self.event_handler, master_file_path, recursive=True)
        observer.start()
        observer.join()
        # self.scan_file(master_file_path)
    

    
