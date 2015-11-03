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

    def hit_cache(self, key):
        try:
            self.seek(0)
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
                        if k == key:
                            return v
                else:
                    return None
        except Exception, e:
            print e
            return None

    def wipe_cache_by_projectid(self, project_id):
        try:
            #import pydevd
            #pydevd.settrace("localhost", port=12345, stderrToServer=True, stdoutToServer=True)

            file_object = open('/var/log/patron/cache.log', 'a+')
            file_object.write('>>>enter wipe_cache_by_projectid\n')
            self.seek(0)
            d = dict()
            while True:
                curIndex = self.tell()
                index = self.find("$", self.tell())
                if index != -1:
                    length = index + 1 - self.tell()
                    head = self.read(length)
                    contentlength = head[:-1]
                    length += int(contentlength)
                    content = self.read(int(contentlength))
                    #ignore "\n" as END symbol
                    self.read(1)
                    #clear memory
                    self.seek(curIndex)
                    self.write('\0' * (length+1))
                    # well, actually, it is a Dict
                    obj = dict(json.loads(content))
                    for (k, v) in obj.items():
                        r = k.split(':')
                        file_object.write('r[0]=%s:%r' % (r[0], r[0]!=project_id))
                        if r[0] != project_id:
                            d[k] = v
                else:
                    file_object.close()
                    return d
        except Exception, e:
            print e
            file_object.close()
            return None

    def getMemory(self):
        self.seek(0)
        index = self.rfind("\n")
        if index != -1:
            memory = self.read(index + 1)
            file_object = open('/var/log/patron/cache.log', 'a+')
            file_object.write('\n\n!!!!This is patron_cache:getMemory:\n')
            file_object.write(memory)
            file_object.close()
            return memory

    def clearMemory(self):
        self.seek(0, 2)
        length = self.tell()
        self.seek(0)
        self.write('\0' * length)
        return

global mm
mm = ObjectMmap(-1, 1024*1024, 1, access=mmap.ACCESS_WRITE)

class PatronCache(object):

    @classmethod
    def save_to_cache(self, op, subject_sid, object_sid, res):
        p = {subject_sid + "**" + op + "**" + object_sid: res}
        mm.jsonwrite(p)

    @classmethod
    def get_from_cache(self, op, subject_sid, object_sid):
        return mm.hit_cache(subject_sid + "**" + op + "**" + object_sid)
        # cache = mm.jsonread()
        # if cache:
        #     try:
        #         res = cache[op + "**" + subject_sid + "**" + object_sid]
        #     except KeyError:
        #         return None
        #     return res
        # else:
        #     return None

    @classmethod
    def wipecache(self, project_id):
        cache = mm.wipe_cache_by_projectid(project_id)
        if cache:
            mm.jsonwrite(cache)

    #uesd for test
    @classmethod
    def get_memory(self):
        return mm.getMemory()

