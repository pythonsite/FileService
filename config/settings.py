# db config
db_config = {
    "host": "127.0.0.1",
    "port": 3306,
    "db": "record",
    "user": "root",
    "password": "123456",
    "charset": 'utf8',
    "minsize": 1,
    "maxsize": 10
}

# master file path
master_file_path = "/app/master"

# temp file path
temp_file_path = "/tmp/FileService"

# detail file path
detail_file_path = "/app/detail"

# log config
log_config = {
    "file_path": "/app/log/file_service.log",
    "size": 10,
    "backup": 50
}

# push url
push_url = "http://127.0.0.1:8080/push"





