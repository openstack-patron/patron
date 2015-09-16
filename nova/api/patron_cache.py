#Add by Yang Luo

"""
provide cache mechanism for patron_verify.

"""

class PatronCache(object):
    cache = dict()

    @classmethod
    def save_to_cache(cls, op, subject_sid, object_sid, res):
        cls.cache[op + "**" + subject_sid + "**" + object_sid] = res

    @classmethod
    def get_from_cache(cls, op, subject_sid, object_sid):
        try:
            res = cls.cache[op + "**" + subject_sid + "**" + object_sid]
        except KeyError:
            return None
        return res
