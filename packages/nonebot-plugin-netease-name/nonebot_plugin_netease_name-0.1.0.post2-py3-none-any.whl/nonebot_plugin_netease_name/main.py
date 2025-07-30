"""
Netease Minecraft Nickname Random by wangyupu
使用来自网易的词典
全部使用built-in库
可自定义
"""

import hashlib
import json
import os
import random
import time
from pathlib import Path

from nonebot_plugin_localstore import get_plugin_config_dir

NAME_STRU_DICT = {
    "内建1": "前缀+人名+动词",
    "内建2": "前缀+人物+动词",
    "内建3": "前缀+人物+动词",
    "内建4": "前缀+形容+人名",
    "内建5": "前缀+动词+人物",
    "内建6": "前缀+动词+人名",
    "内建7": "人名+#的+前缀+物品",
}
application_start_time = time.time()
config_dir = get_plugin_config_dir()
# 获取目录
path = Path(__file__).parent

# 处理db
dbfs = os.listdir(path / "db")
dbs = {}
f2s = {}
try:
    dbfs.remove(".DS_Store")
    dbfs.remove("字到音")
except:  # noqa: E722
    pass

# 写入变量
for filename in dbfs:
    with open(path / "db" / filename) as file:
        dbs[filename] = file.read().split("\n")

with open(path / "db" / "字到音") as file:
    lines = file.read().split("\n")
    for item in lines:
        lineitems = item.split(",")
        f2s[lineitems[0]] = lineitems[1]
if (
    not (config_dir / "name_strus.json").is_file()
    or not (config_dir / "name_strus.json").exists()
):
    with open(config_dir/"name_strus.json", "w") as f:
        json.dump(NAME_STRU_DICT, f, indent=4)
else:
    with open(config_dir/"name_strus.json") as file:
        name_stru: dict[str, str] = json.load(file)

name_stru_keys = list(name_stru.keys())


# 主
def init_random():
    seed = (hashlib.sha512(str(time.time()).encode()).hexdigest())[:8]
    seed = int(seed, 16)
    random.seed(seed)


def get_random_nickname():
    nickname_type = random.choice(name_stru_keys)
    nick = ""
    parts = []

    thisnickname_stru = (name_stru[nickname_type]).split("+")
    for item in thisnickname_stru:
        if str(item)[0] == "#":
            thispart = item[1:]
        else:
            thispart = random.choice(dbs[item])
        parts.append(thispart)
        nick = nick + thispart

    return nick
