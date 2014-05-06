import json

keys = ['email', 'password', 'smsKey', 'forwardingNumber', 'phoneType']


class Config(object):
    """
    ``ConfigParser`` subclass that looks into your home folder for a file named
    ``.gvoice`` and parses configuration data from it.
    """
    def __init__(self):
        try:
            with open('config', 'r') as f:
                self.fname = json.loads(f.read())['gvoice']
        except:
            with open('../../config', 'r') as f:
                self.fname = json.loads(f.read())['gvoice']

    def get(self, option):
        try:
            return self.fname.get(option, None)
        except NoOptionError:
            return

    phoneType = property(lambda self: self.get('phoneType'))
    forwardingNumber = property(lambda self: self.get('forwardingNumber'))
    email = property(lambda self: self.get('email'))
    password = property(lambda self: self.get('password'))
    smsKey = property(lambda self: self.get('smsKey'))
    secret = property(lambda self: self.get('secret'))

config = Config()
