#_*_coding:utf-8_*_

import os
import re
import json
from luatable import fromlua

import sys
reload(sys)
sys.setdefaultencoding('utf8')

def convert(root, filename, out_dir):
    name, ext = os.path.splitext(filename)
    if ext != ".lua":
        return

    lua_file = os.path.join(root, filename)
    with open(lua_file, "r") as fp:
        content = fp.read()

    # remove Table =
    content = re.sub("Table\s*=\s*.*{", "{", content, re.I|re.M|re.S)

    try:
        # there are ??? chars, fix me!!!
        json_datas = fromlua(content[3:])
    except Exception, e:
        print e
        return

    json_str = json.dumps(json_datas, sort_keys=True, indent=4)
    json_file = os.path.join(out_dir, name + ".json")
    with open(json_file, "w") as fp:
        fp.write(json_str.decode("unicode-escape"))

    print "convert file [%s]    OK" % filename


if __name__ == "__main__":
    src_dir = "/Users/tarmylan/p4_mac/fight_depot/client/Assets/LuaFramework/Lua/Game/Table/excel"
    dst_dir = "./datas"

    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)

    for root, _, files in os.walk(src_dir):
        for f in files:
            convert(root, f, dst_dir)
