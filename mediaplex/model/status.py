class Status(object):
    def __init__(self, code, text, shorthand, flag=None):
        self.code = code
        self.text = text
        self.shorthand = shorthand
        self.flag = flag

    def __unicode__(self):
        return self.text
