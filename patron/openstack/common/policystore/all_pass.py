
# Edited by Yang Luo.
# This is the simplest example for an Enforcer.
class AllPassEnforcer(object):

    def __init__(self):
        self.loaded = False

    def clear(self):
        self.loaded = False

    def is_loaded(self):
        return self.loaded

    def set_policy(self, data, default_rule, overwrite=True, use_conf=True):
        self.loaded = True

    def enforce(self, rule, target, creds):
        return True