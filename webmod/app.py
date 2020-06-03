import sys
import os
from datetime import timedelta

import flask_login
from markupsafe import Markup
from pip._vendor import requests

from general import RequestProc, general

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import datetime
import json
# from datetime import timedelta
#
# import flask_login
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_login import login_required

from DataBase.Base import db

from sqlalchemy import func
app = Flask(__name__)
from flask_login import LoginManager
import random

app.secret_key = "SuperSecret"


login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = 'login'
UPLOAD_FOLDER = os.path.dirname(os.path.abspath(__file__))+'/static/'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

with open("params.json") as f:
    config = json.loads(f.read())
    app.secret_key = config["secret_key"]
    app.config["SQLALCHEMY_DATABASE_URI"] = config["postgres"]
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # This is by default don't touch it.
    app.config["MAIL_SERVER"] = config["mail"]["host"]
    app.config["MAIL_PORT"] = int(config["mail"]["port"])
    app.config["MAIL_USE_SSL"] = True
    app.config["MAIL_USERNAME"] = config["mail"]["username"]
    app.config["mail"] = config["mail"]["mail"]
    app.config["MAIL_PASSWORD"] = config["mail"]["password"]



with app.app_context():
    db.init_app(app)
    from UserLogin import UserLogin, UserInfo
    from Header import header, userDetails
    from DataBase.User import User


application = app

@login_manager.user_loader
def load_user(user_id):
    return UserInfo.get(user_id)

@app.route('/login', methods=['POST', 'GET'])
## Login onto the system
def login():
    if request.method=='GET':
        return render_template('login.html',basic={"title":"Login"})
    elif request.method=='POST':
        userlogin = UserLogin(request.form).user_info

        remember = False
        duration = timedelta(days=0.0)
        if 'rememberme' in request.form:
            if request.form['rememberme'] == 'on':
                remember = True
                duration = timedelta(days=6.0)
        if userlogin != None:
            flask_login.login_user(userlogin, remember=remember)

            return redirect(url_for('index'))

@app.route('/register', methods=['POST', 'GET'])
## Register of people
def register():

    if request.method=='GET':
        return render_template('register.html',basic={"title":"User register"})
    elif request.method=='POST':
        data = RequestProc(request).dataPckg

        dataCollection={User.email.name:data[User.email.name],
                 User.idcard.name:data[User.idcard.name],
                 User.last_name.name:data[User.last_name.name],
                 User.first_name.name:data[User.first_name.name],
                 User.user_type.name:int(data[User.user_type.name]),
                 User.passwd.name:general().gen_hash(data[User.passwd.name]),
                 User.idcard_type.name:int(data[User.idcard_type.name])}

        dataCol=User.insert(dataCollection)
        headers = {'Content-Type': 'application/json'}
        if int(data[User.user_type.name]) == 2:
            path='http://localhost:8041/api/patients'
        elif int(data[User.user_type.name]) == 1:
            path='http://localhost:8041/api/doctors'
        else:
            path = 'http://localhost:8041/api/patients'
        response_load = requests.post(path,
                                      data=json.dumps(dataCollection),
                                      headers=headers)
        if response_load.status_code != 200:
            raise Exception("There was a problem communicating with the validator.")
        elif response_load.status_code == 200:
            resp_data =json.loads(response_load.content.decode())
            if resp_data["status"]=='DONE':
                return redirect(url_for('login'))

@app.route('/')
@app.route('/index')
@login_required
@header
def index():
    if '_user_id' in session:
        if "messages" in request.args:
            flash(request.args['messages'])

        headers = {'Content-Type': 'application/json',
                   'idcard_viewer':userDetails.idcard,
                   'idcard_patient':userDetails.idcard}
        path = 'http://localhost:8041/api/evaluations'
        response_load = requests.get(path,
                                      headers=headers)

        if response_load.status_code != 200:
            raise Exception("There was a problem communicating with the validator.")
        elif response_load.status_code == 200:
            feed=""
            feeds_color=['feed-item-secondary','feed-item-success',
                         'feed-item-info','feed-item-warning',
                         'feed-item-danger']
            data =json.loads(response_load.content.decode())['data']
            for evaluation in data[0]['evaluations']:
                random.shuffle(feeds_color)
                feed+="""<li class="feed-item {}">
                <time class="date" datetime="9-25">{}</time>
                <span class="text"><a href="#">"{}"</a></span>
                <span class="text">{}</span>
            </li>""".format(feeds_color[0], general().julian2date(evaluation['date_time']),
                            evaluation['diagnosis'],evaluation['doctor_name'])
            return render_template('index.html', basic={"title": ""},
                               user_details=userDetails,
                               feed=Markup(feed))




    return render_template('login.html', basic={"title": ""})

@app.route('/grant_consent', methods=['POST'])
@login_required
## Register of people
def grant_consent():

    if request.method=='POST':
        data = RequestProc(request).dataPckg
        headers = {'Content-Type': 'application/json'}
        path = 'http://localhost:8041/api/consents'
        response_load = requests.post(path,
                                      data=json.dumps(data),
                                      headers=headers)

        if response_load.status_code != 200:
            raise Exception("There was a problem communicating with the validator.")
        elif response_load.status_code == 200:
            dataResp=json.loads(response_load.content.decode())
            if dataResp['status']=='ERROR':
                return redirect(url_for('index', messages="ERROR: Something go wrong"))
            elif dataResp['status']=='DONE':
                return redirect(url_for('index', messages="Success: The system is working correctly"))








if __name__ == '__main__':
    app.run(debug=True)
