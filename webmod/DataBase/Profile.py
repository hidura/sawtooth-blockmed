import datetime


class Profile():
    """The profile object define a profile user"""
    def __init__(self):
        self.username = None
        self.name = None
        self.lastname=None
        self.avatar = None
        self.id = None
        self.idcard = None
        self.widgets = None
        self.modules = None
        self.notifications = None
        self.messages = None
        self.modules_group = None
        self.time = str(datetime.datetime.now())