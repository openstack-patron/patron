#Add by Yang Luo

#modified by Wu Luo: add class ObjectMmap & PatronCache

"""
provide cache mechanism for patron_verify.

"""

import mmap
import json


class ObjectMmap(mmap.mmap):

    def __init__(self, fileno, length, tagname=None, access=None, offset=None):
        super(ObjectMmap, self).__init__(fileno, length, tagname=tagname, access=access, offset=offset)

    def jsonwrite(self, obj):
        try:
            self.seek(0)
            # seek to SEEK_END
            index = self.rfind("\n")
            if index != -1:
                self.seek(index + 1)

            print self.tell()
            obj_str = json.dumps(obj)
            obj_len = len(obj_str)
            # "  " just for fun. HaHa
            content = str(obj_len) + "$" + obj_str + "\n"
            self.write(content)
            return True
        except Exception, e:
            return False

    def jsonread(self):
        try:
            self.seek(0)
            d = dict()
            while True:
                index = self.find("$", self.tell())
                if index != -1:
                    head = self.read(index + 1 - self.tell())
                    contentlength = head[:-1]
                    content = self.read(int(contentlength))
                    #ignore "\n" as END symbol
                    self.read(1)
                    # well, actually, it is a Dict
                    obj = dict(json.loads(content))
                    for (k, v) in obj.items():
                        d[k] = v
                else:
                    return d
        except Exception, e:
            print e
            return None

    def getMemory(self):
        self.seek(0)
        index = self.rfind("\n")
        if index != -1:
            memory = self.read(index + 1)
            # file_object = open('/var/log/nova/mylog.txt', 'a+')
            # file_object.write('\n\n!!!!This is patron_cache:getMemory:\n')
            # file_object.write(memory)
            # file_object.close()
            return memory

global mm
mm = ObjectMmap(-1, 1024*1024, 1, access=mmap.ACCESS_WRITE)

class PatronCache(object):

    @classmethod
    def save_to_cache(self, op, subject_sid, object_sid, res):
        p = {op + "**" + subject_sid + "**" + object_sid: res}
        mm.jsonwrite(p)

    @classmethod
    def get_from_cache(self, op, subject_sid, object_sid):
        cache = mm.jsonread()
        if cache:
            try:
                res = cache[op + "**" + subject_sid + "**" + object_sid]
            except KeyError:
                return None
            return res
        else:
            return None

    #uesd for test
    @classmethod
    def get_memory(self):
        return mm.getMemory()

