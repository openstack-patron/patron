#Add by Yang Luo

#modified by Wu Luo: add a class ObjectMmap

"""
provide cache mechanism for patron_verify.

"""

import mmap
import json


class ObjectMmap(mmap.mmap):

    def __init__(self, fileno, length, tagname=None, access=None, offset=None):
        super(ObjectMmap, self).__init__(fileno, length, tagname=tagname, access=access, offset=offset)
        self.length = length
        self.access = access
        self.tagname = tagname

    def jsonwrite(self, obj):
        try:
            self.obj = obj
            self.seek(0)
            obj_str = json.dumps(obj)
            obj_len = len(obj_str)
            content = str(obj_len) + ":" + obj_str
            self.write(content)
            self.contentbegin = len(str(obj_len)) + 1
            self.contentend = self.tell()
            self.contentlength = self.contentend - self.contentbegin
            return True
        except Exception, e:
            return False

    def jsonread_master(self):
        try:
            self.seek(self.contentbegin)
            content = self.read(self.contentlength)
            obj = json.loads(content)
            self.obj = obj
            return obj
        except Exception, e:
            if self.obj:
                return self.obj
            else:
                return None

    def jsonread_follower(self):
        try:
            self.seek(0)
            index = self.find(":")
            if index != -1:
                head = self.read(index + 1)
                contentlength = int(head[:-1])
                content = self.read(contentlength)
                obj = json.loads(content)
                self.obj = obj
                return obj
            else:
                return None
        except Exception, e:
            if self.obj:
                return self.obj
            else:
                return None

global mm
mm = ObjectMmap(-1, 1024*1024, 1, access=mmap.ACCESS_WRITE)

class PatronCache(object):

    def save_to_cache(self, op, subject_sid, object_sid, res):
        #cls.cache[op + "**" + subject_sid + "**" + object_sid] = res
        #mm = ObjectMmap(-1, 1024*1024, access=mmap.ACCESS_WRITE, tagname='share_mmap')
        p = {op + "**" + subject_sid + "**" + object_sid: res}
        mm.jsonwrite(p)
        print mm.jsonread_master()

    def get_from_cache(self, op, subject_sid, object_sid):
        #mm = ObjectMmap(-1, 1024*1024, access=mmap.ACCESS_READ, tagname='share_mmap')
        cache = mm.jsonread_follower()
        if cache:
            try:
                res = cache[op + "**" + subject_sid + "**" + object_sid]
            except KeyError:
                return None
            return res
        else:
            return None

#patronCache = PatronCache()
#patronCache.save_to_cache('op', 'subject_sid', 'object_sid', 'result')
#print patronCache.get_from_cache('op', 'subject_sid', 'object_sid')
