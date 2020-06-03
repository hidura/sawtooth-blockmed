# This class loads the header of the page and the decorator inside
# Also loads the main information as the groups of modules the user
# Have access.
import json
from functools import wraps

import requests
from flask import (request, session)
from markupsafe import Markup

from DataBase.Base import db
from DataBase.Profile import Profile
from DataBase.User import User

userDetails = Profile


def header(func):
    @wraps(func)
    def func_wrapper():
        if not db.session.is_active:
            db.session.bind.dispose()
        id = session["_user_id"]
        userDetails.id = id

        getUserInfo = db.session.query(User.first_name, User.last_name,
                                       User.idcard, User.email).\
            filter(User.id == id).first()

        userDetails.name = getUserInfo[0]
        userDetails.lastname = getUserInfo[1]
        userDetails.idcard = getUserInfo[2]
        userDetails.username = getUserInfo[3]
        headers = {'Content-Type': 'application/json', 'idcard': userDetails.idcard}
        response_load = requests.get('http://localhost:8041/api/patients',
                                     headers=headers)
        if response_load.status_code != 200:
            raise Exception("There was a problem communicating with the validator.")
        elif response_load.status_code == 200:
            response = json.loads(response_load.content.decode())
            dataResp = response['data'][0]
            userDetails.avatar = dataResp['photo']


        return func()
    return func_wrapper

