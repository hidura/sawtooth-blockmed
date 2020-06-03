import hashlib
import json

import flask_login
import requests

from passlib.hash import sha256_crypt as crypt

from DataBase.Base import db
from DataBase.User import User


class UserInfo(flask_login.UserMixin):
    # proxy for a database of users
    def __init__(self, id):
        self.authenticated = False
        self.username = None
        self.name = None
        self.lastname = None
        self.avatar = None
        self.idcard = None
        self.id=None
        # This means that login with the system.
        getUserInfo = db.session.query(User.idcard, User.email). \
            filter(User.id == int(id)).first()
        if getUserInfo != None:
            self.authenticated = True
            self.idcard = getUserInfo[0]
            self.username = getUserInfo[1]
            headers = {'Content-Type': 'application/json', 'idcard':self.idcard}
            response_load = requests.get('http://localhost:8041/api/patients',
                                          headers=headers)
            if response_load.status_code != 200:
                raise Exception("There was a problem communicating with the validator.")
            elif response_load.status_code == 200:
                response=json.loads(response_load.content.decode())
                dataResp=response['data'][0]
                self.name=dataResp['name']
                self.lastname=dataResp['lastname']
                self.avatar=dataResp['photo']
        self.id = id


    @classmethod
    def get(cls, id):
        return cls

    def getUsername(self):
        return self.username

    def getName(self):
        return self.name

    def is_authenticated(self):
        return self.authenticated

    def is_active(self):
        return self.authenticated

    def get_id(self):
        return self.id

    def get_idcard(self):
        return self.idcard

class UserLogin(flask_login.UserMixin):

    def __init__(self, inputs):

        # This means that login with the system.
        getUserInfo = db.session.query(User). \
            filter(User.email == inputs["email"]).first()
        if getUserInfo != None:
            if crypt.verify(inputs["passwd"], getUserInfo.passwd):
                self.user_info = UserInfo(getUserInfo.id)
                self.user_info.id = getUserInfo.id
            else:
                self.user_info = None
        else:
            self.user_info = None
