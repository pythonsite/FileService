# 用于模拟生成master文件和detail文件脚本
import time
import json
import datetime
import uuid
import shutil

start = time.time()
for i in range(1):
    master_file_name = str(uuid.uuid1())
    msg_uuid = str(uuid.uuid1())
    firstid = str(uuid.uuid1())
    secondid = str(uuid.uuid1())
    now_time = datetime.datetime.now()
    n_time = now_time.strftime('%Y-%m-%d %H:%M:%S')
    n_date = now_time.strftime('%Y-%m-%d')
    master_data = {
        "msg_uuid": msg_uuid,
        "server":"my_server",
        "firstid": firstid,
        "secondid": secondid,
        "msg_data": "hello world"
    }
    with open("/Users/zhaofan/vs_python/master/" + master_file_name + '.master', 'w') as f:
        f.write(json.dumps(master_data))
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    end_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cdr_first_data = {
        "msg_uuid": msg_uuid,
        "mem_id": firstid,
        "stime": start_time,
        "etime": end_time,
    }
    with open("/Users/zhaofan/vs_python/detail/" + firstid + ".json", "w") as f:
        f.write(json.dumps(cdr_first_data))
    cdr_second_data = {
        "msg_uuid": msg_uuid,
        "mem_id": secondid,
        "stime": start_time,
        "etime": end_time,
    }
    with open("/Users/zhaofan/vs_python/detail/" + secondid + ".json","w") as f:
        f.write(json.dumps(cdr_second_data))
    time.sleep(0.002)

end = time.time()
print('now is %s' % datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f"))
print("total time %s" % (end - start))
