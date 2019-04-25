import os
import traceback
import logging
import asyncio
import json
import aiofiles
from asyncio import CancelledError
from asyncio import TimeoutError
import aiohttp
import time
import datetime
from aiofiles import os as aio_os

from config.settings import detail_file_path
from config.settings import push_url


class FileRead(object):

    def __init__(self, loop, db, push_url):
        self.loop = loop
        self.db = db
        self.push_url = push_url
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
                    "file_name": file_name,
                    "msg_uuid": content.get("msg_uuid"),
                    "mem_id": content.get("mem_id"),
                    "start_time": content.get("stime"),
                    "end_time": content.get("end_time")
                }
                return True, detail_content
        except Exception as e:
            await self.remove_file(file_name, "detail")
            return False, None

    async def push_and_db(self, data, flag):
        try:
            if data:
               async with aiohttp.ClientSession() as session:
                   async with session.post(self.push_url, data=data) as resp:
                        text = await resp.json()
                        if text.get('code') != 200:
                            return False
                        return True

        except asyncio.TimeoutError:
            exc = traceback.format_exc()
            logging.error(exc)
        except Exception as e:
            exc = traceback.format_exc()
            logging.error(exc)

    async def insert_db(self, args, flag):
        sql_args = None
        if flag == 'first'or flag == 'second':
            sql_args = [args.get("msg_uuid"), args.get(
                "mem_id"), args.get("start_time"), args.get("end_time")]
            sql = "insert into FileService.detail (msg_uuid, memid, stime, etime) values (%s,%s,%s,%s)"
        elif flag == "master":
            sql_args = [args.get("msg_uuid"), args.get(
                 "server"), args.get("client"), args.get("msg_data")]
            sql = "insert into FileService.master (msg_uuid, server, client, etmsg_dataime) values (%s,%s,%s,%s)"
        logging.info("msg_uuid [%s] start insert into [%s] sql is [%s] sql_args [%s]", args.get("msg_uuid"), flag, sql, sql_args)
        ret = await self.db.insert(sql, sql_args)
        if not ret:
            logging.error("msg_uuid [%s] insert db [%s] fail" % (
                args.get("msg_uuid"), flag))
            return False
        logging.info("msg_uuid [%s] insert db success")
        return True

    async def push_data(self, data, flag):
        msg_uuid = data.get("msg_uuid", None)
        logging.info("msg_uuid [%s] flag [%s] start push to server [%s]" %(msg_uuid, flag, self.push_url))
        start_time = time.time()
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.push_url, data=data, timeout=3) as resp:
                    text = await resp.json()
                    end_time = time.time()
                    logging.info(
                        "msg_uuid [%s] flag [%s] push data to url [%s] response data [%s]" % (msg_uuid, flag, self.push_url, text))
                    if text.get("code") != 200:
                        logging.error("msg_uuid [%s] push  data to url [%s] response error" %(msg_uuid, self.push_url))
                        return False
                    return True
        except asyncio.TimeoutError:
            exc = traceback.format_exc()
            logging.error("msg_uuid [%s] push data to url [%s] timeout" %(msg_uuid, self.push_url))
            return False
        except Exception as e:
            exc = traceback.format_exc()
            logging.info(exc)
            return False


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
                    "file_name": file_name,
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
