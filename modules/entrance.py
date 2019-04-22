import os
import traceback
import logging
import asyncio
import aiomysql
import threading


from database.database import DataBase
from conf


class HandlerCenter(object):

    def __init__(self, master_queue):
        self.master_queue = master_queue
        self.loop = ""
        self.db = ""

    def execute(self):

        try:
            while True:
                message = self.master_queue.get()

        except Exception as e:
            exec = traceback.format_exc()
            logging.error(exec)

    async def handle_message(self, message):
        pass

    async def app_factory(self):
        pool = await aiomysql.create_pool(host=CDR_DB_CONFIG["host"], port=int(CDR_DB_CONFIG["port"]), user=CDR_DB_CONFIG["user"], password=CDR_DB_CONFIG["password"], db=CDR_DB_CONFIG["db"], minsize=int(CDR_DB_CONFIG["minsize"]), maxsize=int(CDR_DB_CONFIG["maxsize"]), loop=self.loop, autocommit=True, pool_recycle=1)
        self.db = Database(pool)

    def start_coroutine(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.create_task(self.app_factory())
        self.loop.run_forever()

    @classmethod
    def run(cls, master_queue):
        handler_center = cls(master_queue)
        
        # 启动协程
        coroutine_thread = threading.Thread(
            target=handler_center.start_coroutine)
        coroutine_thread.start()

        handler_center.execute()
        

