import os
import traceback
import logging
import asyncio
import json
import aiofiles
from asyncio import CancelledError
import aiohttp
import time
import datetime
from aiofiles import os as aio_os

from config.settings import detail_file_path


class FileRead(object):

    def __init__(self, loop, db):
        self.loop = loop
        self.db = db
        self.first_name = None
        self.second_name = None

    async def execute(self, file_name):
        try:
            logging.info("start handle master file [%s]", file_name)
            self.flag, first_detail_name, second_detail_name = await self.get_master_file_content(file_name)
            if not self.flag:
                self.master_content = {}
                current_task = asyncio.Task.current_task(
                    loop=self.loop).cancel()
                current_task.cancel()
            if first_detail_name:
                self.flag2, self.first_detail_content = await self.get_detail_file_content(first_detail_name)
                if not self.flag2:
                    self.first_detail_content = {}
            else:
                self.first_detail_content = {}

            if second_detail_name:
                self.flag3, self.second_detail_content = await self.get_detail_file_content(second_detail_name)
                if self.flag3:
                    self.second_detail_content = {}
            else:
                self.second_detail_content = {}

        except CancelledError as e:
            logging.info("cancel task success")
        except Exception as e:
            logging.error(e)

    async def get_detail_file_content(self, file_name):
        try:
            async with aiofiles.open(file_name, mode='r') as f:
                file_size = os.path.getsize('%s' % file_name)
                if not file_size:
                    return False
                _content = await f.read()
                content = json.loads(_content)
                detail_content = {
                    "msg_uuid": content.get("msg_uuid"),
                    "mem_id": content.get("mem_id"),
                    "start_time": content.get("stime"),
                    "end_time": content.get("end_time")
                }
                return True, detail_content
        except Exception as e:
            await self.remove_file(file_name, "detail")
            return False, None

    async def push_and_db(self):
        pass

    async def get_master_file_content(self, file_name):
        try:
            async with aiofiles.open(file_name, mode="r") as f:
                file_size = os.path.getsize("%s" % file_name)
                if not file_size:
                    logging.warning("master file [%s] is empty")
                    return False, None, None
                content = await f.read()
                master_data = json.loads(content)
                msg_uuid = master_data.get("msg_uuid", None)
                if master_data.get("firstid", None):
                    self.first_name = detail_file_path + \
                        "/" + master_data["firstid"] + ".json"
                if master_data.get("secondid", None):
                    self.second_name = detail_file_path + \
                        "/" + master_data["secondid"] + ".json"

                self.master_content = {
                    "msg_uuid": master_data.get("msg_uuid"),
                    "server": master_data.get("server"),
                    "client": master_data.get("client"),
                    "msg_data": master_data.get("msg_data")
                }
                return True, self.first_name, self.second_name
        except Exception as e:
            logging.info("handle master file [%s] error", file_name)
            await self.remove_file(file_name, "master")
            return False, None, None

    async def remove_file(self, file, tag):
        try:
            if os.path.exists("%s" % file):
                await aio_os.remove(file)
        except Exception as e:
            pass
