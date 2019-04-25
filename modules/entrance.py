import os
import traceback
import logging
import asyncio
import aiomysql
import threading


from database.database import DataBase
from config.settings import db_config


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
        pool = await aiomysql.create_pool(host=db_config["host"], port=int(db_config["port"]), user=db_config["user"], password=db_config["password"], db=db_config["db"], minsize=int(db_config["minsize"]), maxsize=int(db_config["maxsize"]), loop=self.loop, autocommit=True, pool_recycle=1)
        self.db = DataBase(pool)

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
        

