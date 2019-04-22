import aiomysql
import logging
import traceback


class DataBase(object):
    def __init__(self, pool):
        self.pool = pool

    async def get(self, sql, args=None):
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(sql, args)
                    value = await cur.fetchone()
                    return value
        except Exception as e:
            exe = traceback.format_exc()
            logging.error(exe)
            return e

    async def query(self, sql, args=None):
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    await cur.execute(sql, args)
                    value = await cur.fetchall()
                    return value
        except Exception as e:
            exe = traceback.format_exc()
            logging.error(exe)
            return e

    async def insert(self, sql, args=None):
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    ret = await cur.execute(sql, args)
                    if ret > 0:
                        return cur.lastrowid
                    return -1
        except Exception as e:
            exe = traceback.format_exc()
            logging.error(exe)
            return e.args

    async def execute(self, sql, args=None):
        try:
            async with self.pool.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cur:
                    ret = await cur.execute(sql, args)
                    return ret
        except Exception as e:
            exe = traceback.format_exc()
            logging.error(exe)
            return e
