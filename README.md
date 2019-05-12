# FileService说明

FileService 用于处理特定的系统文件。
1. 【系统】会生成【master】文件和【detail】文件
2. 一个【master】文件对应两个【detail】文件，并具有唯一的msg_uuid
3. 【master】和【detail】的文件内容都是json格式字符串
4. 【master】文件中会包含两个detail文件的文件名
5. FileService解析master文件和detail文件，并将内容master内容插入master表，detail的内容插入detail表中

一个master文件和对应两个detail文件的例子：

```
{
    "msg_uuid": "958e6550-74d0-11e9-b89f-784f436cfaf3",
    "server": "my_server",
    "firstid": "958e65dc-74d0-11e9-b89f-784f436cfaf3",
    "secondid": "958e6636-74d0-11e9-b89f-784f436cfaf3",
    "msg_data": "hello world"
}
```


```
{
    "msg_uuid": "958e6550-74d0-11e9-b89f-784f436cfaf3",
    "mem_id": "958e65dc-74d0-11e9-b89f-784f436cfaf3",
    "stime": "2019-05-13 00:11:22",
    "etime": "2019-05-13 00:11:22"
}
```


```
{
    "msg_uuid": "958e6550-74d0-11e9-b89f-784f436cfaf3",
    "mem_id": "958e6636-74d0-11e9-b89f-784f436cfaf3",
    "stime": "2019-05-13 00:11:22",
    "etime": "2019-05-13 00:11:22"
}
```

上面的例子我们可以看出，在master文件中，有一个firstid和secondid，这个其实对应的就是两个detail文件的文件名。

master表和detail的创建sql语句如下：


```
CREATE TABLE `detail` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `msg_uuid` varchar(45) NOT NULL,
  `mem_id` varchar(45) NOT NULL,
  `stime` datetime NOT NULL,
  `etime` datetime NOT NULL,
  `crdate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```

```
CREATE TABLE `master` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `msg_uuid` varchar(45) NOT NULL,
  `server` varchar(16) NOT NULL,
  `msg_data` varchar(45) NOT NULL,
  `crdate` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```







